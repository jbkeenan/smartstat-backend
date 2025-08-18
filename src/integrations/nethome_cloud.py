import os
import requests
from typing import Dict, Any, Tuple
from src.utils.http import build_session
from src.integrations.errors import VendorError

DEFAULT_BASE = os.getenv("NETHOME_BASE_URL", "https://mapp.appsmb.com")
APP_ID = os.getenv("NETHOME_APP_ID", "1117")
CLIENT_TYPE = os.getenv("NETHOME_CLIENT_TYPE", "1")
LANG = os.getenv("NETHOME_LANG", "en_US")

class NetHomeClient:
    def __init__(self, base: str = DEFAULT_BASE):
        self.base = base.rstrip("/")
        self.s = build_session()

    def login(self, email: str, password: str, region: str | None) -> Tuple[str, str, int]:
        r = self.s.post(f"{self.base}/v1/user/login", json={
            "appId": APP_ID,
            "clientType": CLIENT_TYPE,
            "format": 2,
            "language": LANG,
            "loginAccount": email,
            "password": password
        }, timeout=20)
        if r.status_code >= 400:
            raise VendorError("nethome", f"login failed: {r.text}", status=401)
        js = r.json().get("data", {})
        access = js.get("accessToken") or js.get("token")
        refresh = js.get("refreshToken")
        expires = int(js.get("expiresIn") or 3600)
        if not access:
            raise VendorError("nethome", f"missing token: {r.text}")
        return access, refresh, expires

    def refresh(self, refresh_token: str) -> Tuple[str, str, int]:
        r = self.s.post(f"{self.base}/v1/user/refreshToken", json={
            "appId": APP_ID,
            "format": 2,
            "refreshToken": refresh_token
        }, timeout=20)
        if r.status_code >= 400:
            raise VendorError("nethome", f"refresh failed: {r.text}", status=401)
        js = r.json().get("data", {})
        return js.get("accessToken"), js.get("refreshToken", refresh_token), int(js.get("expiresIn") or 3600)

    def list_devices(self, access_token: str) -> Dict[str, Any]:
        r = self.s.get(f"{self.base}/v1/appliance/user/listGet", headers={"authorization": access_token}, timeout=20)
        if r.status_code >= 400:
            raise VendorError("nethome", f"devices failed: {r.text}")
        return r.json()

    def status(self, access_token: str, appliance_id: str) -> dict:
        r = self.s.get(
            f"{self.base}/v1/appliance/operation/status",
            headers={"authorization": access_token},
            params={"applianceId": appliance_id},
            timeout=20
        )
        if r.status_code >= 400:
            raise VendorError("nethome", f"status failed: {r.text}")
        return r.json()

    def command(self, access_token: str, appliance_id: str, command: str, value) -> dict:
        body = {
            "applianceId": appliance_id,
            "command": command,
            "value": value
        }
        r = self.s.post(
            f"{self.base}/v1/appliance/operation/set",
            headers={"authorization": access_token},
            json=body,
            timeout=20
        )
        if r.status_code >= 400:
            raise VendorError("nethome", f"command failed: {r.text}")
        return r.json()
