import requests

class ApiClient:
    def __init__(self, api_url):
        self.api_url = api_url

    def get_response(self, query_text):
        payload = {"query_text": query_text}
        try:
            resp = requests.post(self.api_url, json=payload)
            resp.raise_for_status()
            # Change 'response' to 'result' below
            return resp.json().get("result", "[No result found]")
        except Exception as e:
            return f"[API error: {e}]"
