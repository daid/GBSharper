from cpu import CPU


class TestCPU(CPU):
    def __init__(self, rom):
        super().__init__()
        self.rom = rom
        self.vram0 = bytearray(0x2000)
        self.vram1 = bytearray(0x2000)
        self.sram = bytearray(0x2000)
        self.wram = bytearray(0x2000)
        self.hram = bytearray(0x7F)
        self.rombank = 1
        self.VBK = False
        self.PC = 0x100

    def read(self, addr):
        if addr < 0x4000:
            return self.rom[addr]
        if addr < 0x8000:
            return self.rom[(addr & 0x3FFF) + self.rombank * 0x4000]
        if addr < 0xA000:
            if self.VBK:
                return self.vram1[addr & 0x1FFF]
            else:
                return self.vram0[addr & 0x1FFF]
        if addr < 0xC000:
            return self.sram[addr & 0x1FFF]
        if addr < 0xE000:
            return self.wram[addr & 0x1FFF]
        if addr < 0xFF80:
            return 0xFF
        if addr < 0xFFFF:
            return self.hram[addr & 0x7F]
        return 0xFF

    def write(self, addr, value):
        if addr < 0x2000:
            return # sram enable
        if addr < 0x4000:
            self.rombank = value
            return
        if addr < 0x6000:
            return # sram bank
        if addr < 0x8000:
            return
        if addr < 0xA000:
            if self.VBK:
                self.vram1[addr & 0x1FFF] = value
            else:
                self.vram0[addr & 0x1FFF] = value
            return
        if addr < 0xC000:
            self.sram[addr & 0x1FFF] = value
            return
        if addr < 0xE000:
            self.wram[addr & 0x1FFF] = value
            return
        if addr < 0xFF80:
            if addr == 0xFF01:
                print(chr(value), end='')
            return
        if addr < 0xFFFF:
            self.hram[addr & 0x7F] = value
            return
