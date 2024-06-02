

_handlers = {}

def handler(size: int, main_op, *ops, priority=50):
    def impl(f):
        if size not in _handlers:
            _handlers[size] = {}
        if main_op not in _handlers[size]:
            _handlers[size][main_op] = []
        f.size = size
        f.priority = priority
        f.ops = ops
        _handlers[size][main_op].append(f)
        _handlers[size][main_op].sort(key=lambda n: (-len(n.ops), n.priority))
        return f
    return impl

def get_handlers(op):
    if op.size in _handlers and op.kind in _handlers[op.size]:
        return _handlers[op.size][op.kind]
    return []