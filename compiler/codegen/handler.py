

_handlers = {}

def handler(size: int, main_op, *ops, priority=50):
    def impl(f):
        if main_op not in _handlers:
            _handlers[main_op] = []
        f.size = size
        f.priority = priority
        f.ops = ops
        _handlers[main_op].append(f)
        _handlers[main_op].sort(key=lambda n: (-len(n.ops), n.priority))
        return f
    return impl

def get_handlers(op):
    if op.kind in _handlers:
        return _handlers[op.kind]
    return []