import hashlib,io,json,tarfile
from pathlib import Path
import pytest
from backend.artifact_transfer import extract_verified_bundle

def bundle(tmp_path,*,bad_inventory=False,extra=None):
    data=b'independently authored synthetic asset'
    inv={'assets/synthetic.txt':hashlib.sha256(data).hexdigest() if not bad_inventory else '0'*64}
    files={'assets/synthetic.txt':data,'inventory.json':json.dumps(inv).encode(),
           'serving-manifest.json':json.dumps({'public_generation_approved':False,'public_display_chunk_ids':[],'public_metadata_chunk_ids':[]}).encode()}
    if extra:files[extra]=b'synthetic'
    p=tmp_path/'test.tar.gz'
    with tarfile.open(p,'w:gz') as tar:
        for name,raw in files.items():
            m=tarfile.TarInfo(name);m.size=len(raw);tar.addfile(m,io.BytesIO(raw))
    return p,hashlib.sha256(p.read_bytes()).hexdigest(),p.stat().st_size

def test_transfer_preserves_restricted_output_defaults(tmp_path):
    p,h,n=bundle(tmp_path)
    r=extract_verified_bundle(p,tmp_path/'destination',h,n)
    assert r['inventory_files']==1 and r['public_generation_approved'] is False
    assert (tmp_path/'destination/assets/synthetic.txt').is_file()
    with pytest.raises(ValueError):extract_verified_bundle(p,tmp_path/'destination',h,n)

@pytest.mark.parametrize('options',[{'bad_inventory':True},{'extra':'../escape'},{'extra':'assets/unlisted.txt'}])
def test_transfer_rejects_corruption_traversal_and_unlisted_files(tmp_path,options):
    p,h,n=bundle(tmp_path,**options)
    with pytest.raises(ValueError):extract_verified_bundle(p,tmp_path/'destination',h,n)
    assert not (tmp_path/'destination').exists()
