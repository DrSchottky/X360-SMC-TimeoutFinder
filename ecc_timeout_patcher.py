import sys
from find_smc_timeout import find_offsets
import struct
import ecc_utils

def decrypt_SMC(SMC):
	key = [0x42, 0x75, 0x4e, 0x79]
	res = b""
	for i in range(len(SMC)):
		j = SMC[i]
		mod = j * 0xFB
		res += bytes([j ^ (key[i&3] & 0xFF)])
		key[(i+1)&3] += mod
		key[(i+2)&3] += mod >> 8
	return res

def encrypt_SMC(SMC):
	key = [0x42, 0x75, 0x4e, 0x79]
	res = b""
	for i in range(len(SMC)):
		j = SMC[i] ^ (key[i&3] & 0xFF)
		mod = j * 0xFB
		res += bytes([j])
		key[(i+1)&3] += mod
		key[(i+2)&3] += mod >> 8
	return res


with open(sys.argv[1], "rb") as f:
	image = f.read()

image = ecc_utils.unecc(image)

(smc_len, smc_start) = struct.unpack(">LL", image[0x78:0x80])
SMC_enc = image[smc_start:smc_start+smc_len]
SMC = decrypt_SMC(SMC_enc)
timeout_offsets = find_offsets(SMC)
for offset in timeout_offsets:
        print("Found timeout occurrence at 0x{:02X}".format(offset))
new_timeout = input("\nInsert new hex value for timeout:")
try:
	new_timeout = int(new_timeout, 16)
except:
	print("Invalid input")
	sys.exit(1)

for offset in timeout_offsets:
	SMC = SMC[:offset] + bytes([new_timeout]) + SMC[offset+1:]

SMC_enc = encrypt_SMC(SMC)
image = image[:smc_start] + SMC_enc + image[smc_start+smc_len:]
print("Rebuilding ECC")
image = ecc_utils.addecc(image)
with open(sys.argv[1]+".patched", "wb") as f:
	f.write(image)
print("Done! Outupt saved in {}".format(sys.argv[1]+".patched"))
