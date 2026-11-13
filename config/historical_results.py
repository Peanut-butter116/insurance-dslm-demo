"""Approved aggregate-only early research evidence; NEVER a live D500 checkpoint."""
D500_STATUS = {
    'live_available': False,
    'historical_d500_results_found': False,
    'reason': 'No verified D500-trained checkpoint or D500-bound evaluation was located. Early SFT receipts identify 21 training rows, not 500.',
}
EARLY_SEED_RESULTS = [
    {'experiment':'Early Ministral seed SFT', 'actual_training_rows':21, 'condition':'SFT',
     'benchmark_questions':140, 'answerable_questions':118, 'unanswerable_questions':22,
     'citation_resolution':0.0, 'resolved_citations':0, 'citation_occurrences':8,
     'balanced_abstention':0.5905238828967643, 'correct_refusals':12, 'over_refusals':43,
     'parse_rate':0.45, 'parsed_answers':63, 'correctness':None, 'semantic_citation_support':None,
     'saved_predictions_sha256':'58097b61d47cde7c3107cd68b37786444b422538edf7a2133621bb5d584663bc'},
    {'experiment':'Early Ministral seed SFT', 'actual_training_rows':21, 'condition':'SFT + RAG',
     'benchmark_questions':140, 'answerable_questions':118, 'unanswerable_questions':22,
     'citation_resolution':0.9147286821705426, 'resolved_citations':118, 'citation_occurrences':129,
     'balanced_abstention':0.6960708782742682, 'correct_refusals':9, 'over_refusals':2,
     'parse_rate':0.8428571428571429, 'parsed_answers':118, 'correctness':None, 'semantic_citation_support':None,
     'saved_predictions_sha256':'65e5e067af1b260b75b532ad25d81a5a9ff1604d1fcfb59f390d2624a929778c'},
]
EARLY_SEED_ADAPTER_SHA256 = '9c4a952d43c98a6e0f92aaa6cdb10e78e83f39b1101223f6c9a4dc74a6011c46'
