from checksum import calculate_checksum, verify_checksum

def run_test(name, condition):
    if condition:
        print(f"{name}: OK")
    else:
        print(f"{name}: FAIL")


def main():
    data = b"hello world hi hello"
    checksum = calculate_checksum(data)
    run_test("Тест 1: корректные данные", verify_checksum(data, checksum))

    broken_data = bytearray(data)
    broken_data[1] = 0x00
    run_test("Тест 2: поврежденные данные", not verify_checksum(bytes(broken_data), checksum))

    wrong_checksum = checksum ^ 0x00FF
    run_test("Тест 3: поврежденная контрольная сумма", not verify_checksum(data, wrong_checksum))


if __name__ == "__main__":
    main()