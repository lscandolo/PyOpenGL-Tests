from cgkit.cgtypes import *
import cgkit

class quat:
    def __init__(self,x=0,y=0,z=0,w=1):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)

    def __str__(self):
        return str([x,y,z,w])

    def __add__(self, q):
        s = quat()
        s.x = self.x + q.x
        s.y = self.x + q.y
        s.z = self.x + q.z
        s.w = self.x + q.w
        return s

    def __sub__(self,q):
        s = quat()
        s.x = self.x - q.x
        s.y = self.x - q.y
        s.z = self.x - q.z
        s.w = self.x - q.w
        return s

    def __mul__(self,q):
        s = quat()
        s.w = self.w * q.w - self.x * q.x - self.y * q.y - self.z * q.z
        s.x = self.w * q.x + self.x * q.w + self.y * q.z - self.z * q.y
        s.y = self.w * q.y - self.x * q.z + self.y * q.w + self.z * q.x
        s.z = self.w * q.z + self.x * q.y - self.y * q.x + self.z * q.w
        return s

    def __rmul__(self,r):
        s = quat()
        s.x = self.x * r
        s.y = self.x * r
        s.z = self.x * r
        s.w = self.x * r
        return s

    def norm(self):
        return (self.x**2+self.y**2+self.z**2+self.w**2)**(0.5)
    
    def conj(self):
        s = self
        s.x = s.x * (-1)
        s.y = s.y * (-1)
        s.z = s.z * (-1)
        return s

    def rot4(self):
        rot = mat4(1.0)
        a = self.w
        b = self.x
        c = self.y
        d = self.z
        rot[0,0] = a**2 + b**2 - c**2 - d**2
        rot[0,1] = 2 * (b*c - a*d)
        rot[0,2] = 2 * (b*d + a*c)

        rot[1,0] = 2 * (b*c + a*d)
        rot[1,1] = a**2 - b**2 + c**2 - d**2
        rot[1,2] = 2 * (c*d - a*b)

        rot[1,0] = 2 * (b*d - a*c)
        rot[1,1] = 2 * (c*d + a*b)
        rot[1,2] = a**2 - b**2 - c**2 + d**2

    def rot3(self):
        rot = mat3()
        a = self.w
        b = self.x
        c = self.y
        d = self.z
        rot[0,0] = a**2 + b**2 - c**2 - d**2
        rot[0,1] = 2 * (b*c - a*d)
        rot[0,2] = 2 * (b*d + a*c)

        rot[1,0] = 2 * (b*c + a*d)
        rot[1,1] = a**2 - b**2 + c**2 - d**2
        rot[1,2] = 2 * (c*d - a*b)

        rot[1,0] = 2 * (b*d - a*c)
        rot[1,1] = 2 * (c*d + a*b)
        rot[1,2] = a**2 - b**2 - c**2 + d**2

def quat_to_rotMat4(q):
	rm=[[0,0,0],[0,0,0],[0,0,0]]
	for i in range(3):
		rm[i][i]=MT(q,q,md[i])
	rm[0][1]=2*(q.q[1]*q.q[2]-q.q[0]*q.q[3])
	rm[0][2]=2*(q.q[1]*q.q[3]+q.q[0]*q.q[2])
	rm[1][0]=2*(q.q[1]*q.q[2]+q.q[0]*q.q[3])
	rm[1][2]=2*(q.q[2]*q.q[3]-q.q[0]*q.q[1])
	rm[2][0]=2*(q.q[1]*q.q[3]-q.q[0]*q.q[2])
	rm[2][1]=2*(q.q[3]*q.q[2]+q.q[0]*q.q[1])	
	return rm
