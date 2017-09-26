import os
import sys
import time
import openvr
import numpy as np
from wowmw import *
from keyboard_funcs import *
from openvr_funcs import *
from win32api import GetSystemMetrics
import win32security, win32api
import subprocess
from config import *



# Source: https://stackoverflow.com/questions/21401663/python-windows-api-dump-process-in-buffer-then-regex-search
def AdjustPrivilege( priv ):
    flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
    htoken =  win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)
    id = win32security.LookupPrivilegeValue(None, priv)
    newPrivileges = [(id, win32security.SE_PRIVILEGE_ENABLED)]
    win32security.AdjustTokenPrivileges(htoken, 0, newPrivileges)

AdjustPrivilege("seDebugPrivilege") # need this to avoid "Handle is invalid" errors with win32.OpenProcess



screen_res = [GetSystemMetrics(0), GetSystemMetrics(1)]
phi_screen = SCREEN_ANGLE*np.pi/180
psi_screen = np.arcsin(screen_res[1]*np.sin(phi_screen)/screen_res[0])
d = screen_res[0]/(2*math.sin(phi_screen))

while True:
    try:
        openvr.init(openvr.VRApplication_Background)
        break
    except:
        print "OpenVR Server not found."
        time.sleep(5)
print "OpenVR Server found."
vrsystem = openvr.VRSystem()
poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
poses = poses_t()
frameDuration = 1.0/vrsystem.getFloatTrackedDeviceProperty(openvr.k_unTrackedDeviceIndex_Hmd, openvr.Prop_DisplayFrequency_Float)[0]
keyboard = keyboard_state()

while not get_pid("wow.exe"):
    print "WoW.exe not found, please start the game."
    time.sleep(5)
print "WoW.exe found."
mw = wowmw(FOV=FOV)

# Use cheat engine trainer to deactivate default camera controls
# Because I don't know how to do this with Python
script_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
CE_exes = {"1.12": os.path.join(script_directory, "CheatEngine", "CE_WoW_1.12.exe"),
           "3.3.5": os.path.join(script_directory, "CheatEngine", "CE_WoW_3.3.5.exe"),
           "2.4.3": os.path.join(script_directory, "CheatEngine", "CE_WoW_2.4.3.exe")}
trainer = subprocess.Popen(args=[CE_exes[mw.version]])
time.sleep(3)
keyboard.toggle([Key.ctrl_l, Key.f1],True)
time.sleep(0.2)
keyboard.toggle([Key.ctrl_l, Key.f1],False)

print "Default camera controls deactivated."
print "Ctrl-c in this window to stop"

toggle_view_button_down = False
free_look_offset = [0,0,0]
view_mode = "FOLLOW"
head_offset_from_hmd = 0.1
old_yaw = 0

event = openvr.VREvent_t()

if mw.version != "1.12":
    PLAYER_HEIGHT -= 2.0
paused = False

