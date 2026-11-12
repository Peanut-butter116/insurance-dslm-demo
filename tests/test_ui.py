from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_unconfigured_frontend_starts_without_inference(monkeypatch):
    monkeypatch.delenv('DEMO_ACCESS_CODE', raising=False)
    at=AppTest.from_file(str(Path(__file__).parents[1]/'app.py')).run(timeout=20)
    assert not at.exception
    assert any('Temporarily unavailable' in x.value for x in at.warning)

def test_available_controls_and_question_form(monkeypatch):
    monkeypatch.setenv('DEMO_ACCESS_CODE','synthetic-test-code')
    from client.inference_client import InferenceClient
    monkeypatch.setattr(InferenceClient,'health',lambda self:{'status':'ready'})
    monkeypatch.setattr(InferenceClient,'configurations',lambda self:{'rag_available':True,
        'configurations':[{'key':k,'available':True} for k in ('base','D1000','D1500')]})
    at=AppTest.from_file(str(Path(__file__).parents[1]/'app.py')).run(timeout=20)
    at.text_input[0].input('synthetic-test-code').run()
    assert not at.exception
    assert at.selectbox(key='dataset').disabled
    at.toggle(key='sft').set_value(True).run()
    assert not at.selectbox(key='dataset').disabled
    at.selectbox(key='dataset').select('D1500').run()
    assert at.selectbox(key='dataset').value=='D1500'
    assert any('D500' in x.value for x in at.caption)
