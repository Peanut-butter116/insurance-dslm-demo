from scripts.build_preview import build
from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_preview_bundle_is_public_allowlist(tmp_path):
    files=build(tmp_path)
    assert set(files)=={'app.py','config/__init__.py','config/model_registry.py','example_questions.py'}
    assert "os.environ['PUBLIC_PREVIEW'] = '1'" in files['app.py']
    assert not any('backend/' in name or 'client/' in name for name in files)

def test_preview_has_full_controls_without_backend(monkeypatch):
    monkeypatch.setenv('PUBLIC_PREVIEW','1')
    monkeypatch.setenv('INFERENCE_API_URL','https://must-not-be-called.example')
    monkeypatch.setenv('INFERENCE_API_TOKEN','not-a-real-token')
    at=AppTest.from_file(str(Path(__file__).parents[1]/'app.py')).run(timeout=20)
    assert not at.exception
    assert len(at.text_area)==1
    assert any(b.label=='Generate Answer' and b.disabled for b in at.button)
    assert at.selectbox(key='dataset').disabled
    at.toggle(key='sft').set_value(True).run()
    assert not at.selectbox(key='dataset').disabled
    at.selectbox(key='dataset').select('D1500').run()
    assert at.selectbox(key='dataset').value=='D1500'
