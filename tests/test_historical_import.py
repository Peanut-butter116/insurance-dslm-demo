import pytest
from backend.schemas import GenerateRequest
from config.historical_results import D500_STATUS, EARLY_SEED_RESULTS
from config.model_registry import ADAPTERS

def test_seed_cannot_be_relabelled_d500():
    assert not D500_STATUS['live_available']
    assert not D500_STATUS['historical_d500_results_found']
    assert 'D500' not in ADAPTERS
    with pytest.raises(ValueError):
        GenerateRequest(question='Synthetic question',model_config='D500',use_rag=False)
    assert all(r['actual_training_rows']==21 for r in EARLY_SEED_RESULTS)
    assert all(r['correctness'] is None and r['semantic_citation_support'] is None for r in EARLY_SEED_RESULTS)

def test_imported_denominators_and_rates():
    for r in EARLY_SEED_RESULTS:
        assert r['benchmark_questions']==r['answerable_questions']+r['unanswerable_questions']==140
        assert r['parse_rate']==pytest.approx(r['parsed_answers']/140)
        assert r['citation_resolution']==pytest.approx(r['resolved_citations']/r['citation_occurrences'])
        ba=.5*((118-r['over_refusals'])/118+r['correct_refusals']/22)
        assert r['balanced_abstention']==pytest.approx(ba)
