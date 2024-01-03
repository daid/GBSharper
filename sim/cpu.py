
class CPU:
    def __init__(self):
        self.A = 0
        self.B = 0
        self.C = 0
        self.D = 0
        self.E = 0
        self.H = 0
        self.L = 0
        self.PC = 0
        self.SP = 0
        self.flagZ = False
        self.flagN = False
        self.flagH = False
        self.flagC = False
        self.ime = False

        self.opcode = [None] * 0x100
        for n in range(0x100):
            if hasattr(self, f"instr{n:02X}"):
                self.opcode[n] = getattr(self, f"instr{n:02X}")
            #else:
            #    print(f"Missing instruction: {n:02X}")

    def read(self, addr):
        raise NotImplementedError()

    def write(self, addr, value):
        raise NotImplementedError()

    def on_halt(self):
        pass

    def step(self):
        self.opcode[self.pc_read_inc()]()

    def pc_read_inc(self):
        ret = self.read(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        return ret

    def pc_read16_inc(self):
        ret = self.pc_read_inc()
        ret |= self.pc_read_inc() << 8
        return ret

    @property
    def BC(self):
        return (self.B << 8) | self.C
    @BC.setter
    def BC(self, value):
        self.B = value >> 8
        self.C = value & 0xFF

    @property
    def DE(self):
        return (self.D << 8) | self.E
    @DE.setter
    def DE(self, value):
        self.D = value >> 8
        self.E = value & 0xFF

    @property
    def HL(self):
        return (self.H << 8) | self.L
    @HL.setter
    def HL(self, value):
        self.H = value >> 8
        self.L = value & 0xFF

    def instr00(self):
        pass
    def instr10(self): # STOP
        self.pc_read_inc() # ignore one byte on the stop instruction.
    def instr20(self):
        if not self.flagZ:
            self.instr18()
        else:
            self.pc_read_inc()
    def instr30(self):
        if not self.flagC:
            self.instr18()
        else:
            self.pc_read_inc()

    def instr01(self):
        self.C = self.pc_read_inc()
        self.B = self.pc_read_inc()
    def instr11(self):
        self.E = self.pc_read_inc()
        self.D = self.pc_read_inc()
    def instr21(self):
        self.L = self.pc_read_inc()
        self.H = self.pc_read_inc()
    def instr31(self):
        self.SP = self.pc_read_inc()
        self.SP |= self.pc_read_inc() << 8

    def instr02(self):
        self.write(self.BC, self.A)
    def instr12(self):
        self.write(self.DE, self.A)
    def instr22(self):
        self.write(self.HL, self.A)
        self.HL = (self.HL + 1) & 0xFFFF
    def instr32(self):
        self.write(self.HL, self.A)
        self.HL = (self.HL - 1) & 0xFFFF

    def instr03(self):
        self.BC = (self.BC + 1) & 0xFFFF
    def instr13(self):
        self.DE = (self.DE + 1) & 0xFFFF
    def instr23(self):
        self.HL = (self.HL + 1) & 0xFFFF
    def instr33(self):
        self.SP = (self.SP + 1) & 0xFFFF

    def instr04(self):
        self.B = self.inc8(self.B)
    def instr14(self):
        self.D = self.inc8(self.D)
    def instr24(self):
        self.H = self.inc8(self.H)
    def instr34(self):
        self.write(self.HL, self.inc8(self.read(self.HL)))

    def instr05(self):
        self.B = self.dec8(self.B)
    def instr15(self):
        self.D = self.dec8(self.D)
    def instr25(self):
        self.H = self.dec8(self.H)
    def instr35(self):
        self.write(self.HL, self.dec8(self.read(self.HL)))

    def instr06(self):
        self.B = self.pc_read_inc()
    def instr16(self):
        self.D = self.pc_read_inc()
    def instr26(self):
        self.H = self.pc_read_inc()
    def instr36(self):
        self.write(self.HL, self.pc_read_inc())

    def instr07(self): #RLCA
        self.flagC = (self.A & 0x80) == 0x80
        self.A = ((self.A << 1) | (self.A >> 7)) & 0xFF
        self.flagZ = False
        self.flagN = False
        self.flagH = False
    def instr17(self): #RLA
        a = self.A
        self.A = (self.A << 1) & 0xFF
        if self.flagC:
            self.A |= 0x01
        self.flagZ = False
        self.flagN = False
        self.flagH = False
        self.flagC = (a & 0x80) == 0x80
    def instr27(self): #DAA
        if not self.flagN:
            if self.flagC or self.A > 0x99:
                self.A = (self.A + 0x60) & 0xFF
                self.flagC = True
            if self.flagH or (self.A & 0x0F) > 0x09:
                self.A = (self.A + 0x06) & 0xFF
                self.flagH = False
        elif self.flagC and self.flagH:
            self.A = (self.A + 0x9A) & 0xFF
            self.flagH = False
        elif self.flagC:
            self.A = (self.A + 0xA0) & 0xFF
        elif self.flagH:
            self.A = (self.A + 0xFA) & 0xFF
            self.flagH = False
        self.flagZ = self.A == 0
    def instr37(self):
        self.flagN = False
        self.flagH = False
        self.flagC = True

    def instr08(self):
        addr = self.pc_read16_inc()
        self.write(addr, self.SP & 0xFF)
        self.write(addr + 1, self.SP >> 8)
    def instr18(self):
        offset = self.pc_read_inc()
        if offset & 0x80:
            offset -= 0x100
        self.PC = (self.PC + offset) & 0xFFFF
    def instr28(self):
        if self.flagZ:
            self.instr18()
        else:
            self.pc_read_inc()
    def instr38(self):
        if self.flagC:
            self.instr18()
        else:
            self.pc_read_inc()

    def instr09(self):
        self.HL = self.add16(self.HL, self.BC)
    def instr19(self):
        self.HL = self.add16(self.HL, self.DE)
    def instr29(self):
        self.HL = self.add16(self.HL, self.HL)
    def instr39(self):
        self.HL = self.add16(self.HL, self.SP)

    def instr0A(self):
        self.A = self.read(self.BC)
    def instr1A(self):
        self.A = self.read(self.DE)
    def instr2A(self):
        self.A = self.read(self.HL)
        self.HL = (self.HL + 1) & 0xFFFF
    def instr3A(self):
        self.A = self.read(self.HL)
        self.HL = (self.HL - 1) & 0xFFFF

    def instr0B(self):
        self.BC = self.dec16(self.BC)
    def instr1B(self):
        self.DE = self.dec16(self.DE)
    def instr2B(self):
        self.HL = self.dec16(self.HL)
    def instr3B(self):
        self.SP = self.dec16(self.SP)

    def instr0C(self):
        self.C = self.inc8(self.C)
    def instr1C(self):
        self.E = self.inc8(self.E)
    def instr2C(self):
        self.L = self.inc8(self.L)
    def instr3C(self):
        self.A = self.inc8(self.A)

    def instr0D(self):
        self.C = self.dec8(self.C)
    def instr1D(self):
        self.E = self.dec8(self.E)
    def instr2D(self):
        self.L = self.dec8(self.L)
    def instr3D(self):
        self.A = self.dec8(self.A)

    def instr0E(self):
        self.C = self.pc_read_inc()
    def instr1E(self):
        self.E = self.pc_read_inc()
    def instr2E(self):
        self.L = self.pc_read_inc()
    def instr3E(self):
        self.A = self.pc_read_inc()

    def instr0F(self): # RRCA
        a = self.A
        self.A = ((a >> 1) | (a << 7)) & 0xFF
        self.flagZ = False
        self.flagN = False
        self.flagH = False
        self.flagC = (a & 0x01) == 0x01
    def instr1F(self): # RRA
        a = self.A
        self.A = a >> 1
        if self.flagC:
            self.A |= 0x80
        self.flagZ = False
        self.flagN = False
        self.flagH = False
        self.flagC = (a & 0x01) == 0x01
    def instr2F(self):
        self.A = self.A ^ 0xFF
        self.flagN = True
        self.flagH = True
    def instr3F(self):
        self.flagN = False
        self.flagH = False
        self.flagC = not self.flagC

    def instr40(self):
        self.B = self.B
    def instr50(self):
        self.D = self.B
    def instr60(self):
        self.H = self.B
    def instr70(self):
        self.write(self.HL, self.B)

    def instr41(self):
        self.B = self.C
    def instr51(self):
        self.D = self.C
    def instr61(self):
        self.H = self.C
    def instr71(self):
        self.write(self.HL, self.C)

    def instr42(self):
        self.B = self.D
    def instr52(self):
        self.D = self.D
    def instr62(self):
        self.H = self.D
    def instr72(self):
        self.write(self.HL, self.D)

    def instr43(self):
        self.B = self.E
    def instr53(self):
        self.D = self.E
    def instr63(self):
        self.H = self.E
    def instr73(self):
        self.write(self.HL, self.E)

    def instr44(self):
        self.B = self.H
    def instr54(self):
        self.D = self.H
    def instr64(self):
        self.H = self.H
    def instr74(self):
        self.write(self.HL, self.H)

    def instr45(self):
        self.B = self.L
    def instr55(self):
        self.D = self.L
    def instr65(self):
        self.H = self.L
    def instr75(self):
        self.write(self.HL, self.L)

    def instr46(self):
        self.B = self.read(self.HL)
    def instr56(self):
        self.D = self.read(self.HL)
    def instr66(self):
        self.H = self.read(self.HL)
    def instr76(self):
        self.on_halt()

    def instr47(self):
        self.B = self.A
    def instr57(self):
        self.D = self.A
    def instr67(self):
        self.H = self.A
    def instr77(self):
        self.write(self.HL, self.A)

    def instr48(self):
        self.C = self.B
    def instr58(self):
        self.E = self.B
    def instr68(self):
        self.L = self.B
    def instr78(self):
        self.A = self.B

    def instr49(self):
        self.C = self.C
    def instr59(self):
        self.E = self.C
    def instr69(self):
        self.L = self.C
    def instr79(self):
        self.A = self.C

    def instr4A(self):
        self.C = self.D
    def instr5A(self):
        self.E = self.D
    def instr6A(self):
        self.L = self.D
    def instr7A(self):
        self.A = self.D

    def instr4B(self):
        self.C = self.E
    def instr5B(self):
        self.E = self.E
    def instr6B(self):
        self.L = self.E
    def instr7B(self):
        self.A = self.E

    def instr4C(self):
        self.C = self.H
    def instr5C(self):
        self.E = self.H
    def instr6C(self):
        self.L = self.H
    def instr7C(self):
        self.A = self.H

    def instr4D(self):
        self.C = self.L
    def instr5D(self):
        self.E = self.L
    def instr6D(self):
        self.L = self.L
    def instr7D(self):
        self.A = self.L

    def instr4E(self):
        self.C = self.read(self.HL)
    def instr5E(self):
        self.E = self.read(self.HL)
    def instr6E(self):
        self.L = self.read(self.HL)
    def instr7E(self):
        self.A = self.read(self.HL)

    def instr4F(self):
        self.C = self.A
    def instr5F(self):
        self.E = self.A
    def instr6F(self):
        self.L = self.A
    def instr7F(self):
        self.A = self.A

    def instr80(self):
        self.A = self.add8(self.A, self.B)
    def instr81(self):
        self.A = self.add8(self.A, self.C)
    def instr82(self):
        self.A = self.add8(self.A, self.D)
    def instr83(self):
        self.A = self.add8(self.A, self.E)
    def instr84(self):
        self.A = self.add8(self.A, self.H)
    def instr85(self):
        self.A = self.add8(self.A, self.L)
    def instr86(self):
        self.A = self.add8(self.A, self.read(self.HL))
    def instr87(self):
        self.A = self.add8(self.A, self.A)

    def instr88(self):
        self.A = self.adc8(self.A, self.B)
    def instr89(self):
        self.A = self.adc8(self.A, self.C)
    def instr8A(self):
        self.A = self.adc8(self.A, self.D)
    def instr8B(self):
        self.A = self.adc8(self.A, self.E)
    def instr8C(self):
        self.A = self.adc8(self.A, self.H)
    def instr8D(self):
        self.A = self.adc8(self.A, self.L)
    def instr8E(self):
        self.A = self.adc8(self.A, self.read(self.HL))
    def instr8F(self):
        self.A = self.adc8(self.A, self.A)

    def instr90(self):
        self.A = self.sub8(self.A, self.B)
    def instr91(self):
        self.A = self.sub8(self.A, self.C)
    def instr92(self):
        self.A = self.sub8(self.A, self.D)
    def instr93(self):
        self.A = self.sub8(self.A, self.E)
    def instr94(self):
        self.A = self.sub8(self.A, self.H)
    def instr95(self):
        self.A = self.sub8(self.A, self.L)
    def instr96(self):
        self.A = self.sub8(self.A, self.read(self.HL))
    def instr97(self):
        self.A = self.sub8(self.A, self.A)

    def instr98(self):
        self.A = self.sbc8(self.A, self.B)
    def instr99(self):
        self.A = self.sbc8(self.A, self.C)
    def instr9A(self):
        self.A = self.sbc8(self.A, self.D)
    def instr9B(self):
        self.A = self.sbc8(self.A, self.E)
    def instr9C(self):
        self.A = self.sbc8(self.A, self.H)
    def instr9D(self):
        self.A = self.sbc8(self.A, self.L)
    def instr9E(self):
        self.A = self.sbc8(self.A, self.read(self.HL))
    def instr9F(self):
        self.A = self.sbc8(self.A, self.A)

    def instrA0(self):
        self.A = self.and8(self.A, self.B)
    def instrA1(self):
        self.A = self.and8(self.A, self.C)
    def instrA2(self):
        self.A = self.and8(self.A, self.D)
    def instrA3(self):
        self.A = self.and8(self.A, self.E)
    def instrA4(self):
        self.A = self.and8(self.A, self.H)
    def instrA5(self):
        self.A = self.and8(self.A, self.L)
    def instrA6(self):
        self.A = self.and8(self.A, self.read(self.HL))
    def instrA7(self):
        self.A = self.and8(self.A, self.A)

    def instrA8(self):
        self.A = self.xor8(self.A, self.B)
    def instrA9(self):
        self.A = self.xor8(self.A, self.C)
    def instrAA(self):
        self.A = self.xor8(self.A, self.D)
    def instrAB(self):
        self.A = self.xor8(self.A, self.E)
    def instrAC(self):
        self.A = self.xor8(self.A, self.H)
    def instrAD(self):
        self.A = self.xor8(self.A, self.L)
    def instrAE(self):
        self.A = self.xor8(self.A, self.read(self.HL))
    def instrAF(self):
        self.A = self.xor8(self.A, self.A)

    def instrB0(self):
        self.A = self.or8(self.A, self.B)
    def instrB1(self):
        self.A = self.or8(self.A, self.C)
    def instrB2(self):
        self.A = self.or8(self.A, self.D)
    def instrB3(self):
        self.A = self.or8(self.A, self.E)
    def instrB4(self):
        self.A = self.or8(self.A, self.H)
    def instrB5(self):
        self.A = self.or8(self.A, self.L)
    def instrB6(self):
        self.A = self.or8(self.A, self.read(self.HL))
    def instrB7(self):
        self.A = self.or8(self.A, self.A)

    def instrB8(self):
        self.sub8(self.A, self.B)
    def instrB9(self):
        self.sub8(self.A, self.C)
    def instrBA(self):
        self.sub8(self.A, self.D)
    def instrBB(self):
        self.sub8(self.A, self.E)
    def instrBC(self):
        self.sub8(self.A, self.H)
    def instrBD(self):
        self.sub8(self.A, self.L)
    def instrBE(self):
        self.sub8(self.A, self.read(self.HL))
    def instrBF(self):
        self.sub8(self.A, self.A)

    def instrC0(self):
        if not self.flagZ:
            self.instrC9()
    def instrD0(self):
        if not self.flagC:
            self.instrC9()
    def instrE0(self):
        self.write(0xFF00 + self.pc_read_inc(), self.A)
    def instrF0(self):
        self.A = self.read(0xFF00 + self.pc_read_inc())

    def instrC1(self):
        self.BC = self.pop()
    def instrD1(self):
        self.DE = self.pop()
    def instrE1(self):
        self.HL = self.pop()
    def instrF1(self):
        v = self.pop()
        self.A = v >> 8
        self.flagZ = (v & 0x80) == 0x80
        self.flagN = (v & 0x40) == 0x40
        self.flagH = (v & 0x20) == 0x20
        self.flagC = (v & 0x10) == 0x10

    def instrC2(self):
        if not self.flagZ:
            self.instrC3()
        else:
            self.pc_read16_inc()
    def instrD2(self):
        if not self.flagC:
            self.instrC3()
        else:
            self.pc_read16_inc()
    def instrE2(self):
        self.write(0xFF00 + self.C, self.A)
    def instrF2(self):
        self.A = self.read(0xFF00 + self.C)

    def instrC3(self):
        self.PC = self.pc_read16_inc()
    # instrD3
    # instrE3
    def instrF3(self):
        self.ime = False

    def instrC4(self):
        if not self.flagZ:
            self.instrCD()
        else:
            self.pc_read16_inc()
    def instrD4(self):
        if not self.flagC:
            self.instrCD()
        else:
            self.pc_read16_inc()
    # instrE3
    # instrF3

    def instrC5(self):
        self.push(self.BC)
    def instrD5(self):
        self.push(self.DE)
    def instrE5(self):
        self.push(self.HL)
    def instrF5(self):
        value = self.A << 8
        if self.flagZ:
            value |= 0x80
        if self.flagN:
            value |= 0x40
        if self.flagH:
            value |= 0x20
        if self.flagC:
            value |= 0x10
        self.push(value)

    def instrC6(self):
        self.A = self.add8(self.A, self.pc_read_inc())
    def instrD6(self):
        self.A = self.sub8(self.A, self.pc_read_inc())
    def instrE6(self):
        self.A = self.and8(self.A, self.pc_read_inc())
    def instrF6(self):
        self.A = self.or8(self.A, self.pc_read_inc())

    def instrC7(self):
        self.call(0x00)
    def instrD7(self):
        self.call(0x10)
    def instrE7(self):
        self.call(0x20)
    def instrF7(self):
        self.call(0x30)

    def instrC8(self):
        if self.flagZ:
            self.instrC9()
    def instrD8(self):
        if self.flagC:
            self.instrC9()
    def instrE8(self):
        n = self.pc_read_inc()
        if n & 0x80:
            n -= 0x100
        tmp = self.SP ^ n ^ (self.SP + n)
        self.SP = (self.SP + n) & 0xFFFF
        self.flagZ = False
        self.flagH = (tmp & 0x10) == 0x10
        self.flagN = False
        self.flagC = (tmp & 0x100) == 0x100
    def instrF8(self):
        n = self.pc_read_inc()
        if n & 0x80:
            n -= 0x100
        tmp = self.SP ^ n ^ (self.SP + n)
        self.HL = (self.SP + n) & 0xFFFF
        self.flagZ = False
        self.flagH = (tmp & 0x10) == 0x10
        self.flagN = False
        self.flagC = (tmp & 0x100) == 0x100

    def instrC9(self):
        self.PC = self.pop()
    def instrD9(self):
        self.ime = True
        self.instrC9()
    def instrE9(self):
        self.PC = self.HL
    def instrF9(self):
        self.SP = self.HL

    def instrCA(self):
        if self.flagZ:
            self.instrC3()
        else:
            self.pc_read16_inc()
    def instrDA(self):
        if self.flagC:
            self.instrC3()
        else:
            self.pc_read16_inc()
    def instrEA(self):
        self.write(self.pc_read16_inc(), self.A)
    def instrFA(self):
        self.A = self.read(self.pc_read16_inc())

    def instrCB(self):
        opcode = self.pc_read_inc()
        if opcode < 0x40:
            op = opcode & 0xF8
            if op == 0x00:
                f = self.rlc8
            if op == 0x08:
                f = self.rrc8
            if op == 0x10:
                f = self.rl8
            if op == 0x18:
                f = self.rr8
            if op == 0x20:
                f = self.sla8
            if op == 0x28:
                f = self.sra8
            if op == 0x30:
                f = self.swap8
            if op == 0x38:
                f = self.srl8
        else:
            bit = 1 << ((opcode >> 3) & 7)
            op = opcode & 0xC0
            if op == 0x40:
                f = lambda n: self.instrBit(n, bit)
            if op == 0x80:
                f = lambda n: self.instrRes(n, bit)
            if op == 0xC0:
                f = lambda n: self.instrSet(n, bit)
        op = opcode & 0x07
        if op == 0:
            self.B = f(self.B)
        if op == 1:
            self.C = f(self.C)
        if op == 2:
            self.D = f(self.D)
        if op == 3:
            self.E = f(self.E)
        if op == 4:
            self.H = f(self.H)
        if op == 5:
            self.L = f(self.L)
        if op == 6:
            self.write(self.HL, f(self.read(self.HL)))
        if op == 7:
            self.A = f(self.A)

    # instrDB
    # instrEB
    def instrFB(self):
        self.ime = True

    def instrCC(self):
        if self.flagZ:
            self.instrCD()
        else:
            self.pc_read16_inc()
    def instrDC(self):
        if self.flagC:
            self.instrCD()
        else:
            self.pc_read16_inc()
    # instrEC
    # instrFC

    def instrCD(self):
        self.call(self.pc_read16_inc())
    # instrDD
    # instrED
    # instrFD

    def instrCE(self):
        self.A = self.adc8(self.A, self.pc_read_inc())
    def instrDE(self):
        self.A = self.sbc8(self.A, self.pc_read_inc())
    def instrEE(self):
        self.A = self.xor8(self.A, self.pc_read_inc())
    def instrFE(self):
        self.sub8(self.A, self.pc_read_inc())

    def instrCF(self):
        self.call(0x08)
    def instrDF(self):
        self.call(0x18)
    def instrEF(self):
        self.call(0x28)
    def instrFF(self):
        self.call(0x38)

    def call(self, addr):
        self.push(self.PC)
        self.PC = addr

    def push(self, value):
        self.write((self.SP - 1) & 0xFFFF, value >> 8)
        self.write((self.SP - 2) & 0xFFFF, value & 0xFF)
        self.SP = (self.SP - 2) & 0xFFFF

    def pop(self):
        value = self.read(self.SP) | (self.read((self.SP + 1) & 0xFFFF) << 8)
        self.SP = (self.SP + 2) & 0xFFFF
        return value

    def add8(self, a, b):
        res = (a + b) & 0xFF
        self.flagZ = res == 0
        self.flagN = False
        self.flagH = (res & 0x0F) < (a & 0x0F)
        self.flagC = a + b > 0xFF
        return res

    def adc8(self, a, b):
        res = (a + b) & 0xFF
        if self.flagC:
            res = (a + b + 1) & 0xFF
            self.flagH = (res & 0x0F) < ((a & 0x0F) + 1)
            self.flagC = a + b > 0xFE
        else:
            res = (a + b) & 0xFF
            self.flagH = (res & 0x0F) < (a & 0x0F)
            self.flagC = a + b > 0xFF
        self.flagZ = res == 0
        self.flagN = False
        return res

    def sub8(self, a, b):
        res = (a - b) & 0xFF
        self.flagZ = res == 0
        self.flagN = True
        self.flagH = (res & 0x0F) > (a & 0x0F)
        self.flagC = a < b
        return res

    def sbc8(self, a, b):
        res = a - b
        if self.flagC:
            res -= 1
        self.flagZ = (res & 0xFF) == 0
        self.flagN = True
        if self.flagC:
            self.flagH = (res & 0x0F) >= (a & 0x0F)
        else:
            self.flagH = (res & 0x0F) > (a & 0x0F)
        self.flagC = res < 0
        return res & 0xFF

    def and8(self, a, b):
        res = a & b
        self.flagZ = res == 0
        self.flagN = False
        self.flagH = True
        self.flagC = False
        return res

    def or8(self, a, b):
        res = a | b
        self.flagZ = res == 0
        self.flagN = False
        self.flagH = False
        self.flagC = False
        return res

    def xor8(self, a, b):
        res = a ^ b
        self.flagZ = res == 0
        self.flagN = False
        self.flagH = False
        self.flagC = False
        return res

    def inc8(self, a):
        res = (a + 1) & 0xFF
        self.flagZ = res == 0
        self.flagN = False
        self.flagH = (res & 0x0F) == 0
        return res

    def dec8(self, a):
        res = (a - 1) & 0xFF
        self.flagZ = res == 0
        self.flagN = True
        self.flagH = (res & 0x0F) == 0x0F
        return res

    def srl8(self, a):
        res = a >> 1
        self.flagC = (a & 1) == 1
        self.flagN = False
        self.flagH = False
        self.flagZ = res == 0
        return res

    def rr8(self, a):
        res = a >> 1
        if self.flagC:
            res |= 0x80
        self.flagC = (a & 1) == 1
        self.flagN = False
        self.flagH = False
        self.flagZ = res == 0
        return res

    def sla8(self, a):
        res = (a << 1) & 0xFF
        self.flagC = (a & 0x80) == 0x80
        self.flagN = False
        self.flagH = False
        self.flagZ = res == 0
        return res

    def sra8(self, a):
        res = (a >> 1) | (a & 0x80)
        self.flagC = (a & 0x01) == 0x01
        self.flagN = False
        self.flagH = False
        self.flagZ = res == 0
        return res

    def swap8(self, a):
        self.flagZ = a == 0
        self.flagN = False
        self.flagH = False
        self.flagC = False
        return (a >> 4) | ((a << 4) & 0xF0)

    def rlc8(self, a):
        self.flagZ = a == 0
        self.flagN = False
        self.flagH = False
        self.flagC = (a & 0x80) == 0x80
        return ((a << 1) | (a >> 7)) & 0xFF

    def rrc8(self, a):
        self.flagZ = a == 0
        self.flagN = False
        self.flagH = False
        self.flagC = (a & 0x01) == 0x01
        return ((a >> 1) | (a << 7)) & 0xFF

    def rl8(self, a):
        res = (a << 1) & 0xFF
        if self.flagC:
            res |= 0x01
        self.flagZ = res == 0
        self.flagN = False
        self.flagH = False
        self.flagC = (a & 0x80) == 0x80
        return res

    def rr8(self, a):
        res = (a >> 1) & 0xFF
        if self.flagC:
            res |= 0x80
        self.flagZ = res == 0
        self.flagN = False
        self.flagH = False
        self.flagC = (a & 0x01) == 0x01
        return res

    def instrBit(self, a, b):
        self.flagZ = (a & b) != b
        self.flagN = False
        self.flagH = True
        return a

    def instrRes(self, a, b):
        return a & ~b

    def instrSet(self, a, b):
        return a | b

    def add16(self, a, b):
        res = a + b
        self.flagH = (a & 0xFFF) > (res & 0xFFF)
        self.flagN = False
        self.flagC = res > 0xFFFF
        return res & 0xFFFF

    def dec16(self, a):
        return (a - 1) & 0xFFFF
