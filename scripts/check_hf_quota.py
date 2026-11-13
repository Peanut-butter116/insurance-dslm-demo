"""Read-only existing-profile check; never creates a Space, authenticates anew or allocates GPU."""
import json,time

def check(api):
    try:
        user=api.whoami()
        quota=api.get_zero_gpu_quota()
        return {'verified':True,'namespace':user['name'],'remaining':quota.remaining,
            'base':quota.base,'overquota_used':quota.overquota_used,'resets_at':str(quota.resets_at),
            'checked_at':time.time(),'is_pro':bool(user.get('isPro',False)),'activated_resources':False}
    except Exception as e:return {'verified':False,'error_type':type(e).__name__,'activated_resources':False}

if __name__=='__main__':
    from huggingface_hub import HfApi
    print(json.dumps(check(HfApi()),indent=2))
