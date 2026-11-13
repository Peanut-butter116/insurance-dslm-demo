"""Approval-only cloud actions. Default invocation creates no resources or compute."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

ACTIONS={'stage':'private_asset_transfer','smoke':'gpu_smoke_test','deploy':'public_endpoint'}

def approval_valid(value,now=None,scope='public_endpoint'):
    now=time.time() if now is None else now
    gross=value.get('gross_usage_cap_usd',0)
    net=value.get('out_of_pocket_cap_usd',-1)
    return (value.get('owner_approved') is True and value.get('private_deployment_approved') is True
        and value.get('app')=='insurance-slm-meeting-demo' and value.get('gpu')=='L4'
        and isinstance(gross,(int,float)) and not isinstance(gross,bool) and 0<gross<=0.60
        and isinstance(net,(int,float)) and not isinstance(net,bool) and net==0
        and value.get('zero_spend_limit_verified') is True
        and value.get('no_auto_topups_verified') is True
        and value.get('remaining_credit_verified') is True
        and value.get('remaining_credit_usd',0)>=1
        and 0<value.get('provider_usage_budget_usd',0)<=0.70
        and value.get('credit_expires_at_epoch',0)>value.get('expires_at_epoch',0)+600
        and value.get('provider_budget_verified') is True and bool(value.get('workspace'))
        and scope in value.get('approved_actions',[])
        and now<value.get('expires_at_epoch',0)<=now+7200)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--activate',action='store_true')
    p.add_argument('--action',choices=ACTIONS,default='deploy')
    p.add_argument('--owner-approval-receipt')
    args=p.parse_args(argv)
    if not args.activate:
        print('PREPARATION ONLY: no deployment. Explicit owner approval and provider budget verification are required.')
        return 0
    if not args.owner_approval_receipt:raise SystemExit('No activation: owner approval receipt required')
    value=json.loads(Path(args.owner_approval_receipt).read_text())
    if not approval_valid(value,scope=ACTIONS[args.action]):
        raise SystemExit('No activation: missing, expired or incompatible approval/budget receipt')
    # Check workspace identity before starting Modal run/deploy or building an image.
    import modal
    if modal.Workspace.from_context().name()!=value['workspace']:
        raise SystemExit('No activation: authenticated workspace differs from approved workspace')
    if args.action=='stage':cmd=['run','backend/stage_modal.py']
    elif args.action=='smoke':cmd=['run','backend/smoke_modal.py']
    else:cmd=['deploy','backend/modal_app.py']
    return subprocess.run([sys.executable,'-m','modal',*cmd],check=False).returncode

if __name__=='__main__':raise SystemExit(main())
