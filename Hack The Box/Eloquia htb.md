# Eloquia.htb

# Enumeration

```jsx
$ nmap -T5 -sC -sV -Pn 10.10.11.99                                                              
Starting Nmap 7.95 ( https://nmap.org ) at 2025-12-18 11:54 EST                                   
Nmap scan report for eloquia.htb (10.10.11.99)                                                    
Host is up (0.24s latency).                                                                       
Not shown: 998 filtered tcp ports (no-response)                                                   
PORT     STATE SERVICE VERSION
80/tcp   open  http    Microsoft IIS httpd 10.0
|_http-title: Eloquia
|_http-server-header: Microsoft-IIS/10.0
5985/tcp open  http    Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
$ nmap -T5 -sC -sV -Pn 10.10.11.99                                                              
Starting Nmap 7.95 ( https://nmap.org ) at 2025-12-18 11:54 EST                                   
Nmap scan report for eloquia.htb (10.10.11.99)                                                    
Host is up (0.24s latency).                                                                       
Not shown: 998 filtered tcp ports (no-response)                                                   
PORT     STATE SERVICE VERSION
80/tcp   open  http    Microsoft IIS httpd 10.0
|_http-title: Eloquia
|_http-server-header: Microsoft-IIS/10.0
5985/tcp open  http    Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-title: Not Found
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows

```

# Web

![Screenshot From 2025-12-18 11-57-21.png](Eloquia%20htb/Screenshot_From_2025-12-18_11-57-21.png)

```jsx
		vs:MariaMaria1
		
		found: support@eloquia.htb
```

### No vhosts.