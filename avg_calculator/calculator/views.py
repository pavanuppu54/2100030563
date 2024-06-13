import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

# Constants
WINDOW_SIZE = 10
window = []

# URLs for the test server endpoints
AUTH_URL = 'http://20.244.56.144/test/auth'
TEST_SERVER_URLS = {
    'p': 'http://20.244.56.144/test/primes',
    'f': 'http://20.244.56.144/test/fibo',
    'e': 'http://20.244.56.144/test/even',
    'r': 'http://20.244.56.144/test/rand',
}

AUTH_PAYLOAD = {
    "companyName": "KL University",
    "clientID": "18fa805a-cbd2-4f64-bc72-6977f98548fa",
    "clientSecret": "nvkcOntPlUkJSGbU",
    "ownerName": "Uppu Jyothi Naga Pavan",
    "ownerEmail": "pavanuppu2002@gmail.com",
    "rollNo": "2100030563"
}

REQUEST_TIMEOUT = 5  
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def fetch_token():
    try:
        logger.debug("Requesting new token from auth server.")
        response = requests.post(AUTH_URL, json=AUTH_PAYLOAD, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        access_token = data.get('access_token')
        if access_token:
            logger.debug("Access token successfully retrieved.")
            return access_token
        else:
            logger.error("Failed to retrieve access token: No access_token in response.")
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred while fetching token: {http_err}")
    except requests.RequestException as req_err:
        logger.error(f"Request exception occurred while fetching token: {req_err}")
    return None


def fetch_numbers(numberid):
    url = TEST_SERVER_URLS.get(numberid)
    if not url:
        logger.error(f"Invalid number ID: {numberid}")
        return None

    token = fetch_token()
    if not token:
        logger.error("Failed to fetch token.")
        return None

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        logger.debug(f"Requesting numbers from {url}.")
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        numbers = data.get('numbers', [])
        logger.debug(f"Numbers successfully retrieved: {numbers}")
        return numbers
    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred while fetching numbers: {http_err}")
    except requests.RequestException as req_err:
        logger.error(f"Request exception occurred while fetching numbers: {req_err}")
    return None

class NumberAPIView(APIView):

    def get(self, request, numberid, format=None):
        global window

        if numberid not in TEST_SERVER_URLS:
            return Response({"error": "Invalid number ID"}, status=status.HTTP_400_BAD_REQUEST)

        new_numbers = fetch_numbers(numberid)
        if new_numbers is None:
            return Response({"error": "Failed to fetch numbers from the test server"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        window_prev_state = list(window)

        for number in new_numbers:
            if number not in window:
                if len(window) >= WINDOW_SIZE:
                    window.pop(0)
                window.append(number)

        avg = sum(window) / len(window) if window else 0

        response_data = {
            "numbers": new_numbers,
            "windowPrevState": window_prev_state,
            "windowCurrState": window,
            "avg": round(avg, 2)
        }
        return Response(response_data, status=status.HTTP_200_OK)