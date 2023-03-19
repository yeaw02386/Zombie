import numpy as np
import math
from Entity import *

distance = lambda x1, y1, x2, y2: math.sqrt((y1-y2)**2 + (x1-x2)**2)

inBlock = lambda x,y,b: True if (x>=b.x1 and x<=b.x2) and (b.y1<=y and y<=b.y2) else False

genWay = lambda x,y,long,d: (int(x+long * np.cos(np.rad2deg(d))),
                                int(y+long * np.sin(np.rad2deg(d))))

def gen8block(x, y, v): return [[y+v, x-v], [y+v, x], [y+v, x+v], [y, x+v],
                                [y-v, x+v], [y-v, x], [y-v, x-v], [y, x-v],
                                [y,x]]

def compare8chunk(x1, y1, x2, y2, b): return [
    [b[0][0] > y1, b[0][1] < x1], [b[1][0] > y1, True],
    [b[2][0] > y1, b[2][1] > x2], [True, b[3][1] > x2],
    [b[4][0] < y2, b[4][1] > x2], [b[5][0] < y2, True],
    [b[6][0] < x1, b[6][1] < y2], [True, b[7][1] < x1],
    [True,True]]


class Chunk:
    def __init__(self,z,ix,iy,x1,y1,x2,y2,entity:np.ndarray) -> None:
        self.ix = ix
        self.iy = iy
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.around = np.array(gen8block(ix,iy,1))
        self.e = entity
        self.z =z
        if z : 
            self.now = 0
        else : 
            self.now = len(entity)
        self.full = len(entity)-1
        self.count = 0
        
    def __repr__(self) -> str:
        return f"e::{self.z} All: {len(self.e)} Now:{self.now} ,x1:{self.x1},y1:{self.y1} x2:{self.x2},y1:{self.y2}"
        
    def regChunk(self):
        size = (self.full+2)*2
        self.e.resize(size)
        self.full = size-1
        
    def compare(self,p8):
        c = compare8chunk(self.x1,self.y1,self.x2,self.y2,p8)
        i = np.all(c,axis=1)
        return self.around[i]
        
    def push(self,entity) :
        
        if self.full <= self.now :
            self.regChunk()
            
        self.e[self.now] = entity
        self.now += 1
        
        
        
    def popAll(self):
        if self.now != 0 and not self.z:n = self.now
        else : n = self.now
        e = np.copy(self.e[:n])
        self.e[:n] = np.full_like(e,None)

        self.now = 0
        return e
    
    def getData(self):
        getx = np.vectorize(lambda e:e.getX())
        gety = np.vectorize(lambda e:e.getY())
        #if not self.z: print(self.e)
        
        if self.now == 0 : return ([],[])
        
        x = getx(self.e[:self.now])
        y = gety(self.e[:self.now])

        return (x,y)
    
    def findEntity(self,e):
        if self.now == 0 :return 0
        self.count = 0
        def find(e:Zombie,p:People):
            d = distance(p.x, p.y, e.x, e.y)
            if d <= p.vision+e.vision : self.count += 1
            
        fFind = np.vectorize(find)
        fFind(e,self.e[:self.now])

        return self.count
