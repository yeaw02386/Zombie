from ClassLib import *
import matplotlib.pyplot as plt
from matplotlib import animation, rc
from IPython.display import HTML

people = Map(False,0,0,3000,3000,100,4000)
zombie= Map(True,0,0,3000,3000,100,4000)
base = Base(1500,1000,400)

zombie.genZombie()

fig, ax = plt.subplots()
plt.close()
ax.set_xlim((0, 3000))
ax.set_ylim((0, 3000))

peoplePlot, = ax.plot([],[],'c.')
zombiePlot, = ax.plot([],[],'r.')
basePlot, = ax.plot([],[],'yo',)

def init():
    px,py = people.getData()
    zx,zy = zombie.getData()
    
    peoplePlot.set_data(px,py)
    zombiePlot.set_data(zx,zy)
    
def animate(i):
    if (i >= 8): 
        base.build = True 
    if (i >= 4): people.know= True
    
    
    people.update(base,zombie)
    zombie.update()
    
    px,py = people.getData()
    zx,zy = zombie.getData()

    peoplePlot.set_data(px,py)
    zombiePlot.set_data(zx,zy)
    
    if base.build :
        basePlot.set_data([base.x],[base.y])
    
    print(len(px),len(zx),base.now)
    return (peoplePlot,zombiePlot,basePlot)
    

n = 30
anim = animation.FuncAnimation(fig, animate, frames=n, interval=1000, blit=False)

anim.save('growingCoil.mp4', writer = 'ffmpeg', fps = 5)


