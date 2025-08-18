import os
from datetime import datetime
from typing import Optional

from src.integrations.errors import VendorError
from src.integrations.nethome_cloud import NetHomeClient
from src.models.vendor_account import VendorAccount, db


def f_to_c(f: float) -> float:
    return round((float(f) - 32.0) * 5.0 / 9.0, 1)


def c_to_f(c: float) -> float:
    return round((float(c) * 9.0 / 5.0) + 32.0, 1)


class PioneerAPI:
    """
    Cloud adapter for Pioneer units that use NetHome/Midea cloud.
    Expects the thermostat_model.device_id to be the Midea applianceId.
    """

    def __init__(self, thermostat_model):
        self.thermostat = thermostat_model
        # Find the NetHome account (this could be filtered by user in multi-user setups)
        acct = VendorAccount.query.filter_by(vendor="nethome").first()
        if not acct or not acct.access_token:
            raise VendorError("nethome", "no NetHome account connected", status=400)
        self.acct = acct
        self.client = NetHomeClient()
        # Temperature unit expected by the API. Default to Celsius.
        self.temp_unit = os.getenv("NETHOME_TEMP_UNIT", "C").upper()

    def _ensure_fresh_token(self):
        if self.acct.token_expires_at and self.acct.token_expires_at <= datetime.utcnow():
            # Refresh tokens
            access, refresh, expires_in = self.client.refresh(self.acct.refresh_token)
            self.acct.set_tokens(access, refresh, expires_in)
            db.session.commit()

    def _status_raw(self) -> dict:
        self._ensure_fresh_token()
        return self.client.status(self.acct.access_token, self.thermostat.device_id)

    def get_status(self):
        js = self._status_raw()
        data = js.get("data") or js
        ambient = (
            data.get("tempIndoor")
            or data.get("indoorTemp")
            or data.get("currentTemperature")
            or data.get("temperature")
        )
        setpt = (
            data.get("setTemperature")
            or data.get("targetTemperature")
            or data.get("setpoint")
        )
        mode = (data.get("mode") or data.get("workMode") or "").lower()

        def maybe_f(x):
            if x is None:
                return None
            try:
                xv = float(x)
                if self.temp_unit == "C":
                    # assume values <=45C are Celsius, convert to Fahrenheit for UI
                    if xv <= 45:
                        return c_to_f(xv)
                    else:
                        return xv
                else:
                    # Already Fahrenheit
                    return xv
            except Exception:
                return x

        return {
            "online": True,
            "current_temperature": maybe_f(ambient),
            "target_temperature": maybe_f(setpt),
            "mode": mode,
            "raw": js,
        }

    def set_temperature(self, temperature: float, is_cooling: bool = True):
        self._ensure_fresh_token()
        value = f_to_c(temperature) if self.temp_unit == "C" else float(temperature)
        self.client.command(
            self.acct.access_token,
            self.thermostat.device_id,
            "temperature",
            value,
        )
        return True

    def turn_on(self):
        self._ensure_fresh_token()
        self.client.command(
            self.acct.access_token,
            self.thermostat.device_id,
            "power",
            "on",
        )
        return True

    def turn_off(self):
        self._ensure_fresh_token()
        self.client.command(
            self.acct.access_token,
            self.thermostat.device_id,
            "power",
            "off",
        )
        return True

    def set_mode(self, mode: str):
        """Set the HVAC mode: e.g., cool, heat, auto, fan, dry, etc."""
        self._ensure_fresh_token()
        self.client.command(
            self.acct.access_token,
            self.thermostat.device_id,
            "mode",
            mode.lower(),
        )
        return True
