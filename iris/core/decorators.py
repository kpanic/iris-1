def rpc():
    def decorator(func):
        func._rpc = True
        return func
    return decorator


def event(event_type):
    def decorator(func):
        if not hasattr(func, '_event_types'):
            func._event_types = set()
        func._event_types.add(event_type)
        return func
    return decorator
