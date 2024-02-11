import hashlib
import struct

def bfi(int2, int1, skip, width):
    bins1 = bin(int1)[2:].zfill(32)
    bins1 = list(bins1)[::-1]
    bins2 = bin(int2)[2:].zfill(32)
    bins2 = list(bins2)[::-1]
    bins2[skip:skip+width] = bins1[:width]
    bins2 = ''.join(bins2[::-1])
    final = int(bins2, 2)
    return final

def tohex(i:str):
    # format int to %2x
    num = ord(i)
    return hex(num)[2:].zfill(2)

def get_gorgon_raw(url_params, ts=None):
    # md5 of url_params
    md5 = hashlib.md5()
    md5.update(url_params.encode())
    md5 = md5.digest()
    # turn md5 to hex string with \x
    md5 = md5.decode('latin')
    gorgon_raw = md5[0:4] + "\x00" * 8 + "\x20\x00\x05\x04"
    if not ts:
        ts = int(time.time())
    # turn ts to hex string with \x

    ts = hex(ts)[2:]
    ts = ts.zfill(8)
    ts = [ts[i:i+2] for i in range(0, len(ts), 2)]
    ts = [chr(int(i, 16)) for i in ts]
    ts = ''.join(ts)
    gorgon_raw += ts
    return gorgon_raw


#url_params = "aid=1233&source_type=0&group_id=40031_1699122162646"
#ts = 1699122271

url_params = "app_name=musical_ly&app_version=31.5.3&channel=googleplay&sdk_version=2.3.3.i1    8n&version_code=31.5.3&lang=en&aid=1233"
ts = 1702172429

rand1_gorgon7 = "\xe0"
rand2_gorgon3 = "\xdb"
seed1 = "\x00"
seed2 = "\x02"
#seed1 = "\x14"
#seed2 = "\x01"

# gorgon raw calculated from timestamp + md5 of url_params
#gorgon_raw = "\x5e\xc4\xe6\xaa\x00\x00\x00\x00\x00\x00\x00\x00\x20\x00\x05\x04\x65\x46\x8c\x5f"
gorgon_raw = get_gorgon_raw(url_params, ts)
gorgon_buf = "\x4a" + seed1 + "\x16" + rand2_gorgon3 + "\x47\x6c" + seed2 + rand1_gorgon7
gorgon_raw = [ord(g) for g in gorgon_raw]
gorgon_buf = [ord(g) for g in gorgon_buf]
gorgon_out = gorgon_raw.copy()
var_test = 0

state = []
final = []
for i in range(0x100):
    state.append(i)

w22 = 0
for i in range(0x100):
    w8 = state[i]
    x9 = i % 8
    w9 = gorgon_buf[x9]
    w8 += w22
    w8 += w9
    w9 = w8 // 0x100
    w22 = w8 - (w9 << 8)
    w26 = state[w22&0xff]
    w8 = i + 0x22
    w8 %= 0x100
    x20 = w22
    state[i] = w26
    state[x20&0xff] = w26

x23 = 0
w25 = 0
x21 = 0x14
w27 = x21
w26 = 0
while x23 < x21:
    w8 = w25 + 1
    w9 = w8 // 0x100
    w25 = w8 - (w9 << 8)
    w8 = state[w25]
    w8 += w26
    w9 = w8 // 0x100
    w26 = w8 - (w9 << 8)
    w8 = state[w26]
    state[w25] = w8
    state[w26] = w8
    w9 = state[w25]
    w10 = gorgon_out[x23]
    w8 += w9
    w8 %= 0x100
    w8 = state[w8]
    w8 ^= w10
    gorgon_out[x23] = w8
    x23 += 1

x8 = 0
w20 = 0xffffffeb
#x9 = w27 - 1
x9 = 0x13
w26 = 0x33
w28 = 1
w12 = 0x23
w13 = 0x1bd
w14 = 7
w15 = 0xFFFFFFAA
w16 = 0x55
gorgon_raw_var = x9
print(x21)
while x8 < x21:
    w11 = gorgon_out[x8]
    w25 = x8 + 1
    i = x8
    w8 = x8
    w9 = w11 >> 4
    w9 = bfi(w9, w11, 4, 8)
    gorgon_out[i] = w9 & 0xff
    if x21 <= w25:
        if w8 == 0: pass
        else:
            w10 = gorgon_raw_var
            if w10 != w8: pass
            else:
                w10 = gorgon_out[0]
                w9 ^= w10
                gorgon_out[i] = w9 & 0xff
    else:
        w9 = gorgon_out[i+1]
        w10 = gorgon_out[i]
        w9 ^= w10
        gorgon_out[i] = w9 & 0xff

    w8 = gorgon_out[i]
    w9 = w15 & (w8 << 1)
    w8 = w16 & (w8 >> 1)
    w8 |= w9
    w9 = w8 << 2
    w9 &= 0xFFFFFFCF
    w8 = w26 & (w8 >> 2)
    w8 |= w9
    # UBFX            W9, W8, #4, #4
    w9 = (w8 >> 4) & 0xf
    w9 = bfi(w9, w8, 4, 0x1c)
    w8 = w9 ^ w20
    gorgon_out[i] = w8 & 0xff
    x8 = w25

final = "".join([hex(i)[2:].zfill(2) for i in gorgon_out])
final = "8404" + tohex(rand1_gorgon7) + tohex(rand2_gorgon3) + tohex(seed1) + tohex(seed2) + final
print(final)

expect = "8404e0db00021c36d7e3c4ad8babb3446fd543bba303012c6107"
