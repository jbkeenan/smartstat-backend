import os
import logging
import requests
from typing import Dict, Any
from src.utils.http import build_session
from src.integrations.errors import VendorError
from src.models.vendor_account import VendorAccount, db

log = logging.getLogger(__name__)

class CieloClient:
    def __init__(self, base_url: str, auth_token: str, x_api_key: str):
        self.base_url = (base_url or "https://home.cielowigle.com/web").rstrip("/")
        self.s = build_session()
        self.s.headers.update({
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
            "auth_token": auth_token,
            "x-api-key": x_api_key
        })

    def _handle(self, r: requests.Response):
        if r.status_code >= 400:
            msg = r.text
            try:
                msg = r.json().get("message", msg)
            except Exception:
                pass
            raise VendorError("cielo", f"HTTP {r.status_code}: {msg}")
        return r.json()

    def list_devices(self):
        return self._handle(self.s.get(f"{self.base_url}/devices", params={"limit": 200}, timeout=15))

    def command(self, device_id: str, payload: Dict[str, Any]):
        body = {"deviceid": device_id, **payload}
        return self._handle(self.s.post(f"{self.base_url}/commands", json=body, timeout=15))


class CieloAPI:
    """Adapter used by thermostat routes."""
    def __init__(self, thermostat_model):
        self.thermostat = thermostat_model
        acct = VendorAccount.query.filter_by(vendor="cielo").first()
        if not acct:
            raise VendorError("cielo", "no Cielo account configured", status=400)
        ex = acct.get_extra()
        self.client = CieloClient(
            base_url=ex.get("base_url"),
            auth_token=acct.access_token,
            x_api_key=ex.get("x_api_key", "")
        )

    def get_status(self):
        devs = self.client.list_devices().get("data") or []
        d = next((d for d in devs if str(d.get("id")) == str(self.thermostat.device_id) or d.get("deviceid") == self.thermostat.device_id), None)
        if not d:
            return {"online": False}
        return {
            "online": True,
            "current_temperature": d.get("currentTemp") or d.get("ambientTemp"),
            "target_temperature": d.get("setPoint"),
            "mode": (d.get("mode") or "").lower(),
            "fan": (d.get("fan") or "auto").lower(),
            "raw": d
        }

    def set_temperature(self, temperature: float, is_cooling: bool = True):
        self.client.command(self.thermostat.device_id, {"command": "setTemp", "params": {"temp": float(temperature)}})
        return True

    def turn_on(self):
        self.client.command(self.thermostat.device_id, {"command": "power", "params": {"value": "on"}})
        return True

    def turn_off(self):
        self.client.command(self.thermostat.device_id, {"command": "power", "params": {"value": "off"}})
        return True
