"""Server-side HTTP client. No weights or artifact tokens in the frontend."""
from urllib.parse import urlparse
import httpx

class InferenceClient:
    def __init__(self, url='', token='', proxy_key='', proxy_secret=''):
        self.url, self.token = url.rstrip('/'), token
        self.proxy_key, self.proxy_secret = proxy_key, proxy_secret
        if self.url:
            p = urlparse(self.url)
            if p.username or p.password or p.query or p.fragment:
                raise ValueError('Backend URL must not contain credentials or query parameters')
            if p.scheme != 'https' and not (p.scheme == 'http' and p.hostname in ('127.0.0.1', 'localhost')):
                raise ValueError('Backend requires HTTPS')

    def call(self, path, payload=None):
        if not self.url or not self.token:
            return {'error': {'code': 'not_configured', 'message': 'Live inference is temporarily unavailable.'}}
        try:
            with httpx.Client(timeout=httpx.Timeout(240, connect=10), follow_redirects=False, trust_env=False) as client:
                response = client.request('GET' if payload is None else 'POST', self.url + path,
                    headers={'Authorization': 'Bearer ' + self.token, **({'Modal-Key': self.proxy_key, 'Modal-Secret': self.proxy_secret} if self.proxy_key and self.proxy_secret else {})}, json=payload)
            if response.status_code != 200:
                code = {401: 'unauthorized', 429: 'quota_or_busy', 503: 'model_unavailable'}.get(response.status_code, 'backend_error')
                return {'error': {'code': code, 'message': 'Live inference unavailable or demonstration quota reached. Please contact the demonstrator.'}}
            return response.json()
        except (httpx.HTTPError, ValueError):
            return {'error': {'code': 'unreachable', 'message': 'The inference service could not be reached.'}}

    def health(self):
        return self.call('/health')

    def configurations(self):
        return self.call('/configurations')

    def generate_answer(self, question, model_config, use_rag):
        return self.call('/generate', {'question': question, 'model_config': model_config, 'use_rag': use_rag})
