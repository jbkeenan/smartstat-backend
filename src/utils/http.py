from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def build_session(total_retries: int = 3, backoff: float = 0.5, status_forcelist=None) -> Session:
    status_forcelist = status_forcelist or [429, 500, 502, 503, 504]
    retry = Retry(
        total=total_retries,
        read=total_retries,
        connect=total_retries,
        backoff_factor=backoff,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(["GET","POST","PUT","PATCH","DELETE"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s = Session()
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s
