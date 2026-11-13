"""Read-only official quota check. Never creates a notebook, GPU, storage or payment."""
import json

def read_quota():
    from kaggle import api
    from kagglesdk.kernels.types.kernels_api_service import ApiGetAcceleratorQuotaStatisticsRequest
    api.authenticate()
    with api.build_kaggle_client() as client:
        value=client.kernels.kernels_api_client.get_accelerator_quota_statistics(ApiGetAcceleratorQuotaStatisticsRequest())
    q=value.gpu_quota
    remaining=max(0,(q.total_time_allowed-q.time_used-q.time_reserved).total_seconds())
    return {'gpu_allowance_seconds':q.total_time_allowed.total_seconds(),
            'gpu_used_seconds':q.time_used.total_seconds(),'gpu_reserved_seconds':q.time_reserved.total_seconds(),
            'gpu_remaining_seconds':remaining,'pay_to_scale_enabled':q.is_pay_to_scale_enabled,
            'quota_refresh_time_as_reported':str(value.quota_refresh_time),
            'ready_for_free_session_approval':remaining>=5400 and not q.is_pay_to_scale_enabled,
            'session_started':False}

if __name__=='__main__':print(json.dumps(read_quota(),indent=2))