class mapRange:
    def __init__(self,x1,y1,x2,y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
class Map:
    def __init__(self,z,x1,y1,x2,y2,numChunk,numEntity) -> None:
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.ox = int((x2-x1)/2)
        self.oy = int((y2-y1)/2)
        self.range = mapRange(x1,y1,x2,y2)
        self.z = z
        self.map = self.spawnChunk(x1,y1,x2,y2,numChunk,numEntity)
        self.know = False
         
    def spawnChunk(self,x1,y1,x2,y2,numChunk,numEntity):
        sqrNCh = int(math.sqrt(numChunk))
        num = int((x2-x1)/sqrNCh)
        spt = int(numEntity/numChunk)
        m =[]
        x1 = 0
        y1 = 0
        x2 = num
        y2 = num
        for i in range(sqrNCh):
            Mx = []
            x1 = 0
            x2 = num
            for j in range(sqrNCh):
                EN = self.genEntity(spt,x1,y1,x2,y2)
                c = Chunk(self.z,j,i,x1,y1,x2,y2,EN)
                Mx.append(c)
                x1 = x1 + num
                x2 = x2 + num
                             
            m.append(Mx)
            y1 = y1 + num
            y2 = y2 + num
                
        return np.array(m)   
        
    def genEntity(self,num,x1,y1,x2,y2):
        if self.z : return np.full((num),None,dtype=Zombie)
        people = []
        for _ in range(num):
            p = People(x1,y1,x2,y2)
            people.append(p)
            
        return np.array(people)
    
    def genZombie(self):
        m = self.map.flatten()
        c = np.random.choice(m)
        p = People(c.x1,c.y1,c.x2,c.y2)
        z = Zombie(p)
        self.map[c.iy][c.ix].push(z)
        

    def findBlock(self,x: int, y: int):
        for i in self.map:
            for j in i:
                if inBlock(x,y,j):
                    return j
        return j
        
    def chooseWay(self,e,n=1,base=None,mapZ=None):
        if self.know:
            way = np.random.randint(0, 360, n)
        else:
            way = np.random.randint(0, 360, 1)

        if self.z: mR = 100
        else: mR = 200
        
        long = np.random.randint(mR, e.walk)
        
        allWay = []
        for i in way:
            x,y = genWay(e.x,e.y,long,i)
            ch = lambda a :self.x2 if a>self.x2 else self.x1 if a<self.x1 else a
            if not inBlock(x,y,self.range):
                x = ch(x)
                y = ch(y)
                # d = math.atan2(e.y-self.oy,e.x-self.ox)
                # x,y = genWay(e.x,e.y, long, np.rad2deg(d))
               
            c = self.findBlock(x, y)
            if self.z: 
                return (x, y, c)
            
            p8 = gen8block(x,y,e.vision)
            chunkS = c.compare(p8)
            
            z = 0
            for iy,ix in chunkS:
                try:
                    z += mapZ.map[iy][ix].findEntity(e)
                except :pass
            
            allWay.append([z,x,y,c]) 
        
        if not self.know:return allWay[0]
        
        allWay.sort()
        if not base.build and base.full:
            return allWay[0] 

        dBase1 = distance(allWay[0][1],allWay[0][2], base.x,base.y)
        dBase2 = distance(allWay[1][1],allWay[1][2], base.x,base.y)
        
        if dBase1 <= dBase2:
            return allWay[0]
        return allWay[1]
            
    def peopleWalk(self,p:People,base:Base,mapZ):
        z,x,y,c = self.chooseWay(p,5,base,mapZ)
        p.walkTo(x,y)
    
        if base.isArrivedBase(p) :
            return
        #print(z)
        if z == 0 : 
            self.map[c.iy][c.ix].push(p)
            return 
            
        fight = np.random.choice([True,False],z,True,p.rateWin)
        if not fight.any():
            z = Zombie(p)
            mapZ.map[c.iy][c.ix].push(z)
            return
        
        self.map[c.iy][c.ix].push(p)

    def zombieWalk(self,z:Zombie):
        x,y,c = self.chooseWay(z)
        z.walkTo(x,y)
        self.map[c.iy][c.ix].push(z)
        
    def update(self,base=None,mapZ=None):
        iy,ix = self.map.shape
        for i in range(iy):
            for j in range(ix):
                e = self.map[i][j].popAll()
                if len(e) == 0 :continue
                if self.z : 
                    # zWalk = np.vectorize(lambda e : self.zombieWalk(e))
                    # zWalk(e)
                    for z in e:
                        self.zombieWalk(z)
                else : 
                    
                    # pWalk = np.vectorize(lambda e,base,mapZ:self.peopleWalk(e,base,mapZ))
                    # pWalk(e,base,mapZ)
                    for p in e :
                        self.peopleWalk(p,base,mapZ)
        
    def getData(self):
        x = []
        y = []
        for i in self.map:
            for j in i :
                ix,iy = j.getData()
                x = x+list(ix)
                y = y+list(iy)
    
        return x,y
    
    