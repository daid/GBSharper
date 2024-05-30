from compiler.compiler import Compiler


def main(filename):
    c = Compiler()
    c.add_file(filename)
    c.dump_ast()
    rom, symbols = c.build(print_asm_code=True)
    open("rom.gb", "wb").write(rom)


if __name__ == "__main__":
    main("code.sharp")
