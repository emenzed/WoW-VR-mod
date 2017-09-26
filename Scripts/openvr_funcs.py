import math
import numpy as np



# Convert OpenVR pose to in-game pose
def convert_pose(x, angles, yaw_offset = 0, pos_offset=[0,0,0], pos_scale=1, abs_offset = [0,0,0],player_height = 1.8): 
    yaw, pitch, roll = angles[0], angles[1], angles[2]
    x1, y1, z1 = -x[0],-x[1],x[2]
    (x,y,z) = (np.array([x1*np.cos(yaw_offset) - y1*np.sin(yaw_offset),y1*np.cos(yaw_offset) + x1*np.sin(yaw_offset),z1])*pos_scale + pos_offset) # left-right pos 
    if abs(pitch) >= np.pi/2:
        yaw = np.mod(np.pi + yaw,2*np.pi)
        roll = roll + np.pi
        pitch = np.sign(pitch)*(np.pi/2 - np.mod(abs(pitch),np.pi/2))
    return (yaw, pitch, roll, x, y, z-player_height)

# Convert OpenVR y-up orientation matrix to WoW's Z-up euler angles + position
def m34_to_wow_euler(m34):
    yaw = -np.arctan2(-m34[0][2],m34[2][2])
    pitch = -np.arctan2(-m34[1][2],np.sqrt(m34[1][0]**2 + m34[1][1]**2))
    roll = -np.arctan2(m34[1][0],m34[1][1])
    
    return [m34[2][3],m34[0][3],m34[1][3]], [yaw, pitch, roll]

def numpy_m33_to_wow_euler(m33):
    yaw = -np.arctan2(-m33[0,2],m33[2,2])
    pitch = -np.arctan2(-m33[1,2],np.sqrt(m33[1,0]**2 + m33[1,1]**2))
    roll = -np.arctan2(m33[1,0],m33[1,1])
    return yaw,pitch,roll
    
def Quaternion_toEulerianAngle(x, y, z, w):
    ysqr = y*y
    t0 = +2.0 * (w * x + y*z)
    t1 = +1.0 - 2.0 * (x*x + ysqr)
    X = math.degrees(math.atan2(t0, t1))
    t2 = +2.0 * (w*y - z*x)
    t2 =  1 if t2 > 1 else t2
    t2 = -1 if t2 < -1 else t2
    Y = math.degrees(math.asin(t2))
    t3 = +2.0 * (w * z + x*y)
    t4 = +1.0 - 2.0 * (ysqr + z*z)
    Z = math.degrees(math.atan2(t3, t4))
    return np.array((X, Y, Z))

def EulerianAngle_toQuaternion(yaw, pitch, roll):
	cy = math.cos(yaw * 0.5);
	sy = math.sin(yaw * 0.5);
	cr = math.cos(roll * 0.5);
	sr = math.sin(roll * 0.5);
	cp = math.cos(pitch * 0.5);
	sp = math.sin(pitch * 0.5);

	w = cy * cr * cp + sy * sr * sp;
	x = cy * sr * cp - sy * cr * sp;
	y = cy * cr * sp + sy * sr * cp;
	z = sy * cr * cp - cy * sr * sp;
	return np.array((w,x,y,z))

def orientation_diff(m34_1, m34_2):
    m1 = np.matrix([[x for x in y[0:3]] for y in m34_1])
    m2 = np.matrix([[x for x in y[0:3]] for y in m34_2])
    m3 = m2.I*m1
    #print m3
    return numpy_m33_to_wow_euler(m3)

def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis/math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2.0)
    b, c, d = -axis*math.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.matrix([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])

def adjust_controller_angle(m34):
    adj = np.matrix([[ 1.       ,  0.       ,  0.       ],
        [ 0.       ,  0.8660254, 0.5      ],
        [ 0.       ,  -0.5      ,  0.8660254]])
    m33 = np.matrix([[x for x in y[0:3]] for y in m34])
    new_m33 = m33*adj
    for i in range(3):
        for j in range(3):
            m34[i][j] = new_m33[i,j]
    return m34
