"""Bounded meeting controller. No model loading, network calls or exposure on import."""
import threading
import time
from dataclasses import dataclass
from config.model_registry import BASE_REVISION, ADAPTERS
from config.deployment import BUNDLE_SHA256
from backend.smoke_validation import validate_selection

@dataclass(frozen=True)
class ReleaseReview:
    review_id: str
    bundle_sha256: str
    audience: tuple[str, ...]
    expires_at: float
    platform_permission_verified: bool = False
    owner_exposure_approved: bool = False
    generated_answers_approved: bool = False
    arbitrary_questions_approved: bool = False

    def verify(self, username):
        if (not self.review_id or self.bundle_sha256 != BUNDLE_SHA256
            or username not in self.audience or not self.audience
            or not time.time() < self.expires_at <= time.time()+2700
            or not all((self.platform_permission_verified, self.owner_exposure_approved,
                        self.generated_answers_approved, self.arbitrary_questions_approved))):
            raise ValueError('Remote meeting release and platform review required')

class MeetingController:
    def __init__(self, session=None, *, expires_at=None, limit=12, rpm=3):
        self.session=session
        self.expires_at=expires_at or time.time()+2700
        self.limit=min(limit,12);self.rpm=min(rpm,3)
        self.calls=[];self.lock=threading.Lock();self.closed=False

    def close(self):
        # Wait for an active generation; never unload a model beneath it.
        with self.lock:
            self.closed=True
            if self.session is not None:self.session.close()
            self.session=None

    def predict(self, question, condition):
        unavailable={'status':'Inference temporarily unavailable. No answer generated.'}
        if self.closed or time.time()>=self.expires_at:return {'status':'Meeting session expired. No answer generated.'}
        if self.session is None:return unavailable
        if not isinstance(question,str) or not 1<=len(question.strip())<=4000 or condition not in ('base','D1000','D1500'):
            return {'status':'Enter a question of 1–4000 characters and choose an available model.'}
        if not self.lock.acquire(blocking=False):return {'status':'Model busy; wait for the current answer.'}
        try:
            now=time.time()
            # Recheck after acquiring the lock. Failed/withheld attempts consume quota too.
            if self.closed or now>=self.expires_at:return {'status':'Meeting session expired. No answer generated.'}
            if len(self.calls)>=self.limit or sum(t>now-60 for t in self.calls)>=self.rpm:
                return {'status':'Meeting request limit reached. No answer generated.'}
            self.calls.append(now)
            result=self.session.predict(question.strip(),condition)
            if result.get('error'):
                return {'status':'Output withheld or inference failed. No substitute answer generated.'}
            proof=result.get('actual_selection_proof') or {}
            validate_selection(condition,proof.get('enabled'),proof.get('active_adapters',[]))
            expected=BASE_REVISION if condition=='base' else 'sha256:'+ADAPTERS[condition]['sha256']
            if result.get('checkpoint')!=expected or not isinstance(result.get('answer'),str):
                return {'status':'Checkpoint identity verification failed. Output withheld.'}
            # Strict field projection: never echo questions, exceptions, file paths or raw evidence.
            gpu=result.get('gpu_measurements') or {}
            details={k:v for k,v in gpu.items() if k in ('peak_allocated_bytes','peak_reserved_bytes','total_bytes')
                     and isinstance(v,int) and v>=0}
            return {'status':'New model response; RAG disabled. No verified policy citation available for this answer.',
                    'answer':result['answer'],'checkpoint':expected,'condition':condition,
                    'selection':{'enabled':proof['enabled'],'active_adapters':list(proof['active_adapters'])},
                    'refused':result.get('refused') if isinstance(result.get('refused'),bool) else None,
                    'latency_seconds':result.get('latency_seconds') if isinstance(result.get('latency_seconds'),(int,float)) else None,
                    'gpu':details}
        except Exception:
            return {'status':'Inference failed or selection could not be verified. No substitute answer generated.'}
        finally:self.lock.release()

    def verify_remote(self, review, username):
        review.verify(username)
        manifest=getattr(getattr(self.session,'_engine',None),'manifest',{})
        if (manifest.get('public_generation_approved') is not True
            or manifest.get('meeting_release_review_id')!=review.review_id):
            raise ValueError('Private-test runtime cannot be exposed remotely; approved runtime manifest required')
