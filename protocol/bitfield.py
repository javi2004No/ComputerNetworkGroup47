def bitfield_to_bytes(bitfield):
    byte_array = bytearray()
    for i in range(0, len(bitfield), 8):
        byte = 0
        for j in range(8):
            if i + j < len(bitfield) and bitfield[i + j] == 1:
                byte |= 1 << (7 - j)
        byte_array.append(byte)
    return bytes(byte_array)


def bytes_to_bitfield(byte_data, total_pieces):
    bitfield = []
    for byte in byte_data:
        for i in range(8):
            if len(bitfield) < total_pieces:
                bitfield.append((byte >> (7 - i)) & 1)
    return bitfield
