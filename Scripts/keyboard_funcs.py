from win32api import keybd_event
import win32api, win32con
import struct

from pynput.keyboard import Key, Controller, Listener


def process_controller_state(state, mapping, keyboard):
        stick = struct.unpack('2f',state.rAxis[0])
        stick_thresh = mapping["stick_thresh"]
        keyboard.toggle(mapping["x_right"],stick[0] > stick_thresh)
        keyboard.toggle(mapping["x_left"],stick[0] < -stick_thresh)
        keyboard.toggle(mapping["y_up"],stick[1] > stick_thresh)
        keyboard.toggle(mapping["y_down"],stick[1] < -stick_thresh)        
        keyboard.toggle(mapping["a"],state.ulButtonPressed & 128) # k_EButton_A
        keyboard.toggle(mapping["b"],state.ulButtonPressed & 2) # k_EButton_ApplicationMenu
        keyboard.toggle(mapping["trigger"],state.ulButtonPressed & 8589934592) # k_EButton_SteamVR_Trigger
        keyboard.toggle(mapping["touchpad"],state.ulButtonPressed & 4294967296)
        keyboard.toggle(mapping["grip"],state.ulButtonPressed & 4) # k_EButton_Grip
        
        


class keyboard_state(object):
    def __init__(self):
        self.pressed = []
        self.keyboard = Controller()
    def press(self,key):
        if key not in self.pressed and key!="":
            self.pressed.append(key)
            if key == "LEFT_CLICK":
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0) # don't want dragging because it messes with the camera
                return
            if key == "RIGHT_CLICK":
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,0,0)
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)
                return
            self.keyboard.press(key)
            
    def release(self,key):
        if key in self.pressed:
            self.pressed.remove(key)
            if key == "LEFT_CLICK":
                #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
                return
            if key == "RIGHT_CLICK":
                #win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,0,0)
                return
            self.keyboard.release(key)
    def toggle(self, keys, do): 
        if(type(keys)!=list):
            if do:
                self.press(keys)
            else:
                self.release(keys)
            return
        if(do):
            for key in keys:
                self.press(key)
        else:
            for key in keys:
                self.release(key)
            