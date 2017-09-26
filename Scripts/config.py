from pynput.keyboard import Key # don't remove this

# Changes mouse position offset since rift controllers feel more comfortable pointing at a lower angle
# May change more settings in future if needed
HEADSET = "RIFT"
#HEADSET = "VIVE"

VERSION="1.12"

# in degrees, angle of screen in virtual desktop
SCREEN_ANGLE=120

# If you look down, you can see your body
SEE_YOURSELF = True

# Distance at which camera teleports to you in stationary camera mode
MAX_CAMERA_DIST = 15

# max speed of camera while in free look mode
FREE_LOOK_SPEED = 10

# Value of the WoW camera FOV address. Default (after Vanilla) = ~1.95. Same as FOVfix
FOV=2.3

# Character height offset (may want to change depending on race to match the height of your character model)
PLAYER_HEIGHT = 1.75

# Latency in Virtual Desktop (ms) - not used atm
HMD_LATENCY = 0.022

# for some reason pitch seemed slightly off to me
# may just have been angle I use the headset at or something
PITCH_OFFSET = 0.06

# Controller keyboard mappings
left_mapping = {"x_left": "q",
                "x_right": "e",
                "y_up": "w",
                "y_down": "s",
                "stick_thresh": 0.5,
                "a": [Key.alt_r],
                "b": [Key.esc],
                "trigger": "LEFT_CLICK",
                "touchpad": [Key.alt_l,"z"], # hide interface
                "grip": Key.shift}
right_mapping = {"x_left": "4",
                "x_right": "2",
                "y_up": "1",
                "y_down": "3",
                "stick_thresh": 0.5,
                "a": " ",
                "b": "b",
                "touchpad": "", # I have this one reserved for toggling camera
                "trigger": "RIGHT_CLICK",
                "grip": Key.ctrl}

