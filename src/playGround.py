import numpy as np
import matplotlib.pyplot as plt
import math

# map = [y block][x block][n entry][entry]
# mapLen = [y block][x block][x1,y1,x2,y2,iy,ix,now,full]

# base = [build?,x,y,capacityNow,capacityMax,full?]
# z = [inf,x,y,max,vision,bit]
# p = [inf,x,y,max,vision,rate]
# way = [newx,newy,chunkI[y,x],zombie]


def initPerson(x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
    """สร้างคนขึ้นมา\n
        รับ พื้นที่สี่เหลี่ยมที่จะให้คนเกิด\n
        ส่ง Array ของคน\n
        ข้อมูล [inf,x,y,max,vision,rate]
        """
    p = np.array([1,
                  np.random.randint(x1, x2),
                  np.random.randint(y1, y2),
                  np.random.randint(200, 1000),
                  np.random.randint(30, 200),
                  np.random.randint(1, 10)])
    return p


def initBase(chunk: list, n: int) -> np.ndarray:
    """สร้างฐาน\n
    รับ chunk ที่จะให้เกิด กับ จำนวนคน\n
    ส่ง Array ของฐาน\n
    ข้อมูล [build?,x,y,capacityNow,capacityMax,full?]
    """
    base = np.array([False,
                    np.random.randint(chunk[0], chunk[2]),
                    np.random.randint(chunk[1], chunk[3]),
                    0,
                    int(0.20*n),
                    False])
    return base


def initZombie(p: np.ndarray) -> np.ndarray:
    """สร้างซอมบี้\n
    รับ คนที่พ่ายแพ้ต่อการสู้\n
    ส่ง Array ของ ซอมบี้\n
    ข้อมูล[inf,x,y,max,vision,bit]
    """
    z = np.array([-1,
                  p[1],
                  p[2],
                  int(p[3]/2),
                  int(p[4]/2),
                  0])
    return z


def arrivedBase(chunk: np.ndarray, cLen: list, base: np.ndarray) -> None:
    """เอาคนเข้าฐาน\n
    รับ คนที่เดินมาถึงฐาน ฐาน\n
    ส่ง ไม่มี\n
    ข้อมูล ไม่มี
    """    
    chunk[cLen[-2]] = np.array([0, 0, 0, 0, 0, 0])
    cLen[-2] -= 1
    base[3] += 1
    
    if (base[3] >= base[4]) : base[5] = True
    return False


def fight(p: np.ndarray, z: np.ndarray) -> bool:
    """คนสู้กับซอมบี้\n
    รับ คน ซอมบี้\n
    ส่ง ผลการต่อสู้\n
    ข้อมูล Trueคนชนะ Falseคนแพ้
    """    
    pr = [1-p[5]/10, p[5]/10]
    r = np.random.choice([0, 1], p=pr)
    if r:
        return True

    z[5] += 1
    return False


# คำนวนระยะห่างระหว่างจุด 2 จุด
def distance(x1, y1, x2, y2): return math.sqrt((y1-y2)**2 + (x1-x2)**2)


def findZombie(e: np.ndarray, p: np.ndarray) -> bool:
    """ค้นหาซอมบี้ที่อยู่ระยะมองเห็น\n
    รับ คน ซอมบี้\n
    ส่ง ผลการค้นหา\n
    ข้อมูล Trueเจอ Falseไม่เจอ
    """ 
    d = distance(p[1], p[2], e[1], e[2])
    if d <= p[4]+e[4]:
        return False

    return True


#สร้างพิกัดใหม่ 8 พิกัดใน 8 ทิศของจุดเดิม
def gen8block(x, y, v): return [[y+v, x-v], [y+v, x], [y+v, x+v], [y, x+v],
                                [y-v, x+v], [y-v, x], [y-v, x-v], [y, x-v]]


def compare8chunk(x1, y1, x2, y2, b): return [
    [b[0][0] > y1, b[0][1] < x1], [b[1][0] > y1, True],
    [b[2][0] > y1, b[2][1] > x2], [True, b[3][1] > x2],
    [b[4][0] < y2, b[4][1] > x2], [b[5][0] < y2, True],
    [b[6][0] < x1, b[6][1] < y2], [True, b[7][1] < x1]]


def newPos(p: np.ndarray, x: int, y: int, mapZ: list, mapZLen: list, cl: list) -> list:
    cy, cx = cl[4], cl[5]
    p8block = gen8block(x, y, p[4])
    comp = compare8chunk(cl[0], cl[1], cl[2], cl[3], p8block).all(axis=1)

    cCheck = gen8block(cx, cy, 1)[comp]
    cCheck.append([cy, cx])

    zombies = []
    for cy, cx in cCheck:
        chunk = mapZ[cy][cx]
        cZLen = mapZLen[cy][cx]
        chunk = chunk[:cZLen[-2]]
        z = list(map(findZombie, chunk,
                     np.full(np.shape(chunk), p)))

        zombies.append([x, y, cZLen, chunk[z]])

    return zombies


def inBlock(
    pos, b): return True if b[0] < pos[0] < b[2] and b[1] < pos[1] < b[3] else False


def genWay(x, y, long, d): return (int(x+long * np.cos(np.rad2deg(d))),
                                   int(y+long * np.sin(np.rad2deg(d))))


def findBlock(x: int, y: int, mapLen: list) -> list:
    for j in mapLen:
        for k in j:
            if inBlock(x, y, k):
                return k


def chooseWay(e: np.ndarray, know: bool, base: np.ndarray, n: int, mapLen: list, mapLenG: list, z: bool) -> list:
    if know:
        way = np.random.randint(0, 360, n)
    else:
        way = np.random.randint(0, 360, 1)

    if z:
        long = np.random.randint(200, e[3])
    else:
        long = np.random.randint(200, e[3])

    allWay = []
    d = []
    for i in way:
        x, y = genWay(e[1], e[2], long, i)
        if not inBlock(x, y, mapLenG):
            x, y = genWay(e[1], e[2], long, i-180)

        w = findBlock(x, y, mapLen)
        if z:
            return (x, y, w)

        w = newPos(e, x, y, mapLen, mapLen, w)
        d.append([len(w[3]), i])
        allWay.append(w)

    if not know:
        return allWay[0]

    d.sort()
    if not base[0] or base[-1]:
        return allWay[d[0][1]]

    dBase1 = distance(allWay[d[0][1]][0], allWay[d[0][1]][1], base[1], base[2])
    dBase2 = distance(allWay[d[1][1]][0], allWay[d[1][1]][1], base[1], base[2])

    if dBase1 <= dBase2:
        return allWay[d[0]]
    return allWay[d[1]]


def regChunk(chunk: np.ndarray, cLen: list) -> list:
    s = (cLen[-1]+1)*2
    chunk.resize(s, 6)
    cLen[-1] = s-1
    return cLen


def moveTo(e: np.ndarray, x: int, y: int, chunk1: list, chunk2: list, mapG: list) -> None:
    mapG[chunk1[4]][chunk1[5]][chunk1[-2]] = np.array([0, 0, 0, 0, 0, 0])
    chunk1[-2] -= 1

    if chunk2[-2] == chunk2[-1]:
        chunk2 = regChunk(mapG[chunk2[4]][chunk2[5]], chunk2)

    e[1], e[2] = x, y
    mapG[chunk2[4]][chunk2[5]][chunk2[-2]+1] = e
    chunk2[-2] += 1


def peopleWalk(p: np.ndarray, chunkNow: np.ndarray, know: bool, base: np.ndarray, mapLen: list, mapLenG: list, mapG: list) -> None:
    way = chooseWay(p, know, base, 4, mapLen, mapLenG, mapG, False)
    nC = way[2]
    moveTo(p, way[0], way[1], chunkNow, nC, mapG)

    if distance(p[1], p[2], base[1], base[2]) <= p[4] and base[0] and not base[-1]:
        arrivedBase(mapG[nC[4]][nC[5]], nC)
        return

    for z in way[-1]:
        if fight(p, z):
            continue
        zombie = initZombie(p)
        mapG[nC[4]][nC[5]][nC[-2]] = zombie
        break


def zombieWalk(z: np.ndarray, chunkNow: list, mapZLen: list, mapZLenG: list, mapZG: list) -> None:
    x, y, nC = chooseWay(z, False, [], 1, mapZLen, mapZLenG, [], True)

    moveTo(z, x, y, chunkNow, nC, mapZG)


def updateEntity(e: np.ndarray, chunkNow: np.ndarray, know: bool, base: np.ndarray, mapLen: list, mapLenG: list, mapG: list) -> None:
    if e[0] == 1:
        peopleWalk(e, chunkNow, know, base, mapLen, mapLen, mapLenG, mapG)
    elif e[0] == -1:
        zombieWalk(e, chunkNow, mapLen, mapLenG, mapG)


plt.show()
