import numpy as np
import math

distance = lambda x1, y1, x2, y2: math.sqrt((y1-y2)**2 + (x1-x2)**2)

inBlock = lambda x,y,b: True if b.x2<x<b.x1 and b.y1<y<b.y2 else False

genWay = lambda x,y,long,d: (int(x+long * np.cos(np.rad2deg(d))),
                                int(y+long * np.sin(np.rad2deg(d))))

def gen8block(x, y, v): return [[y+v, x-v], [y+v, x], [y+v, x+v], [y, x+v],
                                [y-v, x+v], [y-v, x], [y-v, x-v], [y, x-v],
                                [y,x]]

def compare8chunk(x1, y1, x2, y2, b): return [
    [b[0][0] > y1, b[0][1] < x1], [b[1][0] > y1, True],
    [b[2][0] > y1, b[2][1] > x2], [True, b[3][1] > x2],
    [b[4][0] < y2, b[4][1] > x2], [b[5][0] < y2, True],
    [b[6][0] < x1, b[6][1] < y2], [True, b[7][1] < x1]]


class People :
    def __init__(self,x1: int, y1: int, x2: int, y2: int) -> None:
        self.inf = 1
        self.x = np.random.randint(x1, x2)
        self.y = np.random.randint(y1, y2)
        self.walk = np.random.randint(200, 1000)
        self.vision = np.random.randint(30, 200)
        p = np.random.randint(4, 10)/10
        self.rateWin = [p,1-p]
        
    def walkTo(self,x:int,y:int):
        self.x = x
        self.y = y
        
    def getPos(self):
        return [self.x,self.y]
        
class Zombie :
    def __init__(self,p: People) -> None:
        self.inf = -1
        self.x = p.x
        self.y = p.y
        self.walk = int(p.walk/2)
        self.vision = np.random.randint(30, 200)
        
    def walkTo(self,x:int,y:int):
        self.x = x
        self.y = y
        
    def getPos(self):
        return [self.x,self.y]
        
class Chunk:
    def __init__(self,ix,iy,x1,y1,x2,y2,entity:np.ndarray) -> None:
        self.ix = ix
        self.iy = iy
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.around = gen8block(ix,iy,1)
        self.e = entity
        self.now = 0
        self.full = self.e.shape[0]-1
        self.count = 0
        
    def regChunk(self):
        size = (self.full+1)*2
        self.e = self.e.resize(size)
        self.full = size-1
        
    def compare(self,p8):
        c = compare8chunk(self.x1,self.y1,self.x2,self.y2,p8)
        i = np.all(c,axis=1)
        return self.around[i]
        
    def push(self,entity) :
        if self.full <= self.now :
            self.regChunk()
        
        self.now += 1 
        self.e[self.now] = entity
        
    def pop(self) :
        e = self.e[self.now]
        self.e[self.now] = None
        self.now -= 1
        
        return e
    
    def getData(self):
        get = np.vectorize(lambda e:e.getPos())
        pos = get(self.e[:self.now+1])
        
        return (pos[:,0],pos[:,1])
    
    def findEntity(self,e):
        self.count = 0
        def find(e:Zombie,p:People):
            d = distance(p.x, p.y, e.x, e.y)
            if d <= p.vision+e.vision : self.count += 1
            
        fFind = np.vectorize(find)
        fFind(e,self.e[:self.now+1])
        
        return self.count
    


class Base :
    def __init__(self,chunk:Chunk,n) -> None:
        self.build = False
        self.x = np.random.randint(chunk.x1, chunk.x2)
        self.y = np.random.randint(chunk.y1, chunk.y2)
        self.now = 0
        self.max = n
        self.full = False
        
    def isArrivedBase(self,p:People):
        if not self.build or self.full: return False
        
        d = distance(p.x,p.y,self.x,self.y)
        if d <= p.vision :
            self.now += 1
            if self.now >= self.max : 
                self.full = True
            return True
        return False
    
class Map:
    def __init__(self,z,x1,y1,x2,y2,numChunk,numEntity) -> None:
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.z = z
        self.map = self.spawnChunk(x1,y1,x2,y2,numChunk,numEntity)
        self.know = False
        
        
    def spawnChunk(self,x1,y1,x2,y2,numChunk,numEntity):
        n = numChunk**0.5
        
        m = []
        lenght = (x2-x1)/n 
        X1 = 0
        Y1 = 0
        for i in range(n):
            mx = []
            for j in range(n):
                c = Chunk(j,i,1,2,3,4)
                mx.append(c) 
                X1 = x1 + lenght
                Y1 = y1 + lenght

                #พักแปป

                
            m.append(mx) 
        
    def genEntity(self,num,x1,y1,x2,y2):
        if self.z :return np.full(num,None)
        people = []
        for _ in range(num):
            p = People(x1,y1,x2,y2)
            people.append(p)
            
        return np.array(people)
    
    def moveTo(self,x,y,chunkI1,chunkI2):
        y1,x1 = chunkI1
        y2,x2 = chunkI2
        
        e = self.map[y1][x1].pop()
        e.walkTo(x,y)
        
        self.map[y2][x2].push(e)

    def findBlock(self,x: int, y: int):
        for i in self.map:
            for j in i:
                if inBlock(x,y,j):
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
            if not inBlock(x, y,self.map):
                x, y = genWay(e.x,e.y, long, i-180)
                
            c = self.findBlock(x, y)
            if self.z: return (x, y, c)
            
            p8 = gen8block(x,y,e.vision)
            chunkS = c.compare(p8)
            
            z = 0
            for iy,ix in chunkS:
                z += mapZ.map[iy][ix].findEntity(e)
            
            allWay.append([z,x,y,c]) 
        
        if not self.know:return allWay[0]
        
        allWay.sort()
        if not base.bulid and base.full:
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
        
        fight = np.random.choice([True,False],z,True,[p.rateWin])
        
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
                e = self.map[i][j].pop()
                if self.z : self.zombieWalk(e)
                else : self.peopleWalk(e,base,mapZ)
                
    def getData(self):
        getSize = np.vectorize(lambda x:x.now+1)
        s = getSize(self.map)
        x = np.zeros(sum(s),dtype=int)
        y = np.zeros(sum(s),dtype=int)
        cn = 0
        ci = 0
        for i in self.map:
            for j in i :
                ix,iy = j.getData()
                x[cn:s[ci+1]] = ix
                y[cn:s[ci+1]] = iy
                ci += 1
                cn += s[ci]
                
        return x,y