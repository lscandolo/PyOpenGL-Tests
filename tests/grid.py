#!/usr/bin/python -tt

def grid(side, slices):

    vert_dist = float(side) / float(slices)
    vert_start = -side/2.

    verts = []

    for vy in range(0,slices+1):
        verts.append([])
        for vx in range(0,slices+1):
            x = vert_start + vert_dist * vx
            y = vert_start + vert_dist * vy
            verts[vy].append((x,0.,y))

    tris = []

    for vy in range(0,slices):
        for vx in range(0,slices):
            a = vy * (slices+1) + vx
            b = a + 1
            c = a + slices + 1
            d = c + 1
            
            a+= 1
            b+= 1
            c+= 1
            d+= 1

            tris.append( (b,a,c) )
            tris.append( (b,c,d) )

    return (verts,tris)

def main():

    side = 10
    slices = 50
    verts,tris = grid(side,slices)

    print "g grid"

    for row in verts:
        for val in row:
            print "v "+str(val[0])+" "+ str(val[1])+" "+str(val[2])

    for row in verts:
        for val in row:
            vts = val[0]/(side) + .5
            vtv = val[2]/(side) + .5
            print "vt "+str(vts)+" "+ str(vtv)

    print "vn 0 1 0"

    for t in tris:
        v0 = str(t[0])+"/"+str(t[0])+"/1"
        v1 = str(t[1])+"/"+str(t[1])+"/1"
        v2 = str(t[2])+"/"+str(t[2])+"/1"
        print "f "+v0+" "+v1+" "+v2

                                                   


if __name__ == '__main__': main()
