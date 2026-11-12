from backend.privacy import PublicRelease

# Independently authored artificial text; not extracted from insurance data.
TEXT = 'Purple robots collect seventeen paper umbrellas beside the imaginary moon station.'
CHUNK = {'id':'synthetic-1','text':TEXT,'meta':{'section_id':'A','page':1}}

def guard(display=(),metadata=()):
    p=PublicRelease([CHUNK], display, metadata)
    p.resolver=lambda citation,chunks:{'n_supported':1}
    return p

def test_restricted_long_quote_withheld():
    p=guard()
    assert p.release(TEXT,[CHUNK],{'citations':[]},None)==(None,[],[])

def test_no_raw_evidence_without_allowlist():
    p=guard()
    answer,citations,evidence=p.release('A newly generated short summary.',[CHUNK],{'citations':[]},None)
    assert answer and not evidence

def test_metadata_only_and_unverified_citation():
    p=guard(metadata=['synthetic-1'])
    checked={'citations':[{'citation':'[Artificial, Fiction, A, p.1]','supported':True}]}
    answer,cs,evidence=p.release('See [Artificial, Fiction, A, p.1]',[CHUNK],checked,None)
    assert cs[0]['resolves'] and cs[0]['evidence_excerpt'] is None
    assert evidence[0]['excerpt'] is None
    assert TEXT not in str((answer,cs,evidence))

def test_unapproved_metadata_removed():
    checked={'citations':[{'citation':'[Artificial, Fiction, A, p.1]','supported':True}]}
    answer,cs,_=guard().release('See [Artificial, Fiction, A, p.1]',[CHUNK],checked,None)
    assert 'Fiction' not in answer and not cs[0]['resolves']

def test_explicit_display_allowlist():
    p=guard(['synthetic-1'],['synthetic-1'])
    answer,_,evidence=p.release(TEXT,[CHUNK],{'citations':[]},None)
    assert answer==TEXT and evidence[0]['excerpt']==TEXT
