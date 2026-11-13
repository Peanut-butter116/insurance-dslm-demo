"""Print an exact approval proposal only; performs no service or artifact operations."""
import argparse,json
from backend.hf_delivery import DeliveryPlan
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--namespace',required=True);args=p.parse_args()
    plan=DeliveryPlan(args.namespace)
    print(json.dumps({'plan':plan.approval_payload(),'owner_transfer_approved':False,
        'narrow_upload_token_verified':False,'free_storage_verified':False},indent=2))
