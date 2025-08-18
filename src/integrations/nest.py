import os
import time
import logging
import requests
from typing import Dict, Any
from src.utils.http import build_session
from src.integrations.errors import VendorError
from src.models.vendor_account import VendorAccount

log = logging.getLogger(__name__)
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
SDM_BASE = "https://smartdevicemanagement.googleapis.com/v1"

class NestAuth:
    def __init__(self, client_id: str, client_secret: str, refresh_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self._access = None
        self._exp = 0
        self.s = build_session()

    def access_token(self) -> str:
        now = time.time()
        if self._access and now < self._exp - 30:
            return self._access
        r = self.s.post(GOOGLE_TOKEN_URL, data={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token"
        }, timeout=15)
        if r.status_code >= 400:
            raise VendorError("nest", f"token refresh failed: {r.text}", status=401)
        js = r.json()
        self._access = js["access_token"]
        self._exp = now + int(js.get("expires_in", 3600))
        return self._access

class NestClient:
    def __init__(self, project_id: str, auth: NestAuth):
        self.project_id = project_id
        self.auth = auth
        self.s = build_session()

    def _h(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.auth.access_token()}"}

    def name(self, dev_id: str) -> str:
        return f"enterprises/{self.project_id}/devices/{dev_id}"

    def get_device(self, dev_id: str) -> Dict[str, Any]:
        r = self.s.get(f"{SDM_BASE}/{self.name(dev_id)}", headers=self._h(), timeout=15)
        if r.status_code >= 400:
            raise VendorError("nest", f"HTTP {r.status_code}: {r.text}")
        return r.json()

    def exec(self, dev_id: str, command: str, params: Dict[str, Any]):
        r = self.s.post(f"{SDM_BASE}/{self.name(dev_id)}:executeCommand", headers=self._h(), json={"command": command, "params": params}, timeout=15)
        if r.status_code >= 400:
            raise VendorError("nest", f"HTTP {r.status_code}: {r.text}")
        return r.json()

class NestAPI:
    def __init__(self, thermostat_model):
        acct = VendorAccount.query.filter_by(vendor="nest").first()
        if not acct:
            raise VendorError("nest", "no Nest account configured", status=400)
        ex = acct.get_extra()
        auth = NestAuth(
            client_id=ex.get("client_id"),
            client_secret=ex.get("client_secret"),
            refresh_token=acct.refresh_token
        )
        self.client = NestClient(project_id=ex.get("project_id"), auth=auth)
        self.thermostat = thermostat_model

    @staticmethod
    def f_to_c(f: float) -> float:
        return round((float(f) - 32.0) * 5.0 / 9.0, 2)

    @staticmethod
    def c_to_f(c: float) -> float:
        return round((float(c) * 9.0 / 5.0) + 32.0, 1)

    def get_status(self):
        data = self.client.get_device(self.thermostat.device_id)
        traits = data.get("traits", {})
        ambient_c = traits.get("sdm.devices.traits.Temperature", {}).get("ambientTemperatureCelsius")
        tset = traits.get("sdm.devices.traits.ThermostatTemperatureSetpoint", {})
        mode = traits.get("sdm.devices.traits.ThermostatMode", {}).get("mode", "OFF")
        target_c = tset.get("coolCelsius") if mode == "COOL" else tset.get("heatCelsius")
        return {
            "online": True,
            "current_temperature": self.c_to_f(ambient_c) if ambient_c is not None else None,
            "target_temperature": self.c_to_f(target_c) if target_c is not None else None,
            "mode": mode.lower(),
            "raw": data
        }

    def set_temperature(self, temperature: float, is_cooling: bool = True):
        c = self.f_to_c(temperature)
        if is_cooling:
            self.client.exec(self.thermostat.device_id, "sdm.devices.commands.ThermostatTemperatureSetpoint.SetCool", {"coolCelsius": c})
        else:
            self.client.exec(self.thermostat.device_id, "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat", {"heatCelsius": c})
        return True

    def turn_on(self):
        self.client.exec(self.thermostat.device_id, "sdm.devices.commands.ThermostatMode.SetMode", {"mode": "HEAT"})
        return True

    def turn_off(self):
        self.client.exec(self.thermostat.device_id, "sdm.devices.commands.ThermostatMode.SetMode", {"mode": "OFF"})
        return True
