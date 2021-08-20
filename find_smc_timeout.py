import sys
import os

if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
    print("Usage: {} smc.bin".format(sys.argv[0]))
    sys.exit(1)

with open(sys.argv[1], "rb") as f:
    SMC = f.read()
if len(SMC) != 0x3000 and len(SMC) != 0x3800:
    print("Not a valid SMC file")
    sys.exit(1)

console_types = ["none/unk", "Xenon", "Zephyr", "Falcon", "Jasper", "Trinity", "Corona", "Winchester"]
smctype = (SMC[0x100] >> 4) & 0xF
smcver = "{}.{}".format(SMC[0x101], SMC[0x102])

print("Checking {} SMC version {}\n".format(console_types[smctype], smcver))

found = False
for i in range(0, len(SMC) - 6):
    if SMC[i] == 0xd5 and SMC[i+1] == SMC[i+4] and SMC[i+3] == 0x75 and SMC[i+4] & 0xf0 == 0x30 and SMC[i+6] == 0x80:
        found = True
        val = SMC[i+5]
        seq = SMC[i+3:i+6]

if not found:
    for i in range(0, len(SMC) - 6):
        if SMC[i] == 0x12 and SMC[i+1] == 0x00 and SMC[i+3] == 0x75 and SMC[i+4] & 0xf0 == 0x30 and SMC[i+5] > 0x10 and SMC[i+6] == 0x80:
            found = True
            val = SMC[i+5]
            seq = SMC[i+3:i+7]

if not found:
    print("Sorry, can't find the reset timeout")
    sys.exit(1)

print("Default timer value is 0x{:02x}".format(val))

for i in range(0, len(SMC) - len(seq)):
    if SMC[i:i + len(seq)] == seq:
        print("Found timeout occurrence at 0x{:02X}".format(i+2))