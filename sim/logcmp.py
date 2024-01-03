a = open("log.txt", "rt")
b = open("../BadBoy/emulator/_build/log.txt", "rt")

history = []
while True:
    aa = a.readline()
    bb = b.readline()
    if aa != bb:
        for n in history:
            print(" " + n)
        print("-" + aa.strip())
        print("+" + bb.strip())
        break
    history.append(aa.strip())
    if len(history) > 10:
        history.pop(0)
