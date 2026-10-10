import hashlib
from sympy import nextprime
from Crypto.PublicKey import RSA

TARGET_PUBKEY = """-----BEGIN PUBLIC KEY-----
MFswDQYJKoZIhvcNAQEBBQADSgAwRwJAANsfcIiUKqEx+CXxxhgKts+0y5kLf/v5
qk0c/DWCXmi2c/OJ8OoQIPqP+qKtamxMZPThF7rZc8yAN3F0dLyolQIDAQAB
-----END PUBLIC KEY-----"""

target_n = RSA.import_key(TARGET_PUBKEY).n

def derive_key(username):
    seed = f"{username}_lovenote_2026_valentine".encode()
    p = nextprime(int(hashlib.sha256(seed).hexdigest(), 16))
    q = nextprime(int(hashlib.sha256(seed + b"pki").hexdigest(), 16))
    return p, q, p * q

candidates = [
    # From the bank binary
    "admin", "support", "contact", "cyber", "admins", "sam",
    "admin0", "super_user", "control_admin", "it_admin",
    # Common guesses
    "administrator", "root", "cupid", "valenfind", "user", "guest",
    # Email-style
    "admin@bank.a", "support@bank.a",
]

print(f"[*] Target modulus n: {hex(target_n)}\n")

for username in candidates:
    p, q, n = derive_key(username)
    status = "MATCH" if n == target_n else "no match"
    marker = "<<<" if n == target_n else ""
    print(f"[{status}] {username} {marker}")
    if n == target_n:
        print(f"\n[+] p = {p}")
        print(f"[+] q = {q}")
        print(f"[+] n = {n}")

        # Reconstruct full private key
        e = 65537
        phi = (p - 1) * (q - 1)
        d = pow(e, -1, phi)
        key = RSA.construct((n, e, d, p, q))
        print("\n[+] Reconstructed private key:")
        print(key.export_key().decode())
        break
