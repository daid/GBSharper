
class Code:
    def __init__(self):
        self.code = ""
        self.addition = ""

    def comment(self, line):
        self.code += f"; {line}\n"

    def add(self, line):
        self.addition += line + "\n"

    def finish(self):
        self.code += self.addition
        self.addition = ""
