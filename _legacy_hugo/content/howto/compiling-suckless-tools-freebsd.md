---
title: "Compiling ‘suckless tools’ on FreeBSD"
date: 2019-10-23
draft: false
---

I wrote this tutorial for potential new users that want to try out new stuff and wish to expand their technical knowledge, but also because there are some commands and details around here I might forget some months or years down the line (for example, Xorg video driver configurations). The whole writing process was a very good opportunity for me to extend the CSS I used for my website and to try do to a better job at formatting tech/code/console-related text. I would be glad if someone else found these instructions useful.

**⚠ WARNING This tutorial was written on October 23rd, 2019. I decided to keep it here for reference. Things potentially marked as „In progress”, „Not solved” or „Not working” (if any at a given time) may already have a workaround or a solution. Keep in mind that the exact instructions provided here may not be fully applicable to your system’s context!**

### Why bother?
Since most of these tools are already available in the FreeBSD package tree, why go through the hassle of building them yourself? Well, why bother with anything, really?

In my opinion, this is the only way you get to truly undestrand how these tools are built and how they interact with each other. There’s also a small chance you’ll get the hang of manually building software if you’re not used to it or never have done it before. Last,but not least, you get to customize each software piece. Since suckless tools rely on the user recompiling the source files in order to set various parameters, this is the way to do it. Finally, it’s a good first look at the (I would say) intentional philosophy behind these tools.

### Assumptions

+ First of all, you have a new, freshly installed FreeBSD system (version 12 being the latest stable one, at the time of writing). No X server, no pkg-config, etc. The following steps describe what one should to in order to get a fully functional suckless.org-based desktop (strange choice of words, I know).
+ Of course, a bit of experience working in a console is required. But why would you install FreeBSD otherwise?
+ Your user account has administrative privileges or is, at least, added to the /usr/local/etc/sudoers file
+ You have read about the tools developed by the people at suckless.org and their philosophy (if not, go do it now, because it won’t take long)
+ You understand that in order to change some configuration attributes, editing a C header file is mandatory. Luckily, this is just a formality and you don’t really need to know C in order to change some intuitive settings.

### General guidelines

Change X11INC and X11LIB paths in each & every config.mk file (each tool folder contains one such file). This is their FreeBSD-adjusted form:

        X11INC=/usr/local/include
        X11LIB=/usr/local/lib

Each software piece produced by the people at suckless.org relies on a config.h header file that lies in the main source folder, along with Makefile and all the rest. This file does not exist by default, but a template with default settings is available. So, do a quick $ cp config.def.h config.h for each tool you wish to setup.

### Preparations

To setup these tools, we need to install a few things first. Issue this command as root or with sudo privileges:

        $ pkg install git xorg-server xorg-fonts-truetype gcr devel/glib20 \ 
        xorg-fonts-type1 p5-X11-Xlib p5-PkgConfig xauth xrandr xinit libXft xrdb webkit2-gtk3 \
        feh xf86-input-mouse xf86-input-keyboard linux-c7-libpng

Good. Now, let’s take it step by step. In order to keep things organized, create a folder in your home directory where the sources will be stored. Then, proceed in fetching all the source files:

        $ mkdir ~/git
        $ cd git
        $ git clone git://git.suckless.org/dmenu
        $ git clone git://git.suckless.org/slstatus
        $ git clone git://git.suckless.org/st
        $ git clone git://git.suckless.org/dwm
        $ git clone git://git.suckless.org/sent
        $ git clone git://git.suckless.org/surf

Of course, there are more tools available (farbfeld, tabbed, slock, etc.), but these are not essential and will be covered in a separate post.TIP: st is an acronym for „suckless terminal”. It’s quite a simple terminal and some of the functionalities you might’ve found in xterm are missing (even scrolling). Of course, these can all be set by editing the config.h file, but if you want a quick alternative, go ahead and download Luke Smith’s build, which includes tweaks and additional settings that turn this into a more usable terminal emulator.

Now you are ready to start building.

### dmenu (a fast app „search & launch” thingy)

This is a nifty tool that allows you to search & execute programs installed on your system. By default, it uses a so-called „Mod key” in combination with „P”, but we’ll get to that later. In short: this is a must for convenience.

        $ cd dmenu
        $ cp config.def.h config.h
        $ vim config.h
        $ vim config.mk

#### config.mk

+ Set FREETYPEINC to /usr/local/include/freetype2
+ Update X11INC and X11LIB as shown in the Prerequisites section

#### config.h

Increase the font from 10 to 12 or more. This is for readability, but it’s a matter of taste and eyestrain: 
        static const char *fonts[] = {"monospace:size=12"}  
Now, build and install it: 
        $ make $ sudo make install 

### slstatus (a nice status bar)

