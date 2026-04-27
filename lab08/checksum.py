def calculate_checksum(bytes):
    if len(bytes) % 2 == 1:
        bytes += b"\x00"

    total = 0

    for index in range(0, len(bytes), 2):
        total += (bytes[index] << 8) + bytes[index + 1]
        total = (total & 0xFFFF) + (total >> 16)

    return (~total) & 0xFFFF


def verify_checksum(bytes, checksum):
    if len(bytes) % 2 == 1:
        bytes += b"\x00"

    total = checksum

    for index in range(0, len(bytes), 2):
        total += (bytes[index] << 8) + bytes[index + 1]
        total = (total & 0xFFFF) + (total >> 16)

    return (total == 0xFFFF)