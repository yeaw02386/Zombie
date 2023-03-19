import numpy as np
import math

distance = lambda x1, y1, x2, y2: math.sqrt((y1-y2)**2 + (x1-x2)**2)

class People :
    def __init__(self,x1: int, y1: int, x2: int, y2: int) -> None:
        self.x = np.random.randint(x1,x2)
        self.y = np.random.randint(y1,y2)
        self.walk = np.random.randint(220, 600)
        self.vision = np.random.randint(30, 180)
        p = np.random.randint(4, 10)/10
        self.rateWin = [p,1-p]
        
    def __repr__(self) -> str:
        return 'people '+f'x:{self.x} y:{self.y}'
        
    def walkTo(self,x:int,y:int):
        self.x = x
        self.y = y
        
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
        
class Zombie :
    def __init__(self,p: People) -> None:
        self.x = p.x
        self.y = p.y
        self.walk = int(p.walk/2)
        self.vision = int(p.vision/2)

    def __repr__(self) -> str:
        return 'zombie '+f'x:{self.x} y:{self.y}'
        
    def walkTo(self,x:int,y:int):
        self.x = x
        self.y = y
        
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
class Base :
    def __init__(self,x,y,n) -> None:
        self.build = False
        self.x = x
        self.y = y
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
    
    

        