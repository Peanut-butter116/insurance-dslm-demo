"""Approval-only activation helper. Default invocation starts no cloud resources."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

def approval_valid(value,now=None):
    now=time.time() if now is None else now
    return (value.get('owner_approved') is True and value.get('app')=='insurance-slm-meeting-demo'
        and value.get('gpu')=='L4' and 0<value.get('gross_usage_cap_usd',0)<=2
        and value.get('provider_budget_verified') is True
        and now<value.get('expires_at_epoch',0)<=now+7200)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--activate',action='store_true')
    p.add_argument('--owner-approval-receipt')
    args=p.parse_args(argv)
    if not args.activate:
        print('PREPARATION ONLY: no deployment. Explicit owner approval and provider budget verification are required.')
        return 0
    if not args.owner_approval_receipt:
        raise SystemExit('No activation: owner approval receipt required')
    value=json.loads(Path(args.owner_approval_receipt).read_text())
    if not approval_valid(value):
        raise SystemExit('No activation: missing, expired or incompatible approval/budget receipt')
    # This receipt records actual explicit owner permission; do not generate it automatically.
    return subprocess.run([sys.executable,'-m','modal','deploy','backend/modal_app.py'],check=False).returncode

if __name__=='__main__':raise SystemExit(main())
