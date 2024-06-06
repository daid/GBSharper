

class DataType:
    __slots__ = 'type', 'size', 'my_pointer', 'target'

    INT = 0
    POINTER = 1
    def __init__(self, my_type, size):
        self.type = my_type
        self.size = size
        self.my_pointer = None
        self.target = None
    
    def get_pointer(self):
        if self.my_pointer is None:
            self.my_pointer = DataType(DataType.POINTER, 16)
            self.my_pointer.target = self
        return self.my_pointer
    
    def __repr__(self):
        if self.type == self.INT:
            return f"u{self.size}"
        elif self.type == self.POINTER:
            return f"{self.target}*"
        raise RuntimeError()


DEFAULT_TYPE = DataType(DataType.INT, 8)
BASE_TYPES = {
    "u8": DEFAULT_TYPE,
    "u16": DataType(DataType.INT, 16),
}
