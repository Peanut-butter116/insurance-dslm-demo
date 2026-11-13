import pytest
from backend.smoke_validation import validate_selection
from scripts.activate_modal import approval_valid

def test_proof_requires_actual_disabled_base_and_single_selected_adapter():
    validate_selection('base',False,['D1500'])
    validate_selection('D1000',True,['D1000'])
    validate_selection('D1500',True,['D1500'])
    for args in [('base',True,['D1000']),('D1500',True,['D1000']),('D1000','irregular',['D1000']),('D1000',True,['D1000','D1500'])]:
        with pytest.raises(ValueError):validate_selection(*args)

def test_gpu_permission_is_not_public_deployment_permission():
    receipt={'owner_approved':True,'private_deployment_approved':True,'workspace':'synthetic',
             'app':'insurance-slm-meeting-demo','gpu':'L4','gross_usage_cap_usd':0.60,'zero_spend_limit_verified':True,'no_auto_topups_verified':True,'remaining_credit_verified':True,'remaining_credit_usd':1,'provider_usage_budget_usd':0.70,'credit_expires_at_epoch':10000,
             'out_of_pocket_cap_usd':0,'provider_budget_verified':True,
             'approved_actions':['gpu_smoke_test'],'expires_at_epoch':200}
    assert approval_valid(receipt,now=100,scope='gpu_smoke_test')
    assert not approval_valid(receipt,now=100,scope='public_endpoint')
    assert not approval_valid(receipt,now=100,scope='private_asset_transfer')
