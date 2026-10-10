# Juice Shop

# Enumeration

## Nmap [juice-shop.herokuapp.com](https://juice-shop.herokuapp.com/)

```jsx
$ nmap -T5 -sC -sV -Pn juice-shop.herokuapp.com                                                                                                              
Starting Nmap 7.94SVN ( https://nmap.org ) at 2026-04-17 12:53 CEST                                                                                           
Nmap scan report for juice-shop.herokuapp.com (54.220.192.176)                                                                                                
Host is up (0.067s latency).                                                                                                                                  
Other addresses for juice-shop.herokuapp.com (not scanned): 46.137.15.86 54.73.53.134                                                                         
rDNS record for 54.220.192.176: ec2-54-220-192-176.eu-west-1.compute.amazonaws.com                                                                            
Not shown: 998 filtered tcp ports (no-response)                                                                                                               
PORT    STATE SERVICE   VERSION                                                                                                                               
80/tcp  open  http      heroku-router                                                                                                                         
| http-server-header:                                                                                                                                         
|   Heroku                                                                                                                                                    
|_  heroku-router                                                                                                                                             
|_http-cors: HEAD GET POST PUT DELETE PATCH                                                                                                                   
| fingerprint-strings:                                                                                                                                        
|   FourOhFourRequest:                                                                                                                                        
|     HTTP/1.0 400 Bad Request                                                                                                                                
|     Cache-Control: no-cache, no-store                                                                                                                       
|     Content-Type: text/html; charset=utf-8                                                                                                                  
|     Date: 2026-04-17 10:53:45.546948665 +0000 UTC                                                                                                           
|     Server: heroku-router                                                                                                                                   
|     Content-Length: 0                                                                                                                                       
|   GetRequest:                                                                                                                                               
|     HTTP/1.0 400 Bad Request                                                                                                                                
|     Cache-Control: no-cache, no-store                                                                                                                       
|     Content-Type: text/html; charset=utf-8                                                                                                                  
|     Date: 2026-04-17 10:53:34.936671488 +0000 UTC                                                                                                           
|     Server: heroku-router                                                                                                                                   
|     Content-Length: 0                                                                                                                                       
|   HTTPOptions:                                                                                                                                              
|     HTTP/1.0 400 Bad Request                                                                                                                                
|     Cache-Control: no-cache, no-store                                                                                                                       
|     Content-Type: text/html; charset=utf-8                                                                                                                  
|     Date: 2026-04-17 10:53:35.232023086 +0000 UTC                                                                                                           
|     Server: heroku-router                                                                                                                                   
|_    Content-Length: 0                                                                                                        
|_http-title: OWASP Juice Shop    
                                                                                                                                                                                      
443/tcp open  ssl/https heroku-router                                                                                          
|_http-cors: HEAD GET POST PUT DELETE PATCH                                                                                    
| http-robots.txt: 1 disallowed entry                                                                                          
|_/ftp                                 
| http-server-header:                  
|   Heroku                             
|_  heroku-router                      
|_http-title: OWASP Juice Shop         
| fingerprint-strings:                 
|   FourOhFourRequest:                 
|     HTTP/1.0 400 Bad Request         
|     Cache-Control: no-cache, no-store                                        
|     Content-Type: text/html; charset=utf-8                                   
|     Date: 2026-04-17 10:53:46.433180679 +0000 UTC                            
|     Server: heroku-router            
|     Content-Length: 0                
|   GetRequest:                        
|     HTTP/1.0 400 Bad Request         
|     Cache-Control: no-cache, no-store                                        
|     Content-Type: text/html; charset=utf-8                                   
|     Date: 2026-04-17 10:53:41.39074013 +0000 UTC                             
|     Server: heroku-router            
|     Content-Length: 0                
|   HTTPOptions:                       
|     HTTP/1.0 400 Bad Request         
|     Cache-Control: no-cache, no-store                                        
|     Content-Type: text/html; charset=utf-8                                   
|     Date: 2026-04-17 10:53:44.11029603 +0000 UTC                             
|     Server: heroku-router            
|_    Content-Length: 0                
| ssl-cert: Subject: commonName=*.herokuapp.com                                
| Subject Alternative Name: DNS:*.herokuapp.com                                
| Not valid before: 2026-01-01T00:00:00                                        
|_Not valid after:  2027-01-29T23:59:59                                        
|_ssl-date: TLS randomness does not represent time                             
```

