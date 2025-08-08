import requests

class ApiClient:
    def __init__(self, api_url):
        self.api_url = api_url

    def get_response(self, query_text):
        payload = {"query_text": query_text}
        try:
            resp = requests.post(self.api_url, json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"result": f"[API error: {e}]", "metadata": None}
