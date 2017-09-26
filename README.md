# WoW-VR-mod
A shoddily-put-together World of Warcraft VR mod for private servers

## Description
This is a tool to add headtracking with OpenVR for World of Warcraft private servers. It is intended to be used with TriDef and Virtual Desktop. Versions 1.12.1, 2.4.3 and 3.3.5 of the WoW client are supported. Warning: this is not a polished VR experience - you will probably get motion sick from some functions, and there are still some bugs. For the most part, it works ok. Cheat Engine and a python script are used to edit the game's memory to add headtracking. There is some judder when moving the headset due to the very hacky nature of this method, unfortunately. I am not sure how to solve this.

Features:
- First person view mode
- Google Earth VR style free camera for exploring
- Third person mode
- Keybindings and mouse emulation for VR controllers

## Requirements and Installation
- [Tridef 3d](https://www.tridef.com/cart/product.php?productid=3). You could technically use this without TriDef, but it would be a pirate simulator.
- [Virtual Desktop steam version](http://store.steampowered.com/app/382110/Virtual_Desktop/)
- Python 2.7 64 bit
- The following Python packages:
  - psutil
  - openvr
  - memorpy
  - pynput
  - numpy
  - pypiwin32
These can be installed by running in the command line in the installation directory:
```
pip install -r requirements.txt
```
- I use Cheat Engine to disable the default camera movement of the game. Cheat Engine installation is not required, but if you don't trust random executables off the internet, you can create the files yourself in Cheat Engine using the AutoAssemble scripts provided.
- A supported old WoW client version and a private server account. Disclaimer: I have tested this on a few servers (including Elysium) and have not been banned, but this is an executable modification and so is probably against most servers' TOS.
- For best results you should set your monitor to a custom 5:4 or 4:3 resolution (eg. 1280x1024 for a 1080p monitor). A high framerate monitor is also best so that you get at least 90 fps capture rate.

## Usage
You can run this script using
```
python Scripts/wowvr.py
```
You can just make a shortcut to the provided run.bat file and it should hopefully work. You might have to run as administrator, I haven't really checked.
Launch WoW using TriDef 3d ignition so that it renders in stereo 3d. You can use the default World of Warcraft profile. Some settings that I found work alright:
- TriDef -> 3D (in-game settings)
  - Scene Depth = 30
  - Percent In Front = 20
  - Custom Focus = On
  - Near Plane = 91
  - Far Plane = 100
- Config.wtf:
  - SET nearClip "0.10"
- WoW settings:
  - Camera Following Style = Never
- Virtual Desktop
  - Screen angle 120 degrees
  - no curvature
  - Vive/touch controllers deactivated (doesn't handle head lock mode correctly so I do it)
- config.py
  - FOV=2.3

But suggestions for better settings are welcome. There is also a setting is config.py "PITCH_OFFSET" since the in-game world seemed slightly off to me. This may be incorrect and I just have the headset at a weird angle, I don't know.
Virtual Desktop must be launched using OpenVR. If you have an Oculus Rift, you will need to add the launch parameter "-ForceOpenVR" in Steam. Then to launch correctly, you must open Oculus Home, then launch Virtual Desktop. Do not start SteamVR manually - I found this buggy. Set Virtual Desktop to "Head lock, no delay" mode with Half SBS 3D active (F7) (**required**).

Once you have logged in in-game and the script is running, all you have to do is tab in to the game and then realise you didn't customise your keybinds or interface for VR yet.

## Controls
Keybinds and additional settings are in Scripts/config.py. Customise them to your liking. By default, they are (on Touch controllers):
### Right controller:
- A: Spacebar (Jump)
- B: B (open inventory)
- Trigger: Right click
- Grip: Ctrl
- Stick: Up, Right, Down, Left = 1,2,3,4
- Stick button: Toggle movement mode
### Left controller:
- X: alt
- Y: escape (this resets position in Virtual Desktop)
- Trigger: Left click
- Grip: Shift
- Stick: Up, Right, Down, Left = wdsa. It is also assumed for movement that AD = turn and QE = strafe.
- Stick button: alt-z (toggle hide interface)

There are three camera control modes (toggle between them using right controller stick/pad button):
- First person
  - Room centre will follow your character's position. Character will be transparent while standing near the centre. Moving away will make your character visible so you can 'mire them. Seeing yourself when you look down is also an option.
  - Left stick (WSQE) for movement, character will face the same way as you do (while in centre of room), but movement direction only changes when stationary so you can look around while moving.
- Free look
  - Can move around like in Google Earth VR with the left stick
- Third Person
  - Camera will teleport towards your character when they get a certain distance away (in Config.py).
  - WASD movement, no strafing
  - Height relative to player preserved from Free Look mode

The hotkey to disable headtracking for cheat engine is Ctrl-F1.

## Interface Recommendations
WIP (Other than Move Anything, I need recommendations)
## Issues
- Different addresses for camera positions are used while on transports (elevators, boats, zeppelins). Be prepared to be a bit disoriented.
- I'm not sure if mounts are visible in first person
WIP
