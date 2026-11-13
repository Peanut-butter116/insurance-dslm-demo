"""Prepared private cloud-to-cloud delivery. No repo creation or upload on import."""
from dataclasses import dataclass,asdict
from pathlib import Path
import re
import os
from config.deployment import BUNDLE_SHA256,BUNDLE_BYTES

@dataclass(frozen=True)
class DeliveryPlan:
    namespace: str
    artifact_slug: str = 'insurance-slm-private-serving'
    space_slug: str = 'insurance-slm-private-meeting'
    filename: str = 'private-serving-bundle.tar.gz'
    bundle_sha256: str = BUNDLE_SHA256
    bundle_bytes: int = BUNDLE_BYTES
    owner_only_artifacts: bool = True

    @property
    def artifact_repo(self):return self.namespace+'/'+self.artifact_slug
    @property
    def space_repo(self):return self.namespace+'/'+self.space_slug
    def validate(self):
        if (not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{1,95}',self.namespace)
            or self.artifact_slug!='insurance-slm-private-serving'
            or self.space_slug!='insurance-slm-private-meeting'
            or self.filename!='private-serving-bundle.tar.gz'
            or self.bundle_sha256!=BUNDLE_SHA256 or self.bundle_bytes!=BUNDLE_BYTES
            or self.owner_only_artifacts is not True):raise ValueError('Exact private delivery plan required')
    def approval_payload(self):
        self.validate()
        return {**asdict(self),'repo_type':'model','private':True,'artifact_access':'owner only',
            'space_private':True,'supervisor_artifact_access':False,'create_resources':False}


def verify_transfer_approval(plan, approval):
    expected=plan.approval_payload()
    if (approval.get('plan')!=expected or approval.get('owner_transfer_approved') is not True
        or approval.get('narrow_upload_token_verified') is not True
        or approval.get('free_storage_verified') is not True):
        raise ValueError('Exact destination, permissions and free-storage approval required')


def upload_verified_cloud_bundle(plan, approval, archive, *, token, api):
    verify_transfer_approval(plan,approval)  # Before any service or artifact operation.
    if not (Path('/kaggle')/'working').is_dir():raise RuntimeError('Approved hosted transfer only; no laptop asset download')
    from backend.artifact_transfer import file_sha,extract_verified_bundle
    import tempfile
    archive=Path(archive)
    if archive.stat().st_size!=BUNDLE_BYTES or file_sha(archive)!=BUNDLE_SHA256:raise ValueError('Bundle identity differs')
    info=api.repo_info(repo_id=plan.artifact_repo,repo_type='model',token=token)
    if info.private is not True or info.author!=plan.namespace:raise ValueError('Destination privacy/owner differs')
    if not re.fullmatch('[0-9a-f]{40}',info.sha or ''):raise ValueError('Initialised private destination commit required')
    with tempfile.TemporaryDirectory() as tmp:
        extract_verified_bundle(archive,Path(tmp)/'verified')
    # Existing private repo only. No create_repo, permission change, Space creation,
    # public publication, broad snapshot upload or source-directory upload.
    commit=api.upload_file(path_or_fileobj=str(archive),path_in_repo=plan.filename,
        repo_id=plan.artifact_repo,repo_type='model',token=token,
        parent_commit=info.sha,commit_message='Store approved hash-verified private serving bundle')
    return {'repo_id':plan.artifact_repo,'revision':commit.oid,'bundle_sha256':BUNDLE_SHA256,'bytes':BUNDLE_BYTES}


def download_private_hf_bundle(plan,revision,destination,*,token,api,download):
    plan.validate()
    if not re.fullmatch('[0-9a-f]{40}',revision):raise ValueError('Immutable artifact commit required')
    if not (Path('/kaggle')/'working').is_dir() and os.environ.get('SPACE_ID')!=plan.space_repo:
        raise RuntimeError('Approved hosted artifact read only; never download private assets to a laptop')
    info=api.repo_info(repo_id=plan.artifact_repo,repo_type='model',revision=revision,token=token)
    if info.private is not True or info.author!=plan.namespace or info.sha!=revision:
        raise ValueError('Private artifact identity differs')
    cached=download(repo_id=plan.artifact_repo,repo_type='model',filename=plan.filename,revision=revision,token=token)
    from backend.artifact_transfer import extract_verified_bundle
    return extract_verified_bundle(cached,destination)


def verify_scoped_token(api, token, *, namespace, repositories, write=False):
    """Validate resource-scoped metadata only; never return or log credential values."""
    user=api.whoami(token=token)
    metadata=user.get('auth',{}).get('accessToken',{})
    fine=metadata.get('fineGrained',{})
    scopes=fine.get('scoped',[])
    names=[s.get('entity',{}).get('name') for s in scopes]
    permissions=[p for s in scopes for p in s.get('permissions',[])]
    permitted={'repo.content.read','repo.content.write'} if write else {'repo.content.read'}
    if (user.get('name')!=namespace or metadata.get('role')!='fineGrained'
        or fine.get('global') or fine.get('canReadGatedRepos')
        or set(names)!=set(repositories) or len(names)!=len(repositories)
        or not permissions or any(p not in permitted for p in permissions)
        or (write and 'repo.content.write' not in permissions)):
        raise ValueError('Exact fine-grained repository token scope not established')
    return True
