import numpy
from cgkit.all import vec3

def calculateTangents(positions,normals,texcoords,elements):

#We want our tangent space to be aligned such that 
#the x axis corresponds to the u direction in the bump map and
# the y axis corresponds to the v direction in the bump map. 
#That is, if Q represents a point inside the triangle,
# we would like to be able to write
#Q - P0 = (u - u0)T + (v - v0)B

    vcount = len(positions)
    tan1 = numpy.zeros((vcount,3),dtype='float32')
    tan2 = numpy.zeros((vcount,3),dtype='float32')
    tangents = numpy.zeros((vcount,4),dtype='float32')

    for (i1,i2,i3) in elements:
        v1,v2,v3 = positions[i1],positions[i2],positions[i3]
        w1,w2,w3 = texcoords[i1],texcoords[i2],texcoords[i3]

        x1,y1,z1 = v2 - v1
        x2,y2,z2 = v3 - v1

        s1,t1 = w2 - w1
        s2,t2 = w3 - w1

        r = 1.0 / (s1 * t2 - s2 * t1)

        sdir = [(t2*x1-t1*x2)*r,(t2*y1-t1*y2)*r,(t2*z1-t1*z2)*r]
        tdir = [(s1*x2-s2*x1)*r,(s1*y2-s2*y1)*r,(s1*z2-s2*z1)*r]

        tan1[i1] += sdir
        tan1[i2] += sdir
        tan1[i3] += sdir

        tan2[i1] += tdir
        tan2[i2] += tdir
        tan2[i3] += tdir

    for i in range(0,vcount):
        vn = normals[i]
        vt = tan1[i]
        n = vec3(float(vn[0]),float(vn[1]),float(vn[2]))
        t = vec3(float(vt[0]),float(vt[1]),float(vt[2]))

        #Gram-Scmidt orthogonalize
        tan = (t - n * (n*t)).normalize()
        tangents[i] = tan[0],tan[1],tan[2],0
        
        #Handedness
        vt2 = tan2[i]
        t2 = vec3(float(vt2[0]),float(vt2[1]),float(vt2[2]))
        h = (n.cross(t)) * t2
        if h < 0:
            tangents[i][3] = -1.0
        else:
            tangents[i][3] = 1.0
        
    #In the end, B = (NxT)*T_w
    return tangents

        
