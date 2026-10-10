import hashlib
from sympy import nextprime
from Crypto.PublicKey import RSA

username = "admin"
seed = f"{username}_lovenote_2026_valentine".encode()

p = nextprime(int(hashlib.sha256(seed).hexdigest(), 16))
q = nextprime(int(hashlib.sha256(seed + b"pki").hexdigest(), 16))
n = p * q
e = 65537
d = pow(e, -1, (p-1)*(q-1))

key = RSA.construct((n, e, d, p, q))

print("=== PRIVATE KEY ===")
print(key.export_key().decode())
print()
print("=== PUBLIC KEY ===")
print(key.publickey().export_key().decode())