Actually, a very nice and highly customizable status bar. Create the config.h file from the template and edit it.

        $ cd ../slstatus
        $ cp config.def.h config.h

#### config.h

Since there are quite a lot of available options, here’s how my file looks at the moment (for my laptop installation, that is):

        static const struct arg args[] = {
                /* function format          argument */
                { datetime, "%s",           "%F %T" },
                { cpu_perc, "[CPU %3s%%] ", NULL    },
                { ram_used, "[RAM %2s%%] ", NULL    },
                { battery_state, "[BAT %s", "BAT0" },
                { battery_perc, "%s%%] ", "BAT0" },
                { run_command, "[VOL %s%%] ", "/bin/sh -c \"amixer get Master | tail -n1 | grep -Po '\\[\\K[^%]*' | head -n1\"" },
                { ipv4, "[wlan0 %s] ", "wlan0" }
        };

All available options and attributes are listed in a long comment inside the original config.def.h file. Please do check them out!

#### config.mk

Update X-related variables (as previously shown)

#### Makefile

For some reason I still can’t grasp, the swap component causes a compilation error. Since I don’t find it useful, I choose to take it out of the build process. Just edit the Makefile and remove the following line:

        components/swap  \

Next, the usual:

        $ make
        $ sudo make install

### dwm (THE window manager)

Or the dynamic window manager. In my opinion, probably i3’s nemesis. A tiling window manager that’s very lightweight & fast. Very similar to i3 in some respects, but a bit different when it comes to how it’s being used (refer to the original docs for details). I admit that it might not seem very different to the average user, but the specifics come about after using it for at least a week.

        $ cd ../dwm
        $ cp config.def.h config.h

#### config.h

By default, the „modifier key” (the one used for all keyboard shortcuts) is Alt. If one wants to use the Win key, for example, the MODKEY must be redefined. Go to line 47 in config.h and change Mod1Mask to Mod4Mask (Mod1Mask for Alt). You should end up with: 
        #define MODKEY Mod4Mask 
dwm uses „st” implicitly when the user requests a new terminal window ($MODKEY + Shift + Enter). If another terminal emulator is desired, feel free to set it at line 60: 
        static const char *termcmd[] = {"xterm", NULL} 
I am not comfortable with small screen fonts, therefore I also change that at line 8: 
        static const char *fonts[] = {"monospace:size=12"} 

#### config.mk

Update freetype fonts path: 
        FREETYPEINC=/usr/local/include/freetype2

Next:
        $ sudo make clean install

### st („simple terminal”)

The people at suckless.org find xterm to be bloated and carrying a lot of „baggage” (code for interacting with systems that nowadays are pretty scarce). Therefore, they developed their own terminal emulator. A very basic one, which lacks some of the features I personally love about xterm and mrxvt (like scrolling and easy copy/pasting). Of course, it can be extended and tinkered by tackling the config.h file, but there is an alternative: Luke Smith’s st fork actually contains all these missing features. If you wish to use that instead, go ahead and clone his repo.

Because I like Luke’s fork, I am going to remove the original st I cloned at the very beginning and fetch that instead:

        $ cd ..
        $ rm -rf st/
        $ git clone https://github.com/LukeSmithxyz/st.git
        $ cd st

Of course, feel free to mess around with the config file if you wish.

In case you really want to use the original st repository, keep the current clone and remember to $ cp config.def.h config.h so you have a custom config file.

Some changes need to be made in order to successfully compile st on FreeBSD.

#### config.mk

Update X11INC & X11LIB paths as before:

        X11INC = /usr/local/include
        X11LIB = /usr/local/lib

Properly set PKG_CONFIG:

        PKG_CONFIG=/usr/local/bin/pkg-config

Once all settings are in place, build & install:

        $ sudo make clean install

### sent

It’s trendy to „go minimal” nowadays, but minimalism itself is not a new thing. Let’s face it: letting go of superficial content & eye-candy is the only way to actively focus on relevant issues and information. sent adheres to the Takahashi method by helping you create simple presentations that support you, the presenter.

During a corporate or technical presentation, the presenter needs to be the one people pay attention to, not the slides coming on & off the walls. Apart from some relevant screenshots or simple charts, concise textual information is the only thing that should reside in a presentation.

Just remember how many times you dozed-off during a boring but visually loaded presentation. Wouldn’t it be nicer if you could bravely show an alternative way of doing presentations? At least the more technical ones, which target tech people. You know, challenging the status-quo of MS PowerPoint.

#### config.mk

+ Update X-related paths as shown before
+ Change -I/usr/include/freetype2 to -I/usr/local/include/freetype2 in INCS

config.h is a good place to learn about all the available shortcuts and options.

Then,

        $ sudo make clean install

