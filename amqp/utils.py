
def hexdump(data, length=16):
    result = []
    for i in range(0, len(data), length):
        slice_ = data[i:i+length]
        hex_values = ' '.join(f'{byte:02x}' for byte in slice_)
        ascii_values = ''.join((chr(byte) if 32 <= byte <= 126 else '.') for byte in slice_)
        line = ('->' if i == 0 else '  ') + f' {hex_values:<{length*3}}  {ascii_values}'
        result.append(line)
    return '\n'.join(result)