import time
import requests
from utils.exceptions import ApiRequestError

def send_api_request(
    method: str,
    url: str,
    data: dict | None = None,
    params: dict | None = None,
    max_retries: int = 10,
    retry_delay: int = 2,
    headers = {"Content-Type": "application/json"},
    timeout: int = 60,
):
    method = method.upper()

    for attempt in range(1, max_retries + 1):
        response = requests.request(
            method=method,
            url=url,
            json=data,
            params=params,
            headers=headers,
            timeout=timeout,
        )

        # Úspěch
        if response.status_code < 400:
            # někdy API nevrací JSON (204)
            if response.content:
                return response.json()
            return None

        # Rate limit
        if response.status_code == 429:
            if attempt == max_retries:
                raise ApiRequestError("429 Too Many Requests – max retries reached")

            time.sleep(retry_delay)
            continue

        # Ostatní chyby
        raise ApiRequestError(
            f"{method} {url} failed ({response.status_code}): {response.text}"
        )

    raise ApiRequestError("Unexpected error")
