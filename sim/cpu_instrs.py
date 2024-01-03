from cpu import CPU
import sys


class TestCPU(CPU):
    def __init__(self):
        super().__init__()
        self.PC = 0x100
        self.A = 0x11
        self.BC = 0x0013
        self.DE = 0x00d8
        self.HL = 0x014d
        self.SP = 0xfffe
        self.flagZ = True
        self.flagN = False
        self.flagH = True
        self.flagC = True
        self.rom = open("cpu_instrs.gb", "rb").read()
        self.ram = bytearray(0x8000)
        self.ram[0xFF44 - 0x8000] = 144

        self.rombank = 1

    def read(self, addr):
        if addr < 0x4000:
            return self.rom[addr]
        if addr < 0x8000:
            return self.rom[(addr & 0x3FFF) + self.rombank * 0x4000]
        return self.ram[addr - 0x8000]

    def write(self, addr, value):
        #if addr == 0xDD02:
        #    print(f"Write: {addr:04x}:{value:02x} PC: {self.PC:04x}")
        if addr == 0x2000:
            self.rombank = value if value != 0 else 1
        if addr < 0x8000:
        #    print(f"Write: {addr:04x}:{value:02x} PC: {self.PC:04x}")
            return
        if addr == 0xFF4D:
            value = 0x80 if self.ram[addr - 0x8000] == 0 else 0x00
        self.ram[addr - 0x8000] = value
        if addr == 0xFF01:
            sys.stderr.write(chr(value))
            sys.stderr.flush()


cpu = TestCPU()
while True:
    #print(f"{cpu.rombank:02x}:{cpu.PC:04x} {cpu.read(cpu.PC):02x} {cpu.read(cpu.PC+1):02x} {cpu.read(cpu.PC+2):02x} SP:{cpu.SP:04x} A:{cpu.A:02x} BC:{cpu.BC:04x} DE:{cpu.DE:04x} HL:{cpu.HL:04x} F:{'Z' if cpu.flagZ else ' '}{'N' if cpu.flagN else ' '}{'H' if cpu.flagH else ' '}{'C' if cpu.flagC else ' '}")
    #if cpu.read(cpu.PC) == 0 and cpu.PC != 0x0100:
    #    break
    cpu.step()
