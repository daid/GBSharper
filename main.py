from compiler import Compiler


def main(filename):
    c = Compiler()
    c.add_file(filename)
    c.build()

if __name__ == "__main__":
    main("code.sharp")
