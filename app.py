# Public Streamlit frontend: every generation goes to the authenticated backend.
import os
import hmac
import streamlit as st
from config.model_registry import BASE_MODEL, BASE_REVISION, ADAPTERS
from example_questions import EXAMPLES
from config.historical_results import D500_STATUS, EARLY_SEED_RESULTS

st.set_page_config(page_title='UK Motor Insurance — SLM Research Demo', layout='centered')
st.title('UK Motor Insurance — Small Language Model Research Demo')
st.caption('Tech Mahindra Makers Lab | Policy-Grounded Question Answering')
st.caption('Research demonstration. Check the original policy wording; do not enter personal or claim details.')

def setting(name):
    try:
        return str(st.secrets.get(name, os.environ.get(name, '')))
    except FileNotFoundError:
        return os.environ.get(name, '')

preview = os.environ.get('PUBLIC_PREVIEW') == '1'
access_code = '' if preview else setting('DEMO_ACCESS_CODE')
backend_url = '' if preview else setting('INFERENCE_API_URL')
backend_token = '' if preview else setting('INFERENCE_API_TOKEN')
entered = ''
if backend_url and backend_token and access_code and not preview:
    entered = st.text_input('Meeting access code', type='password')
connected = bool(backend_url and backend_token and access_code and hmac.compare_digest(entered, access_code))
client = None
health, status = {}, {}
if connected:
    from client.inference_client import InferenceClient
    client = InferenceClient(backend_url, backend_token, setting('MODAL_PROXY_KEY'), setting('MODAL_PROXY_SECRET'))
    if st.button('Connect / refresh model service'):
        st.session_state['runtime_health'] = client.health()
        st.session_state['runtime_configs'] = client.configurations() if not st.session_state['runtime_health'].get('error') else {}
    health = st.session_state.get('runtime_health', {})
    status = st.session_state.get('runtime_configs', {})
configs = status.get('configurations', [])
ready_keys = {c['key'] for c in configs if c.get('available')}
ready = connected and health.get('status') == 'ready'
if ready:
    st.success('Live inference available · capped meeting demonstration')
else:
    st.warning('Inference temporarily unavailable — GPU backend not activated or connected.')
    st.caption('Review the real interface below. Generation is disabled; no saved or simulated answers are shown.')
if preview:
    st.info('Public website preview · runs in your browser · no model, backend credentials or policy data are loaded.')

with st.sidebar:
    st.header('Model configuration')
    st.selectbox('Base model', [BASE_MODEL])
    sft = st.toggle('Supervised fine-tuning', value=False, key='sft')
    rag = st.toggle('Retrieval-Augmented Generation', value=True)
    dataset = st.selectbox('Training data size — source-dataset experiment', ['D1000', 'D1500'], disabled=not sft, key='dataset')
    st.caption('D500 — unavailable: no verified checkpoint.')
    key = dataset if sft else 'base'
    with st.expander('Model details'):
        st.write('Base revision: ' + BASE_REVISION)
        st.write('Actual fine-tuning rows: ' + (str(ADAPTERS[dataset]['training_rows']) if sft else 'not applicable'))
        st.write('Checkpoint: ' + ('sha256:' + ADAPTERS[dataset]['sha256'] if sft else 'original base'))
        st.caption('Dataset selection has no effect while SFT is off.')
    st.caption('Citation resolution verifies an identifier, not semantic support for a claim.')

choice = st.selectbox('Example question', list(EXAMPLES))
if st.session_state.get('last_example') != choice:
    st.session_state['question'] = EXAMPLES[choice]
    st.session_state['last_example'] = choice
with st.form('question_form'):
    question = st.text_area('Your UK motor insurance question', key='question', max_chars=4000, height=110)
    can_generate = ready and key in ready_keys and (not rag or status.get('rag_available', False))
    submitted = st.form_submit_button('Generate Answer', type='primary', disabled=not can_generate)
if ready and not can_generate:
    st.info('This checkpoint or the approved retrieval runtime is unavailable. Select an available configuration.')
if submitted:
    if not question.strip():
        st.error('Please enter a question.')
    else:
        with st.spinner('Generating a new model answer…'):
            st.session_state['prediction'] = client.generate_answer(question, key, rag)
record = st.session_state.get('prediction')
if record:
    if record.get('error'):
        st.error(record['error']['message'])
    else:
        st.subheader('Model answer')
        st.caption('Answer for: ' + record['question'])
        st.write(record['answer'])
        st.caption('Refusal detected: ' + ('Yes' if record['refused'] else 'No'))
        # Streamlit's text code block provides a native clipboard button.
        with st.expander('Copy Answer'):
            st.code(record['answer'], language=None)
            st.download_button('Download answer', record['answer'], 'answer.txt', 'text/plain')
        st.subheader('Policy citations')
        citations = record.get('citations', [])
        if not any(c.get('resolves') for c in citations):
            st.info('No verified policy citation available for this answer.')
        for c in citations:
            st.write(c['citation'])
            st.caption('Resolves to retrieved evidence' if c['resolves'] else 'Unverified model-generated reference')
            if c.get('evidence_excerpt'):
                st.text(c['evidence_excerpt'])
            else:
                st.caption('Source reference available; policy excerpt restricted.')
        if record['rag']:
            with st.expander('Retrieved evidence'):
                for evidence in record.get('retrieved_evidence', []):
                    st.write(evidence['source_id'])
                    st.caption(f"Section {evidence['section']} · page {evidence['page']}")
                    if evidence.get('excerpt'):
                        st.text(evidence['excerpt'])
                st.caption('Excerpts are shown only for documents approved for public display.')
        with st.expander('Generation details'):
            st.json({k: record.get(k) for k in ('model_id', 'revision', 'checkpoint', 'sft', 'dataset_version',
                'training_rows', 'rag', 'retrieval_status', 'latency_seconds', 'serving_status', 'output_complete')})

with st.expander('Historical early research — not live D500 inference'):
    st.write(D500_STATUS['reason'])
    st.caption('These saved aggregate metrics belong to a 21-row seed SFT run on a 140-question mixed-insurance benchmark. They are not D500 results and are not directly comparable to the later 76-question motor evaluation. No predictions are replayed here.')
    st.table([{
        'Condition': r['condition'], 'Actual SFT rows': r['actual_training_rows'],
        'Questions': r['benchmark_questions'],
        'Citation resolution': f"{r['resolved_citations']}/{r['citation_occurrences']}",
        'Balanced abstention': f"{100*r['balanced_abstention']:.2f}%",
        'Correct refusals': f"{r['correct_refusals']}/{r['unanswerable_questions']}",
        'Over-refusals': f"{r['over_refusals']}/{r['answerable_questions']}",
        'Parse': f"{r['parsed_answers']}/{r['benchmark_questions']}",
    } for r in EARLY_SEED_RESULTS])
    st.caption('Answer correctness and semantic citation support are not imported: the inspected deterministic reports do not establish those scores. Resolution is metadata matching; parse means refusal or recognized citation, not JSON validity.')
