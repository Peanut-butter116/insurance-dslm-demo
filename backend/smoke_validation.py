"""Independent checks of PEFT's actual state while generation executes."""
def validate_selection(condition,enabled,active_adapters):
    if condition=='base':
        if enabled is not False:raise ValueError('Base generation still has an enabled adapter')
    elif condition in ('D1000','D1500'):
        if enabled is not True or list(active_adapters)!=[condition]:
            raise ValueError('Loaded adapter selection does not match requested condition')
    else:raise ValueError('Unknown smoke-test condition')
