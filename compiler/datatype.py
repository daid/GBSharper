

class DataType:
    __slots__ = 'type', 'size', 'my_pointer'

    INT = 0
    POINTER = 1
    def __init__(self, my_type, size):
        self.type = my_type
        self.size = size
        self.my_pointer = None
    
    def __repr__(self):
        if self.type == self.INT:
            return f"u{self.size}"
        raise RuntimeError()


DEFAULT_TYPE = DataType(DataType.INT, 8)
BASE_TYPES = {
    "u8": DEFAULT_TYPE,
}
