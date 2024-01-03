from compiler.compiler import Compiler


def main(filename):
    c = Compiler()
    c.add_file(filename)
    rom = c.build()
    open("rom.gb", "wb").write(rom)

if __name__ == "__main__":
    main("code.sharp")
