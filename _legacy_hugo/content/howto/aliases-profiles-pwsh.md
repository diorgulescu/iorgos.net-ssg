---
title: "Aliases & Profiles in PowerShell"
date: 2021-02-12
draft: false
---

Coming from a Linux background, I found myself looking for a way to define aliases in PowerShell. You know, like one does in bash, sh and the likes. PowerShell is one environment I believe people should understand and know how to use, at least at the bare functional level. It really does not matter if you prefer to use bash or tchor other UNIX CLIs. The truth is we live & work in mixed environments and it’s worth knowing how to orient yourself in a “mixed situation”.

So, the first thing I had to do was to find out where my profile file is, because the path provided by the official PowerShell online help had nothing to do with the real world.

```powershell
PS C:\Users\drago> $PROFILE
C:\Users\drago\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
```

Yes, I used OneDrive on that Windows 10 machine. And yes, I have chocolatey installed, thus making it trivial to add other tools I love, like vim. So, I went on to edit my profile:

```powershell
PS C:\Users\drago> vim C:\Users\drago\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
```

Even though PowerShell does provide the Set-Alias cmdlet, that won’t help you if you’re trying to make an alias for an SSH command, for example. Passing command arguments in an alias does not work as it does on Bash or others. Therefore, I had to define a simple function with the name of my alias, adding the SSH command in its body. This would generally look like this:

```powershell
function wackyserver {ssh "dragos@wackyserver"}
```

So, I did that. Then saved the file and spawned a new PowerShell session, which greeted me with the following error:

```text
. : File C:\Users\drago\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1 
cannot be    loaded. The file C:\Users\drago\OneDrive\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1 
is not digitally signed. You cannot run this script on the current system. 
For more information about running scripts and setting execution policy, see about_Execution_Policies 
at https:/go.microsoft.com/fwlink/?LinkID=135170.
At line:1 char:3
. 'C:\Users\drago\OneDrive\Documents\WindowsPowerShell\Microsoft.Powe ...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
CategoryInfo          : SecurityError: (:) [], PSSecurityException
FullyQualifiedErrorId : UnauthorizedAccess
PS C:\Users\drago>
```

Bonkers! In order to fix this, I realised PowerShell did not trust local scripts (happened to me in the past). So, I needed to make PowerShell trust and execute local scripts, but not remote ones (just for the sake of not going “Unrestricted”). So, opened up a new PowerShell session as Administrator and issued:

```powershell
PS C:\Windows\system32> Set-ExecutionPolicy RemoteSigned
```

Press “A” when asked:

```text
Execution Policy Change
The execution policy helps protect you from scripts that you do not trust. 
Changing the execution policy might expose you to the security risks described in the 
about_Execution_Policies help topic at https:/go.microsoft.com/fwlink/?LinkID=135170. 
Do you want to change the execution policy?
[Y] Yes  [A] Yes to All  [N] No  [L] No to All  [S] Suspend  [?] Help (default is "N"): A
```

And that’s about it. Now I was free to add & customize my PowerShell profile. Joy!
