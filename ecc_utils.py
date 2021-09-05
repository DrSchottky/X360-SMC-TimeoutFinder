import sys
import struct

def calcecc(data):
	assert len(data) == 0x210
	val = 0
	for i in range(0x1066):
		if not i & 31:
			v = ~struct.unpack("<L", data[i//8:i//8+4])[0]
		val ^= v & 1
		v >>= 1
		if val & 1:
			val ^= 0x6954559
		val >>= 1

	val = ~val
	return data[:-4] + struct.pack("<L", (val << 6) & 0xFFFFFFFF)

def addecc(data, block = 0, off_8 = b"\x00" * 4):
	res = b""
	while len(data):
		d = (data[:0x200] + b"\x00" * 0x200)[:0x200]
		data = data[0x200:]
		
		d += struct.pack("<L4B4s4s", block // 32, 0, 0xFF, 0, 0, off_8, b"\0\0\0\0")
		d = calcecc(d)
		block += 1
		res += d
	return res

def unecc(image):
    res = b""
    for s in range(0, len(image), 528):
        res += image[s:s+512]
    return res

def help():
    print("Usage: {} [-u][-e] file".format(sys.argv[0]))

def main():
    if len(sys.argv) < 3:
        help()
        return

    with open(sys.argv[2], "rb") as f:
	    image = f.read()

    if sys.argv[1] == "-u":
        image = unecc(image)
        with open(sys.argv[2]+".unecc", "wb") as f:
	        f.write(image)
    elif sys.argv[1] == "-e":
        image = addecc(image)
        with open(sys.argv[2]+".ecc", "wb") as f:
            f.write(image)
    else:
        help()
        return

if __name__ == "__main__":
    main()