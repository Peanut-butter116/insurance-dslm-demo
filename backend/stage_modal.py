"""APPROVAL ONLY: one ephemeral CPU transfer; no GPU and no public endpoint."""
import modal
from config.deployment import APP_NAME,VOLUME_NAME

app=modal.App(APP_NAME+'-private-staging')
image=(modal.Image.debian_slim(python_version='3.11')
       .pip_install('kaggle==2.2.5','six==1.17.0','requests')
       .add_local_python_source('backend','config'))
volume=modal.Volume.from_name(VOLUME_NAME,create_if_missing=False)

@app.function(image=image,cpu=(1,1),memory=(1024,2048),timeout=600,max_containers=1,
              volumes={'/private-assets':volume},
              secrets=[modal.Secret.from_name('insurance-slm-artifact-reader')])
def stage():
    import contextlib,os,tempfile
    from pathlib import Path
    from backend.artifact_transfer import download_private_source,extract_verified_bundle
    # Suppress downloader output, paths, temporary URLs and authentication diagnostics.
    with open(os.devnull,'w') as sink,contextlib.redirect_stdout(sink),contextlib.redirect_stderr(sink):
        with tempfile.TemporaryDirectory() as tmp:
            archive=Path(tmp)/'bundle.tar.gz'
            download_private_source(archive)
            receipt=extract_verified_bundle(archive,Path('/private-assets/bundle'))
        volume.commit()
    return receipt

@app.local_entrypoint()
def main():
    # Run only through scripts/activate_modal.py --action stage after owner approval.
    print(stage.remote())
