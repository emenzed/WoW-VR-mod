from memorpy import *
import psutil
import sys

def get_pid(names):
    if type(names)!=list:
        names = [names]
    names = names + [name.split('.exe')[0] if '.exe' in name else name + '.exe' for name in names]
    for proc in psutil.process_iter():
        if proc.name().lower() in names:
            return(proc.pid)
    return 0
    
# Memory address offsets for variables
class wowOffsets(object):
    def __init__(self,version="1.12"):
        self.version = version
        if version == "1.12":
            self.isInGame = 0x00B4B424
            self.worldFrame = 0x00B4B2BC
            self.worldFrameCameraOffset = 0x65B8
            self.cameraX = 0x0008
            self.cameraY = 0x000C
            self.cameraZ = 0x0010
            
            self.cameraFOV = 0x0040
            self.cameraZoom = 0x00EC
            self.cameraYaw = 0x00F0
            self.cameraPitch = 0x00F4
            self.cameraRoll = 0x00F8
            self.cameraPlayerYaw = 0x018C
            self.cameraPlayerX = 0x0174
            self.cameraPlayerY = 0x0178
            self.cameraPlayerZ = 0x017C
            self.cameraFixFlag = 0x00A4
            
            self.objectManager = [0x00B41414]
            #self.objectManagerOffset = 0x00
            self.playerGuid = 0x00B41E30
            self.baseObjectOffset = 0xAC
            self.nextObjectOffset = 0x3C
            self.objectGuidOffset = 0x30
            self.objectOrientationOffset = 0x118
            self.objectYawOffset = 0x1C
            self.objectAlphaOffset = 0x100
        if version == "3.3.5":
            self.isInGame = 0x00BCEFE0
            self.worldFrame = 0x00B7436C
            self.worldFrameCameraOffset = 0x7E20
            self.cameraX = 0x0008
            self.cameraY = 0x000C
            self.cameraZ = 0x0010
            
            self.cameraFOV = 0x0040
            self.cameraZoom = 0x0118
            self.cameraYaw = 0x011C
            self.cameraPitch = 0x0120
            self.cameraRoll = 0x0124
            self.cameraPlayerYaw = 0x01D4
            self.cameraPlayerX = 0x01C4
            self.cameraPlayerY = 0x01C8
            self.cameraPlayerZ = 0x01CC
            self.cameraFixFlag = 0x00AC
            
            self.objectManager = [0x00C79CE0,0x2ED0]
            #self.objectManagerOffset = 0x2ED0
            self.playerGuid = 0x00CA1238
            self.baseObjectOffset = 0xAC
            self.nextObjectOffset = 0x3C
            self.objectGuidOffset = 0x30
            #self.objectOrientationOffset = 0x118
            self.objectYawOffset = 0x7A8
            self.objectAlphaOffset = 0xCB
        if version == "2.4.3":
            self.isInGame = 0x00BDB1AC
            self.worldFrame = 0x00C6ECCC
            self.worldFrameCameraOffset = 0x732C
            self.cameraX = 0x0008
            self.cameraY = 0x000C
            self.cameraZ = 0x0010
            
            self.cameraFOV = 0x0040
            self.cameraZoom = 0x100
            self.cameraYaw = 0x104
            self.cameraPitch = 0x108
            self.cameraRoll = 0x010C
            self.cameraPlayerYaw = 0x01A0
            self.cameraPlayerX = 0x0190
            self.cameraPlayerY = 0x0194
            self.cameraPlayerZ = 0x0198
            self.cameraFixFlag = 0x00AC
            
            self.objectManager = [0x00D43318, 0x2218]
            #self.objectManagerOffset = 0x00
            self.playerGuid = 0x00D68A00
            self.baseObjectOffset = 0xAC
            self.nextObjectOffset = 0x3C
            self.objectGuidOffset = 0x30
           # self.objectOrientationOffset = 0x118
            self.objectYawOffset = 0xBFC
            self.objectAlphaOffset = 0x10C
            

