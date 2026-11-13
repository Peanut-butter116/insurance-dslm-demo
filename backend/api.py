"""One process, one inference at a time, persistent capped request quota."""
from contextlib import asynccontextmanager
import asyncio
import contextlib
import hmac
import os
from pathlib import Path
import sqlite3
import threading
import time
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from backend.schemas import GenerateRequest

class Quota:
    def __init__(self, path, limit=100, rpm=6):
        self.path, self.limit, self.rpm = str(path), limit, rpm
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS requests (time REAL NOT NULL)')
    def reserve(self):
        # Only timestamps, no prompts, IPs, credentials or answers are stored.
        with sqlite3.connect(self.path, timeout=5) as db:
            db.execute('BEGIN IMMEDIATE')
            now = time.time()
            total = db.execute('SELECT count(*) FROM requests').fetchone()[0]
            recent = db.execute('SELECT count(*) FROM requests WHERE time > ?', (now-60,)).fetchone()[0]
            if total >= self.limit or recent >= self.rpm:
                raise HTTPException(429, 'Demonstration quota reached')
            db.execute('INSERT INTO requests VALUES (?)', (now,))

def create_app(engine=None, token=None, quota=None, expires_at=None):
    token = token or os.environ.get('INFERENCE_API_TOKEN', '')
    gate = threading.Lock()
    @asynccontextmanager
    async def lifespan(app):
        if engine is None:
            from backend.runtime import ResearchRuntime
            try:
                def initialize():
                    with open(os.devnull, 'w') as sink, contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                        return ResearchRuntime.from_environment()
                app.state.engine = await asyncio.to_thread(initialize)
            except Exception:
                app.state.engine = None
        yield
    app = FastAPI(title='Insurance SLM inference', lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.engine = engine
    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse(status_code=422, content={'error': {'code': 'invalid_request', 'message': 'Invalid question or configuration'}})
    @app.middleware('http')
    async def body_limit(request, call_next):
        if request.method == 'POST':
            body = bytearray()
            async for part in request.stream():
                body.extend(part)
                if len(body) > 20000:
                    return JSONResponse(status_code=413, content={'error': 'Request too large'})
            request._body = bytes(body)
        return await call_next(request)
    def authenticate(request: Request):
        expires = expires_at if expires_at is not None else float(os.environ.get('DEMO_EXPIRES_AT', '0'))
        if expires and time.time() >= expires:
            raise HTTPException(403, 'Meeting demonstration has ended')
        supplied = request.headers.get('Authorization', '')
        if len(token) < 32 or not hmac.compare_digest(supplied, 'Bearer '+token):
            raise HTTPException(401, 'Authentication required')
    def active():
        if app.state.engine is None:
            raise HTTPException(503, 'Verified model runtime unavailable')
        return app.state.engine
    @app.get('/health', dependencies=[Depends(authenticate)])
    def health():
        e = active()
        return {'status': 'ready', 'mode': 'live', 'configurations': e.configurations()}
    @app.get('/configurations', dependencies=[Depends(authenticate)])
    def configurations():
        e = active()
        return {'configurations': e.configurations(), 'rag_available': e.rag_available}
    @app.post('/generate', dependencies=[Depends(authenticate)])
    def generate(body: GenerateRequest):
        e = active()
        if not body.question.strip():
            raise HTTPException(422, 'Question is empty')
        if not e.available(body.configuration, body.use_rag):
            raise HTTPException(503, 'Selected model or retrieval unavailable')
        if not gate.acquire(blocking=False):
            raise HTTPException(429, 'Model busy; try again after the current request')
        try:
            quota.reserve()
            with open(os.devnull, 'w') as sink, contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                return e.generate_answer(body.question.strip(), body.configuration, body.use_rag)
        except HTTPException:
            raise
        except Exception:
            # No exception bodies, prompts, policy wording, or secrets in responses/logs.
            raise HTTPException(503, 'Inference failed; no substitute answer generated') from None
        finally:
            gate.release()
    if quota is None:
        quota = Quota(os.environ.get('DEMO_QUOTA_DB', '/tmp/insurance-demo/quota.sqlite3'),
            limit=int(os.environ.get('DEMO_REQUEST_LIMIT', '100')), rpm=int(os.environ.get('DEMO_REQUESTS_PER_MINUTE', '6')))
    return app

app = create_app()
