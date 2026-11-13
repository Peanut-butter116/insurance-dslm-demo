from scripts.activate_modal import main, approval_valid

def test_activation_default_is_nonbillable(capsys):
    assert main([])==0
    assert 'no deployment' in capsys.readouterr().out

def test_missing_expired_or_large_budget_not_permission():
    assert not approval_valid({},now=100)
    base={'owner_approved':True,'app':'insurance-slm-meeting-demo','gpu':'L4','gross_usage_cap_usd':2,'provider_budget_verified':True,'expires_at_epoch':200}
    assert approval_valid(base,now=100)
    for change in ({'owner_approved':False},{'gross_usage_cap_usd':20},{'expires_at_epoch':90},{'provider_budget_verified':False},{'gpu':'H100'}):
        assert not approval_valid({**base,**change},now=100)
