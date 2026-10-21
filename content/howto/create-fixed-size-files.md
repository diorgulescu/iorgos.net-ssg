---
title: "Quickly creating fixed sized files in Linux & Windows"
date: 2021-03-24
draft: false
---

Often times, while working as a Software Test Engineer, I encountered situations in which the software I was testing relied a lot on available disk space. If that wasn’t the case, surely it had a way to upload files to it (either through a WEB-UI or by sending them over a certain network protocol). So, I was either going to make sure the device/machine that program ran on would end up without any available disk space at a given point in time, or try to crash the whole program by feeding it large dummy or random binary files.

However, for that to work quickly, I could not rely on an endless copy operation just for the sake of populating disk space. Especially if I wanted this to happen at a particular time during the run of an automated test case (i.e. triggering that programatically).

### On Linux

The ```dd``` and the newer fallocate commands are here to help.

```fallocate``` is available on newer systems, but if that is not your case, fear not, because ```dd``` does get you there.

You basically tell these to create a file of a certain size. The size itself may be expressed in a “human-friendly form”: 1G for 1 Gigabyte, 466M for 466 Megs, and so on (you get the idea).

So, here they are, in action.

#### Creating a 144 MB file
```
dragos@laptop:~$ dd if=/dev/zero of=test_dd.bin bs=144M count=1
1+0 records in
1+0 records out
150994944 bytes (151 MB, 144 MiB) copied, 0,130152 s, 1,2 GB/s
```
```
dragos@laptop:~$ fallocate -l 144M test_fallocate.img
```

#### Creating a 2.5 GB file (well, roughly; it’s best to specify the exact size in MBs):
```
dragos@laptop:~$ dd if=/dev/zero of=2.5_g.bin bs=2500M count=1
0+1 records in
0+1 records out
2147479552 bytes (2,1 GB, 2,0 GiB) copied, 1,68972 s, 1,3 GB/s
```
```
dragos@laptop:~$ fallocate -l 2500M test.img
```
### On Windows systems

Don’t generally disregard Windows. It does have its place & tools, and newer improvements and additions (Windows Terminal, PowerShell, Windows Subsystem for Linux) demonstrate the company is nowadays fully aware of the mixed environments businesses and people use on a daily basis.

A big thanks to Windows-CommandLine.com for the clear hints that enlightened me.

So, if you find yourself in a need to generate such files on Windows, fire up a Command Prompt (cmd.exe).

#### Create a dummy/sparse/empty file of a given size
```
fsutil file createnew test.txt 52428800
```
The above creates a 50 MB file. The size is always expressed in bytes.

#### Create a 128 MB file with real data:
```
echo "Sample text to create some big files." > dummy.txt
for /L %i in (1,1,21) do type dummy.txt >> dummy.txt
```
And the trick here is to increase the third value within the parenthesis. Each run, the file doubles itself in size.

That’s about it.
***
### TESTER’S TIP

You can easily script these commands in order to generate a “test bed” of variable-sized dummy files. These could be very useful for testing an FTP server, for example. Let’s say you wish to generate 50 files with sizes between 1KB and 366787K (just of the top of my head). It could very well be files between 1 MB & 500 MB, depending on your needs & plans.
***