## Enumerating port 433 (https)

![Screenshot from 2026-04-17 14-29-36.png](Juice%20Shop/Screenshot_from_2026-04-17_14-29-36.png)

## Fuff:

```jsx
$ ffuf -w SecLists/Discovery/Web-Content/directory-list-2.3-big.txt -u https://juice-shop.herokuapp.com/FUZZ -e .php -fs 75002
media                   [Status: 301, Size: 155, Words: 6, Lines: 11, Duration: 68ms]
profile                 [Status: 500, Size: 1036, Words: 153, Lines: 50, Duration: 144ms]
video                   [Status: 200, Size: 10075518, Words: 0, Lines: 0, Duration: 0ms]
assets                  [Status: 301, Size: 156, Words: 6, Lines: 11, Duration: 106ms]
redirect                [Status: 500, Size: 2959, Words: 244, Lines: 50, Duration: 944ms]
ftp                     [Status: 200, Size: 11308, Words: 1579, Lines: 358, Duration: 341ms]
api.php                 [Status: 500, Size: 2865, Words: 235, Lines: 50, Duration: 142ms]
api                     [Status: 500, Size: 2857, Words: 235, Lines: 50, Duration: 142ms]
channel.php             [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 6188ms]
spanish                 [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 6177ms]
spanish.php             [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 6118ms]
include                 [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 6139ms]
include.php             [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 8688ms]
win.php                 [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 7142ms]
cp                      [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 7137ms]
Video                   [Status: 200, Size: 10075518, Words: 0, Lines: 0, Duration: 0ms]
tp.php                  [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 2046ms]
atom03                  [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 2046ms]
atom03.php              [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 2046ms]
icon2.php               [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 2046ms]
icon2                   [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 2046ms]
extra                   [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 2030ms]
88x31                   [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 2029ms]
extra.php               [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 2029ms]
88x31.php               [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 7376ms]
ma                      [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 7351ms]
ma.php                  [Status: 200, Size: 0, Words: 1, Lines: 1, Duration: 7350ms]
```

## Looking at the functionality of the website

### I found a login page

![Screenshot from 2026-04-17 14-29-51.png](Juice%20Shop/Screenshot_from_2026-04-17_14-29-51.png)

### Also found that the email is @juice-sh.op

![Screenshot from 2026-04-17 14-31-07.png](Juice%20Shop/Screenshot_from_2026-04-17_14-31-07.png)

![Screenshot from 2026-04-17 14-31-19.png](Juice%20Shop/Screenshot_from_2026-04-17_14-31-19.png)

![Screenshot from 2026-04-17 14-31-33.png](Juice%20Shop/Screenshot_from_2026-04-17_14-31-33.png)

## Using SqlMap to see if it is vuln.

We try the `admin@juice-sh.op`

### Using Caido to see the request and to make the SqlMap synatx.

![Screenshot from 2026-04-17 14-35-33.png](Juice%20Shop/Screenshot_from_2026-04-17_14-35-33.png)

There is sql injection and we can log in into the admin page.

`admin@juice-sh.op' or 1=1 --`

![Screenshot from 2026-04-17 14-42-33.png](Juice%20Shop/Screenshot_from_2026-04-17_14-42-33.png)

# I used some online websites as well to see what else is going wrong.

## Security Headers:

![screencapture-securityheaders-2026-04-17-12_49_30.png](Juice%20Shop/screencapture-securityheaders-2026-04-17-12_49_30.png)

## Qualys SSL Labs:

![screencapture-ssllabs-ssltest-analyze-html-2026-04-17-12_54_50.png](Juice%20Shop/screencapture-ssllabs-ssltest-analyze-html-2026-04-17-12_54_50.png)

## Issues

```jsx
Content-Security-Policy	-> Content Security Policy is an effective measure to protect your site from XSS attacks. By whitelisting sources of approved content, you can prevent the browser from loading malicious assets.

Referrer-Policy	Referrer -> Policy is a new header that allows a site to control how much information the browser includes with navigations away from a document and should be set by all sites.

Permissions-Policy	     -> Permissions Policy is a new header that allows a site to control which features and APIs can be used in the browser.
```

Better that http. Less issues.