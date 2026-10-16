import os
import datetime as dt
import requests

BASE_URL = os.environ.get("VSELLM_BASE_URL", "https://litellm.data-light.ru")
API_KEY = os.environ.get("VSELLM_API_KEY", "APIKEY")  # замените или задайте через env

def _url(path: str) -> str:
    # гарантируем /v1 в пути
    return f"{BASE_URL.rstrip('/')}/v1{path}"

def _headers() -> dict:
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

def get_models():
    r = requests.get(_url("/models"), headers=_headers(), timeout=20)
    r.raise_for_status()
    return r.json()

def get_subscription():
    # Может не поддерживаться прокси
    r = requests.get(_url("/dashboard/billing/subscription"), headers=_headers(), timeout=20)
    if r.status_code >= 400:
        return {"error": f"{r.status_code}", "body": safe_text(r)}
    return r.json()

def get_credit_grants():
    # Может не поддерживаться прокси
    r = requests.get(_url("/dashboard/billing/credit_grants"), headers=_headers(), timeout=20)
    if r.status_code >= 400:
        return {"error": f"{r.status_code}", "body": safe_text(r)}
    return r.json()

def get_usage(start_date: str, end_date: str):
    # Формат дат: YYYY-MM-DD
    params = {"start_date": start_date, "end_date": end_date}
    r = requests.get(_url("/usage"), headers=_headers(), params=params, timeout=30)
    if r.status_code >= 400:
        return {"error": f"{r.status_code}", "body": safe_text(r)}
    return r.json()

def safe_text(resp: requests.Response) -> str:
    try:
        return resp.text
    except Exception:
        return "<non-text response>"

if __name__ == "__main__":
    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
        raise SystemExit("Set VSELLM_API_KEY or put your key in the code")

    # 1) Проверка ключа: список моделей
    try:
        models = get_models()
        print("Models:", models)
    except requests.HTTPError as e:
        print("GET /v1/models failed:", e.response.status_code, safe_text(e.response))
        raise
    except requests.RequestException as e:
        print("Network error:", e)
        raise

    # 2) Попытка получить подписку/кредиты (если поддерживается)
    sub = get_subscription()
    print("Subscription:", sub)

    credits = get_credit_grants()
    print("Credit grants:", credits)

    # 3) Расходы за период (например, за последние 7 дней)
    end = dt.date.today()
    start = end - dt.timedelta(days=7)
    usage = get_usage(start.isoformat(), end.isoformat())
    print(f"Usage {start}..{end}:", usage)