class wowAddresses(object):
    def __init__(self, mw, offsets):
        # static addresses
        self.isInGame = mw.Address(offsets.isInGame)
        self.worldFramePointer = mw.Address(offsets.worldFrame)
    def updatePointers(self, mw, offsets):
        self.worldFrame = mw.Address(self.worldFramePointer.read(type='uint'))
        self.cameraPointer = self.worldFrame + offsets.worldFrameCameraOffset
        self.camera = mw.Address(self.cameraPointer.read(type='uint'))
        
        self.cameraPos = self.camera + offsets.cameraX # Vector3 (x, y, z)
        self.cameraFOV = self.camera + offsets.cameraFOV
        self.cameraZoom = self.camera + offsets.cameraZoom
        self.cameraAngles = self.camera + offsets.cameraYaw # Vector3 (yaw, pitch, roll)
        self.cameraPlayerPos = self.camera + offsets.cameraPlayerX # Vector3 (x, y ,z)
        self.cameraPlayerYaw = self.camera + offsets.cameraPlayerYaw
        self.cameraFixFlag = self.camera + offsets.cameraFixFlag        
        
        self.objectManager = mw.Address(mw.Address(offsets.objectManager[0]).read())
        for i in range(len(offsets.objectManager)-1):
            self.objectManager = mw.Address((self.objectManager + offsets.objectManager[1+i]).read())
        self.playerGuid = mw.Address(offsets.playerGuid)
        
        self.playerObject = self.getObjectPtr(mw, offsets, self.playerGuid.read(type='uint'))
        self.playerAlpha = self.playerObject + offsets.objectAlphaOffset
        if offsets.version == "1.12":
            self.playerYaw = mw.Address((self.playerObject+offsets.objectOrientationOffset).read(type='uint')) + offsets.objectYawOffset
        elif offsets.version in ("2.4.3","3.3.5"):
            self.playerYaw = self.playerObject + offsets.objectYawOffset
    def getObjectPtr(self, mw, offsets, guid):
        objectAddress = mw.Address((mw.Address((self.objectManager)) + offsets.baseObjectOffset).read()) 
        while(objectAddress.read(type='uint')!=0):
            objectGuid = (objectAddress + offsets.objectGuidOffset).read(type='uint', maxlen=8)
            if objectGuid == guid:
                return objectAddress
            objectAddress = mw.Address((objectAddress + offsets.nextObjectOffset).read(type='uint'))
        return 0

class wowmw(object):
    def __init__(self, FOV):
        self.mw = MemWorker(pid=get_pid(["wow.exe","wow-64.exe"]),debug=False)
        # Check version
        if len([x for x in self.mw.mem_search("1.12.1 (5875) (Release)")]):
            self.version = "1.12"
        elif  len([x for x in self.mw.mem_search("3.3.5 (12340) (Release)")]):
            self.version = "3.3.5"
        elif len([x for x in self.mw.mem_search("2.4.3 (8606) (Release)")]):
            self.version = "2.4.3"
        else:
            print "WoW version not supported."
            #return
            sys.exit(1)
        self.offsets = wowOffsets(version = self.version)
        self.addresses = wowAddresses(self.mw, self.offsets)
        self.inGame = 0
        self.FOV = FOV
        
    def isInGame(self):
        inGame = self.addresses.isInGame.read(type='uint', maxlen=1)
        if self.inGame == 0 and inGame == 1:
            self.addresses.updatePointers(self.mw, self.offsets)
            self.setCameraFOV(self.FOV)
            self.fixCameraTurning()
        self.inGame = inGame
        return inGame
    def fixCameraTurning(self):
        self.addresses.cameraFixFlag.write(data=struct.pack('i',1),type='bytes')
    def getPlayerPos(self):
        return struct.unpack('3f', self.addresses.cameraPlayerPos.read(type='bytes',maxlen=12))
    
    def getPlayerYaw(self):
        return struct.unpack('f', self.addresses.playerYaw.read(type='bytes', maxlen=4))[0]
    
    def setCameraPos(self,x,y,z):
        self.addresses.cameraPos.write(data = struct.pack('3f',x,y,z), type='bytes')
    # By default, distance of camera to player position. By default, affects character alpha and different addresses are used in 1st person (zoom = 0)
    def setCameraZoom(self,f):
        self.addresses.cameraZoom.write(data = struct.pack('f',f), type='bytes')
    def setCameraFOV(self,f):
        self.addresses.cameraFOV.write(data = struct.pack('f',f), type='bytes')
    
    def setCameraAngles(self, yaw, pitch, roll):
        self.addresses.cameraAngles.write(data = struct.pack('3f', yaw, pitch,roll), type='bytes')
    def setPlayerYaw(self, yaw):
        self.addresses.playerYaw.write(data = struct.pack('f', yaw), type='bytes')
    def setPlayerAlpha(self, alpha):
        if self.version in ("1.12","2.4.3"):
            self.addresses.playerAlpha.write(data = struct.pack('f', alpha), type='bytes')
        elif self.version == "3.3.5":
            self.addresses.playerAlpha.write(data = struct.pack('B', max(min(int(alpha*255),255),0)),type='bytes')