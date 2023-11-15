def bytes_to_hex(buf):
    s=''
    for b in buf:
        s+=hex(int(b))[2:]
    return s

def device_id_compare(a:str, b:str) -> int:
    if a < b:
        return -1
    elif a > b:
        return 1
    else:
        return 0