I intend to do a brief tutorial for this tool in the near future.

### surf

Talking about minimalism, here’s a Webkit-based browser that has no tabs or any other „bling”. Just the main window and a few shortcuts. It handles almost any common website very well, including HTML5, CSS3, JavaScript and the such. I admit this is the browser I use 99% of the time, except those moments when I must make sure some CSS changes in my website’s appearance work well on others, too.

It’s kind of tricky for someone that’s been using dozens of tabs & browser extensions, but I fancy it quite a lot. Maybe it is because using many tabs has a confusing effect on me, making me lose focus a lot easier. I remember a time when I started working on a Firefox extension that would deny the use of more than one tab :).

Anyway, I will come back to surf and „focused browsing” on another occasion.

This one is pretty straightforward, assuming you don’t want to tinker all options availabe in config.h:

        $ cd ../surf
        $ sudo make clean install

If all goes well, lauch it using something like surf https://duckduckgo.com. If you want to enter a different web address in the current window, use Ctrl + G and then just type it and hit Enter.TIP: Alternatively, you may use a fork of surf that improves usability by facilitating bookmarks and the use of WebKit Inspector (useful for web developers). If that sounds good, go ahead and

        $ rm -rf git/surf; git clone https://github.com/imiric/surf.git

### Xorg configuration

At this point, we have everything we need to start using our new „desktop UI”. In order to wrap this up, we need to make sure Xorg uses the appropriate display drivers and quickly set a couple other things. nVidia drivers ¶

I use a GeForce GT 430 on my desktop. Even though I knew the adapter was officially supported by the original nVidia driver for FreeBSD systems, I set things wrong the first time. So, here are the steps, in order:

Install the official nVidia driver (check the version you need, depending on your graphics card):

        $ sudo kldload linux64
        $ sudo pkg install nvidia-driver

Run sudo sysrc kld_list+="nvidia-modeset" Add the following to /boot/loader.conf:

        linux_load="YES"
        linux64_load="YES"

Create /usr/local/etc/X11/xorg.conf.d/driver-nvidia.conf and add populate it with the following:

        Section "Device"
                Identifier "NVIDIA Card"
                VendorName "NVIDIA Corporation"
                Driver "nvidia"
        EndSection

#### Intel integrated graphics

        sudo pkg install drm-kmod

Edit /etc/rc.conf and add:

        kld_list="/boot/modules/i915kms.ko"

#### Keyboard configuration

Create /usr/local/etc/X11/xorg.conf.d/kbd-layout-multi.conf and add:

        Section "InputClass"
                Identifier "All Keyboards"
                MatchIsKeyboard "yes"
                Option  "XkbLayout" "us, ro"
        EndSection

#### .xinitrc

Create .xinitrc in your $HOME and populate it accordingly:

        xrdb -load $HOME/.Xresources
        slstatus&
        exec dwm

#### .Xresources

Using your editor, create $HOME/.Xresources and add the following):

        ! Use a nice truetype font and size by default...
        xterm*faceName: DejaVu Sans Mono Book
        xterm*faceSize: 12

        ! Every shell is a login shell by default (for inclusion of all necessary environment variables)
        xterm*loginshell: true

        ! I like a LOT of scrollback...
        xterm*savelines: 16384

        ! double-click to select whole URLs 😀
        xterm*charClass: 33:48,36-47:48,58-59:48,61:48,63-64:48,95:48,126:48

        ! DOS-box colours...
        xterm*foreground: rgb:a8/a8/a8
        xterm*background: rgb:00/00/00
        xterm*color0: rgb:00/00/00
        xterm*color1: rgb:a8/00/00
        xterm*color2: rgb:00/a8/00
        xterm*color3: rgb:a8/54/00
        xterm*color4: rgb:00/00/a8
        xterm*color5: rgb:a8/00/a8
        xterm*color6: rgb:00/a8/a8
        xterm*color7: rgb:a8/a8/a8
        xterm*color8: rgb:54/54/54
        xterm*color9: rgb:fc/54/54
        xterm*color10: rgb:54/fc/54
        xterm*color11: rgb:fc/fc/54
        xterm*color12: rgb:54/54/fc
        xterm*color13: rgb:fc/54/fc
        xterm*color14: rgb:54/fc/fc
        xterm*color15: rgb:fc/fc/fc

        ! right hand side scrollbar...
        xterm*rightScrollBar: true
        xterm*ScrollBar: true

        ! stop output to terminal from jumping down to bottom of scroll again
        xterm*scrollTtyOutput: false

### Ready? Go!

The moment has come. Reboot your system to make sure all modules are loaded correctly.

Then:

        $ startx

That’s mainly it. I hope this was useful. The config files I use can be found in this repo.