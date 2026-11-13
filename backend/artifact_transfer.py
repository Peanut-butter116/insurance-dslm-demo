"""Hash-bound cloud-only transfer utilities. Importing this module makes no requests."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
from config.deployment import BUNDLE_SHA256, BUNDLE_BYTES


def file_sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def extract_verified_bundle(archive, destination, expected_sha=BUNDLE_SHA256, expected_size=BUNDLE_BYTES):
    """Validate everything before publishing a new directory; never overwrite assets."""
    archive, destination=Path(archive),Path(destination)
    if destination.exists() or archive.stat().st_size!=expected_size or file_sha(archive)!=expected_sha:
        raise ValueError('Bundle identity differs or destination already exists')
    with tarfile.open(archive) as tar:
        members=tar.getmembers()
        names=[m.name for m in members]
        if len(names)!=len(set(names)):
            raise ValueError('Duplicate archive member')
        for m in members:
            p=PurePosixPath(m.name)
            if not m.isfile() or p.is_absolute() or '..' in p.parts or '\\' in m.name:
                raise ValueError('Unsafe archive member')
        if sum(m.size for m in members)>1024**3:
            raise ValueError('Bundle exceeds serving limit')
        if tar.getmember('inventory.json').size>1024**2 or tar.getmember('serving-manifest.json').size>1024**2:
            raise ValueError('Manifest too large')
        inventory=json.load(tar.extractfile('inventory.json'))
        if set(names)!=set(inventory)|{'inventory.json','serving-manifest.json'}:
            raise ValueError('Archive inventory differs')
        manifest=json.load(tar.extractfile('serving-manifest.json'))
        if (manifest.get('public_generation_approved') is not False
            or manifest.get('public_display_chunk_ids') or manifest.get('public_metadata_chunk_ids')):
            raise ValueError('Bundle must preserve restricted output defaults')
        for name,expected in inventory.items():
            h=hashlib.sha256()
            with tar.extractfile(name) as f:
                for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
            if h.hexdigest()!=expected:
                raise ValueError('Serving file hash differs')
        destination.parent.mkdir(parents=True,exist_ok=True)
        import tempfile
        with tempfile.TemporaryDirectory(dir=destination.parent,prefix='.verified-serving-') as tmp:
            stage=Path(tmp)/'bundle';stage.mkdir(mode=0o700)
            for member in members:
                target=stage/member.name;target.parent.mkdir(parents=True,exist_ok=True)
                with tar.extractfile(member) as source,target.open('wb') as out:
                    for chunk in iter(lambda:source.read(1024*1024),b''):out.write(chunk)
                target.chmod(0o600)
            # Atomic publication after the whole archive and every inventoried file pass.
            stage.rename(destination)
    return {'bundle_sha256':expected_sha,'bundle_bytes':expected_size,
            'inventory_files':len(inventory),'public_generation_approved':False,
            'excerpt_allowlist_empty':True,'model_calls':0}


def verify_private_kernel(kernel,version=None):
    """Hosted metadata check only; never prints or saves notebook source."""
    from kaggle import api
    from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelRequest
    owner,slug=kernel.split('/')
    api.authenticate()
    r=ApiGetKernelRequest();r.user_name=owner;r.kernel_slug=slug
    if version is not None:r.version_label='v'+str(version)
    with api.build_kaggle_client() as client:response=client.kernels.kernels_api_client.get_kernel(r)
    if not response.metadata.is_private or response.metadata.id<=0:
        raise ValueError('Notebook privacy not verified')
    return True


def download_private_source(destination):
    """Only runs on the approved backend CPU worker; no artifact is sent to the laptop."""
    import os
    from kaggle import api
    from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelRequest,ApiListKernelSessionOutputRequest
    import requests
    kernel=os.environ['PRIVATE_BUNDLE_KERNEL']
    version=int(os.environ['PRIVATE_BUNDLE_VERSION'])
    filename=os.environ['PRIVATE_BUNDLE_FILE']
    if version!=38 or not filename.endswith('/private-serving-bundle.tar.gz'):
        raise ValueError('Unexpected source pin')
    owner,slug=kernel.split('/')
    api.authenticate()
    r=ApiGetKernelRequest();r.user_name=owner;r.kernel_slug=slug;r.version_label='v'+str(version)
    with api.build_kaggle_client() as client:response=client.kernels.kernels_api_client.get_kernel(r)
    if not response.metadata.is_private or response.metadata.id<=0:
        raise ValueError('Source privacy not verified')
    del response
    q=ApiListKernelSessionOutputRequest();q.user_name=owner;q.kernel_slug=slug;q.version_label=r.version_label;q.page_size=100
    with api.build_kaggle_client() as client:result=client.kernels.kernels_api_client.list_kernel_session_output(q)
    found=[f for f in result.files if f.file_name==filename]
    if len(found)!=1:raise ValueError('Pinned bundle absent')
    # The temporary authenticated URL is never printed, persisted or returned.
    count=0
    with requests.get(found[0].url,stream=True,timeout=90) as response:
        response.raise_for_status()
        with Path(destination).open('wb') as f:
            for chunk in response.iter_content(1024*1024):
                count+=len(chunk)
                if count>BUNDLE_BYTES:raise ValueError('Unexpected download size')
                f.write(chunk)
    if count!=BUNDLE_BYTES or file_sha(destination)!=BUNDLE_SHA256:
        raise ValueError('Downloaded private artifact differs')
