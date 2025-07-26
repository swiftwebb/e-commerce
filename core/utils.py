# core/utils.py
import requests
from django.conf import settings

def verify_payment(ref, amount):
    url = f"https://api.paystack.co/transaction/verify/{ref}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        res_data = response.json()
        if res_data['data']['amount'] == int(amount * 100) and res_data['data']['status'] == 'success':
            return True
    return False



def verify_payment(ref, amount=None):
    url = f"https://api.paystack.co/transaction/verify/{ref}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        result = response.json()


        if result.get("status") is not True:
            return False

        # Only compare amount if passed
        if amount:
            paid_amount = result["data"]["amount"]
            return result["data"]["status"] == "success" and int(amount * 100) == int(paid_amount)

        return result["data"]["status"] == "success"

    except (requests.exceptions.RequestException, KeyError) as e:
        return False
