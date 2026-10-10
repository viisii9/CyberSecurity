---
name: htb-reactor-progress
description: HackTheBox Reactor machine - progress, findings, and exploit details
metadata:
  type: project
---

# HTB Reactor Machine Progress

**IP:** 10.129.4.110
**Status:** User flag not yet captured (RCE achieved, need privesc to engineer)

## Confirmed Findings

### Open Ports
- 22/tcp SSH (OpenSSH 9.6p1 Ubuntu)
- 3000/tcp Next.js App Router web app (ReactorWatch v3.2.1)
- Several filtered ports: 1345, 25604, 32620, 57202, 64962

### CVE Exploited
CVE-2025-55182 ("React2Shell") — pre-auth RCE via RSC Flight protocol deserialization
- POST to `/` with `Next-Action: x` header
- Multipart form-data with crafted payload using `$@` self-reference + prototype chain traversal
- Working exploit: `/home/mari/CTF/HACKTHEBOX/Reactor/exploits/exploit.py`

### Shell Access
- Running as: `uid=999(node) gid=988(node)`
- No shell — using OOB HTTP exfil via Node.js `http.request()`

### Environment Variables (from server)
- DB_PATH=/opt/reactor-app/reactor.db (SQLite)
- SENSOR_API_KEY=rw_sk_7f8a9b2c3d4e5f6g7h8i9j0k
- PWD=/opt/reactor-app
- ALERT_WEBHOOK=https://alerts.internal.reactor.htb/webhook
- NODE_ENV=production

### Users on System
- engineer (home: /home/engineer, permission denied)
- node (home: /home/node, no user.txt)

### DB Tables
- users
- sensor_logs

### Next Steps
1. Query the users table with Node.js sqlite module (find better-sqlite3 path)
2. Crack any password hashes found
3. SSH as engineer with cracked password
4. Get user flag from /home/engineer/user.txt
5. Privesc to root

**Why:** engineer user has user.txt, node can't read /home/engineer/
**How to apply:** Continue from OOB exfil technique, query DB using correct sqlite3 module path
