---
title: "SSH key-based authentication in Windows 10 (using no password)"
date: 2020-11-01
---

I found this solution somewhere online. Thanks a lot for that! Just adding this to my own “docs base” for personal future reference.

Working with Linux/UNIX machines, I rely a lot on SSH. Thus, not having to type passwords each time I open a new session is a great plus. Achieving this on Linux systems is trivial, since you have the ssh-copy-id command at hand. But, on Windows, that’s missing. Luckily, there is a (logical) way around that, instead of adding keys by hand in the remote server’s authorized_keys file (like I used to do). Below you can see how a new RSA key is generated and then copied to the remote host using a one-liner:
```
PS C:\Users\drago> ssh-keygen.exe -t rsa
Enter file in which to save the key (C:\Users\drago/.ssh/id_rsa):
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in C:\Users\drago/.ssh/id_rsa.
Your public key has been saved in C:\Users\drago/.ssh/id_rsa.pub.
The key fingerprint is:
SHA256:9IHYvsX6pbpS9Fwuq3j648ceNN7pH5MFEt8n0y9O6Jk drago@DESKTOP-KDTKFHA
The key's randomart image is:
+---[RSA 2048]----+
|            .    |
|       o .   o o |
|      . + . . = +|
|       o.o ..o +o|
|       .So*o. o o|
|        .*++.* + |
|       .o.ooE =  |
|      ..o.+=   o |
|      o**B+ ...  |
+----[SHA256]-----+
```
Once the key has been generated, copy it to the remote server. Use your current credentials (```user@server```). You will be asked to type the password once.
```
PS C:\Users\drago> type $env:USERPROFILE\.ssh\id_rsa.pub | ssh user@myserver "cat >> .ssh/authorized_keys"
user@myserver's password:
```
And that’s it. Now, each time you ssh to that server (using the specified account), you will be directly logged in, without any other password prompts.