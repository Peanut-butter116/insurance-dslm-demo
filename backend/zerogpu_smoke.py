"""One shot per condition, across GPU worker forks. Receipt contains no answers."""
import hashlib,json,sqlite3,time,secrets
from pathlib import Path
from config.model_registry import BASE_REVISION,ADAPTERS
QUESTION='What conditions apply to getting a courtesy car under this motor policy?'
CONDITIONS=('base','D1000','D1500')
DURATION_SECONDS=60
REQUIRED_FREE_SECONDS=240  # Three 60s requests + 60s unspent margin; never paid extension.


def verify_free_quota(receipt, requests_left=3):
    if not isinstance(receipt,dict) or requests_left not in (1,2,3):raise ValueError("Fresh quota receipt required")
    required_seconds=requests_left*DURATION_SECONDS+60
    if (receipt.get('free_account_verified') is not True or receipt.get('no_paid_extension') is not True
        or receipt.get('overquota_used')!=0 or not 0<=time.time()-receipt.get('checked_at',0)<=300
        or receipt.get('remaining',0)<required_seconds):
        raise ValueError('Fresh verified free quota of enough for remaining cases plus margin required')

class BoundedSmoke:
    def __init__(self,runtime,journal,expires_at):
        self.runtime=runtime;self.journal=Path(journal);self.expires_at=expires_at
        self.journal.parent.mkdir(parents=True,exist_ok=True)
        with sqlite3.connect(self.journal) as db:
            db.execute('CREATE TABLE IF NOT EXISTS cases (condition TEXT PRIMARY KEY,status TEXT NOT NULL,receipt TEXT,nonce TEXT)')

    def reserve(self,condition,quota_receipt=None):
        # Main-process CPU preflight BEFORE ZeroGPU allocation; rejects repeat clicks.
        if time.time()>=self.expires_at:raise ValueError('Smoke approval expired')
        with sqlite3.connect(self.journal,timeout=5) as db:
            db.execute('BEGIN IMMEDIATE')
            previous=dict(db.execute('SELECT condition,status FROM cases').fetchall())
            if (condition not in CONDITIONS or condition in previous or any(v!='passed' for v in previous.values())
                or condition!=CONDITIONS[len(previous)]):raise ValueError('No retries or out-of-order smoke requests')
            verify_free_quota(quota_receipt,requests_left=len(CONDITIONS)-len(previous))
            nonce=secrets.token_hex(24)
            db.execute('INSERT INTO cases VALUES (?,?,NULL,?)',(condition,'reserved',nonce))
        return {'condition':condition,'nonce':nonce}

    def predict(self,reservation):
        # Only directly bound @spaces.GPU handler invokes this worker method.
        if time.time()>=self.expires_at:raise ValueError('Smoke approval expired')
        condition=reservation['condition']
        with sqlite3.connect(self.journal,timeout=5) as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT status,nonce FROM cases WHERE condition=?',(condition,)).fetchone()
            if row!=('reserved',reservation['nonce']):raise ValueError('Invalid or already used reservation')
            db.execute('UPDATE cases SET status=? WHERE condition=?',('intent',condition))
        started=time.monotonic()
        from backend.zerogpu_runtime import measure_prediction
        try:
            result=measure_prediction(self.runtime,QUESTION,condition)
            row={'condition':condition,'checkpoint':BASE_REVISION if condition=='base' else 'sha256:'+ADAPTERS[condition]['sha256'],
                 'selection':result['actual_selection_proof'],'latency_seconds':result.get('latency_seconds'),
                 'gpu':result['gpu_measurements'],'allocation':result['allocation_diagnostics'],
                 'screened_output_released':not bool(result.get('error')),
                 'final_answer_present':bool(result.get('final_answer_present')),
                 'refused':result.get('refused'),'raw_answers_returned':False,'rag_enabled':False}
            if not result.get('error'):row['answer_sha256']=hashlib.sha256(result['answer'].encode()).hexdigest()
            passed=row['screened_output_released'] and row['final_answer_present']
            row['status']='passed' if passed else 'failed'
        except Exception as e:
            row={'condition':condition,'status':'failed','error_type':type(e).__name__,'raw_answers_returned':False}
        row['worker_seconds']=time.monotonic()-started
        with sqlite3.connect(self.journal) as db:
            db.execute('UPDATE cases SET status=?,receipt=? WHERE condition=?',(row['status'],json.dumps(row),condition))
        return row
