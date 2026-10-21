---
title: "Deploying Microsoft Hyper-V Server 2019 without a Domain Controller"
date: 2021-05-20
draft: false
---

### Prerequisites

+ For fully managing the Hyper-V server remotely, you need to install Remote Server Administration Tools
+ Download the Hyper-V 2019 ISO from Microsoft
+ Rufus USB flashing tool
+ A decent PC LOL

### Installation

Well, not much to say here. Pretty straightforward, just like a normal Windows installation.

Once the ISO is downloaded, stick an USB stick into your PC and launch Rufus. Select the ISO file you’ve just downloaded, make sure the USB stick is selected and check that GPT is used. Reboot your server-to-be and select the USB drive as a boot option. Then, carry on as usual.

Easy-peasy lemon-squeezy!

### Enable Remote Hyper-V Management

This is strictly in regards to Hyper-V and it’s settings. For “full” remote server management, please see the section about using Remote Administration Tools/Server Manager. All commands are for Powershell, unless otherwise specified so. Make sure you run these in a Powershell session with administrative rights!

On The Server:

```
Enable-PSRemoting Enable-WSManCredSSP -Role server
```

On the client (my laptop in this case):

```
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "HYPERV-SERVER" Enable-WSManCredSSP -Role "Client" -DelegateComputer "HYPERV-SERVER"
```

Now, for me this did not seem to work at all, so I reissued the commands above, but with the IP address replacing the FQDN of the Hyper-V server:

```
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "192.168.1.6" Enable-WSManCredSSP -Role "Client" -DelegateComputer "192.168.1.6"
```

After that, it was required for me edit the Group Policies.

### Edit Group Policies

Again, following the official instructions from Microsoft proved to be insufficient, so I once again need to praise Taylord Tech, because he did encounter all these issues and pointed to a valuable tip.

Open **gpedit.msc** and go to **“Computer Configuration > Administrative Templates > System > Credentials Delegation”**. Double click **“Allow delegating fresh credentials with NTLM-only server authentication”** and select **“Enable”**. Then, Click **“Show”**, next to **“Add servers to the list”** and add **“WSMAN*“**. The official docs say one should add the FQDN of the server (**“WSMAN\HYPERV-SERVER” in my case**), but that didn’t work at all for me.

### Enable Remote Disk Management

I did not succeed in setting up remote disk management, even though I did follow some how-to’s/tutorials/links in the MS Docs. I issued the following PowerShell commands on both the server & the client, but with no luck:

```
Set-NetFirewallRule –Name “RVM-VDS-In-TCP” –Enabled True -Profile Any
Set-NetFirewallRule –Name “RVM-VDSLDR-In-TCP” –Enabled True -Profile Any
Set-NetFirewallRule –Name “RVM-RPCSS-In-TCP” –Enabled True -Profile Any
```

After installing Remote Server Administration Tools on my Windows 10 laptop, I couldn’t get the Server Manager to properly connect to the Hyper-V host. I have some things to learn, that’s true. The errors were in regards to HTTPS access, since my laptop & server are not part of a domain (I guess that has something to do with it).

But, for my needs, a simple Remote Desktop Connection was enough.

### Adding a new disk

I ran the ‘diskpart.exe’ tool from a simple command prompt (“cmd.exe”) and formatted the second SSD drive on my server (~500GB) and assigned it a drive letter:

```
c:\diskpart
DISKPART> list disk
Disk ###  Status         Size     Free     Dyn  Gpt
--------  -------------  -------  -------  ---  ---
Disk 0    Online          120 GB     0 B
Disk 1    Online          500 GB   200 GB
DISKPART> select disk 1
Disk 1 is now the selected disk.
DISKPART> create partition primary
DISKPART> list partition
DISKPART> select partition 1
DISKPART> format fs=NTFS quick
DISKPART> assign letter=D
```

### Copying files to the Hyper-V host

Now, I just needed a way to actually copy some ISO’s over to the server so that I could install various operating systems. Being in the context of a homelab, I resorted to file sharing (I even mapped the drive on which I keep my “ISO store”). For that, I issued the following from a Powershell instance on the Server:

```
netsh advfirewall firewall set rule group="File and Printer Sharing" new enable=Yes
```

Then, I mapped the C: drive on my server to Z: on my laptop. This way, I was able to copy all ISO files I would ever need (and not only that).

Right after that, I began installing my first VMs on my first homelab Hyper-V Server.

Yay me!

### References & Resources

+ https://docs.microsoft.com/en-us/windows-server/virtualization/hyper-v/manage/remotely-manage-hyper-v-hosts
+ https://www.youtube.com/watch?v=57Ijn7re8X8
+ https://social.technet.microsoft.com/Forums/office/en-US/cbdbcf92-d697-41d1-aa7a-bacf34bd48a5/remote-disk-management-rpc-server-unavailable
+ https://serverfault.com/questions/449192/server-2012-core-no-gui-how-to-manage-disks
+ http://technet.microsoft.com/en-us/library/cc770877.aspx
+ https://www.nakivo.com/blog/copy-iso-file-hyper-v-host/
