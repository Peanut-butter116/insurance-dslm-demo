from scripts.activate_modal import main, approval_valid

def test_activation_default_is_nonbillable(capsys):
    assert main([])==0
    assert 'no deployment' in capsys.readouterr().out

def test_missing_expired_or_large_budget_not_permission():
    assert not approval_valid({},now=100)
    base={'owner_approved':True,'private_deployment_approved':True,'workspace':'synthetic-workspace','out_of_pocket_cap_usd':0,'approved_actions':['public_endpoint'],'app':'insurance-slm-meeting-demo','gpu':'L4','gross_usage_cap_usd':0.60,'zero_spend_limit_verified':True,'no_auto_topups_verified':True,'remaining_credit_verified':True,'remaining_credit_usd':1,'provider_usage_budget_usd':0.70,'credit_expires_at_epoch':10000,'provider_budget_verified':True,'expires_at_epoch':200}
    assert approval_valid(base,now=100)
    for change in ({'owner_approved':False},{'gross_usage_cap_usd':1},{'expires_at_epoch':90},{'provider_budget_verified':False},{'gpu':'H100'}):
        assert not approval_valid({**base,**change},now=100)

def test_one_dollar_credit_is_not_approval_or_zero_spend_proof():
    base={'owner_approved':True,'private_deployment_approved':True,'workspace':'synthetic',
          'out_of_pocket_cap_usd':0,'approved_actions':['gpu_smoke_test'],
          'app':'insurance-slm-meeting-demo','gpu':'L4','gross_usage_cap_usd':0.60,
          'provider_budget_verified':True,'expires_at_epoch':200,
          'zero_spend_limit_verified':True,'no_auto_topups_verified':True,
          'remaining_credit_verified':True,'remaining_credit_usd':1,
          'provider_usage_budget_usd':0.70,'credit_expires_at_epoch':10000}
    assert approval_valid(base,now=100,scope='gpu_smoke_test')
    for change in ({'out_of_pocket_cap_usd':0.01},{'gross_usage_cap_usd':1},
                   {'remaining_credit_usd':0.5},{'zero_spend_limit_verified':False},
                   {'credit_expires_at_epoch':250},{'no_auto_topups_verified':False},
                   {'provider_usage_budget_usd':1}):
        assert not approval_valid({**base,**change},now=100,scope='gpu_smoke_test')