# main loop
while(True):
    while(True):
        new_event = vrsystem.pollNextEvent(event)
        if not new_event:
            break
        else:
            if event.eventType == 103 and event.trackedDeviceIndex == openvr.k_unTrackedDeviceIndex_Hmd:
                paused = False
                break
    old_time = time.time()
    while(mw.isInGame() and not paused):
        while(True):
            new_event = vrsystem.pollNextEvent(event)
            if not new_event:
                break
            else:
                if event.eventType == 104 and event.trackedDeviceIndex == openvr.k_unTrackedDeviceIndex_Hmd:
                    paused = True
                    break
        
        delta_t = time.time() - old_time
        # I'm not sure about reducing judder, needs work
        time.sleep(max(frameDuration*0.2 - delta_t,0))
        old_time = time.time()
        delta_t = frameDuration*0.2
        
        # What is the best value for predictedSecondsFromNow? Can this reduce judder?
        timeSinceLastVsync = vrsystem.getTimeSinceLastVsync()[1]
        
        #predictedSecondsFromNow = HMD_LATENCY
        predictedSecondsFromNow = max(0, frameDuration) # What do I do here
        
        poses = vrsystem.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding,predictedSecondsFromNow,16,None)

        openvr.VRCompositor().waitGetPoses(poses, 16, None, 0)
        hmd_pose=poses[openvr.k_unTrackedDeviceIndex_Hmd]
        
        p = hmd_pose.mDeviceToAbsoluteTracking
        
        player_pos = mw.getPlayerPos()
        player_yaw = mw.getPlayerYaw()
        
        hmd_pos, hmd_angles = m34_to_wow_euler(p)
        hmd_angles[1] += PITCH_OFFSET

        (yaw, pitch, roll, x, y ,z) =  convert_pose(hmd_pos, hmd_angles,pos_offset=mw.getPlayerPos(),yaw_offset=0,pos_scale=1,player_height=PLAYER_HEIGHT)
        
        leftcont = vrsystem.getTrackedDeviceIndexForControllerRole(1)
        rightcont = vrsystem.getTrackedDeviceIndexForControllerRole(2)
        leftcont_pose = poses[leftcont]
        rightcont_pose = poses[rightcont]
        if(view_mode == "FOLLOW"):
            if 2*np.sqrt(hmd_pos[0]**2 + hmd_pos[1]**2) > 0.75:
                alpha = 1
            else:
                alpha = 0
            # When standing a certain distance from the centre of the room/player, you can 'mire your character instead of turning them
            if alpha == 0 and abs(old_yaw - yaw) > 0.05:
                mw.setPlayerYaw(yaw)
                old_yaw = yaw
            if pitch > 0.7 and SEE_YOURSELF:
                alpha = 1 # See yourself! I guess?
            
            mw.setCameraAngles(yaw, pitch, roll)            
            mw.setCameraPos(x,y,z)        
            
        elif view_mode=="FOLLOW_TELE":
            alpha = 1
            player_yaw = mw.getPlayerYaw()
            mw.setCameraAngles(yaw, pitch, roll)
            
            if (x - cur_x)**2 + (y - cur_y)**2 > MAX_CAMERA_DIST**2:
                
                mw.setCameraPos(x + (cur_x-x)/5,y + (cur_y-y)/5,z+free_look_offset[2])
                cur_x = x
                cur_y = y
        else:

            alpha = 1
            mw.setCameraAngles(yaw, pitch, roll)
            #mw.setCameraZoom(zoom)
            x,y,z = np.array([x,y,z]) + free_look_offset
            mw.setCameraPos(x,y,z)
        mw.setPlayerAlpha(alpha)
        
        #Process controller inputs
        if leftcont < 16:
            
            leftstate = vrsystem.getControllerState(leftcont)[1]

            left_pos, left_angles = m34_to_wow_euler(leftcont_pose.mDeviceToAbsoluteTracking if HEADSET!="RIFT" else adjust_controller_angle(leftcont_pose.mDeviceToAbsoluteTracking))            
            
            if view_mode == "FREE_LOOK":
                
                left_x, left_y = struct.unpack('2f',leftstate.rAxis[0])
                delta_phi = np.pi/2 if left_y == 0 else np.arctan(-left_x/left_y)

                stick_speed = np.sqrt(left_x**2 + left_y**2) * np.sign(left_y)
                v = np.array([(np.cos(left_angles[0] + delta_phi))*np.cos(left_angles[1]),
                                        (np.sin(left_angles[0] + delta_phi))*np.cos(left_angles[1]),
                                        (-np.sin(left_angles[1]))])
                v = v * delta_t * stick_speed * FREE_LOOK_SPEED
                free_look_offset[0] = free_look_offset[0] + v[0]
                free_look_offset[1] = free_look_offset[1] + v[1]
                free_look_offset[2] = free_look_offset[2] + v[2]
            process_controller_state(leftstate,left_mapping, keyboard)
        if rightcont < 16:
            rightstate = vrsystem.getControllerState(rightcont)[1]
            right_pos, right_angles = m34_to_wow_euler(rightcont_pose.mDeviceToAbsoluteTracking if HEADSET!="RIFT" else adjust_controller_angle(rightcont_pose.mDeviceToAbsoluteTracking))   
            
            # Mouse tracking
            v1 = [math.sin(hmd_angles[0])*math.cos(hmd_angles[1]), math.cos(hmd_angles[0])*math.cos(hmd_angles[1]), math.sin(hmd_angles[1])]
            v2 = [math.sin(right_angles[0])*math.cos(right_angles[1]), math.cos(right_angles[0])*math.cos(right_angles[1]), math.sin(right_angles[1])]
            n1 = np.array(v1)
            n2 = np.array(v2)

            n1 = n1/np.linalg.norm(n1)
            n2 = n2/np.linalg.norm(n2)
            n_dot = n1[0]*n2[0] + n1[1]*n2[1] + n1[2]*n2[2]
            
            x_intersect = (d/n_dot)*n2 - d*n1
            
            rot_n11 = rotation_matrix([0,0,1],hmd_angles[0])
            rot_n12 = rotation_matrix([1,0,0],-hmd_angles[1])
            rot_n13 = rotation_matrix([0,1,0], -hmd_angles[2])
            mouse_coords = rot_n13*rot_n12*rot_n11*x_intersect.reshape(3,1)
            mouse_x = int(max(min(-mouse_coords[0]+screen_res[0]/2 + 1,screen_res[0]),1))
            mouse_y = int(max(min(mouse_coords[2]+screen_res[1]/2 + 1,screen_res[1]),1))
            win32api.SetCursorPos((mouse_x,mouse_y))

            if rightstate.ulButtonPressed & 4294967296:
                toggle_view_button_down = True
            else:
                # this is very lazily written
                if toggle_view_button_down: # toggle through the different camera modes
                    if view_mode == "FOLLOW":
                        left_mapping["x_left"] = ""
                        left_mapping["x_right"] = ""
                        left_mapping["y_up"] = ""
                        left_mapping["y_down"] = ""
                        free_look_offset = [0,0,0]
                        view_mode = "FREE_LOOK"
                    elif view_mode == "FOLLOW_TELE":
                        
                        left_mapping["x_left"] = "q"
                        left_mapping["x_right"] = "e"
                        left_mapping["y_up"] = "w"
                        left_mapping["y_down"] = "s"
                        view_mode = "FOLLOW"
                    elif view_mode == "FREE_LOOK":
                        cur_x, cur_y, cur_z = x,y,z
                        left_mapping["x_left"] = "a"
                        left_mapping["x_right"] = "d"
                        left_mapping["y_up"] = "w"
                        left_mapping["y_down"] = "s"
                        view_mode = "FOLLOW_TELE"
                toggle_view_button_down = False
            
            process_controller_state(rightstate,right_mapping, keyboard)
    time.sleep(1)
