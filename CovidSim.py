from itertools import product
import numpy as np
import matplotlib.pyplot as plt
import random
import sys

π = np.pi

class Hito:
    
    def __init__(self,CI, status, rad = 0.002):
        
        # 0 < x,y,θ < 1 : Initial position and direction
        # θ must me multiplied by 2π in order to indicate correctly the direction
        
        x,y,θ = CI
        self.x, self.y = x,y
        self.vx, self.vy = np.cos(2*π*θ), np.sin(2*π*θ)
        
        self.Rad = rad
        self.status = status

        self.CS = 0
        
    def Move(self):
        dt = 0.003
        
        if 0 < self.x + self.vx*dt < 1:
            
            # Trayectoria usual
            self.x = self.x + self.vx*dt
            
        else:
            # Choque contra una pared
            self.vx = -self.vx
            self.x = self.x + self.vx*dt
        
        if 0 < self.y + self.vy*dt < 1:
            
             # Trayectoria usual
            self.y = self.y + self.vy*dt
        else:
            
             # Choque contra una pared
            self.vy = -self.vy
            self.y = self.y + self.vy*dt

        # Posibilidad arbitraria de recuperarse
        if self.status == "SICK": 
            self.status = random.choices( population=["SICK", "Recovered"], weights=[0.999, 0.001])[0]            
                    
class Population:
    
    def __init__(self,N,Arel):
        
        n  = 0
        self.CN = 0
        self.Arel = Arel
        R = np.sqrt(self.Arel/π/N)  # Particle radius
                
        while True:
            
            self.Citizens = [ Hito(np.random.rand(3),status = "Healthy",rad = R) for _ in range(N-1)]
            self.Citizens.append( Hito(np.random.rand(3),status = "SICK",rad = R))
                        
            if len(self.CheckPositions()) == 0: break
            n += 1

            if n == 1000:
                print ("It took too much tries, bye")
                sys.exit()
            
        print ("It took",n,"tries to initialize the population" )
  

    def CheckPositions(self):
        
        CTuple = []
        for i,j in product(range(N),range(N)):
            if i>j:
                
                # Coordinates
                xi, xj = self.Citizens[i].x , self.Citizens[j].x
                yi, yj = self.Citizens[i].y , self.Citizens[j].y
                R = self.Citizens[i].Rad
                
                if np.sqrt((xi-xj)**2 + (yi-yj)**2 ) < 2*R: CTuple.append((i,j))
        return CTuple           
    
    def Move(self):
        
        N =  len(self.Citizens)
        for i in range(N) : self.Citizens[i].Move()
            
        Ctuple = self.CheckPositions()
        
        for i,j in Ctuple:
            
            # CITIZEN I and CITIZEN J have COLLIDED: WE ENTER IN COLLISION SITUATION 
            
            self.Citizens[i].vx , self.Citizens[j].vx = self.Citizens[j].vx , self.Citizens[i].vx
            self.Citizens[i].vy , self.Citizens[j].vy = self.Citizens[j].vy , self.Citizens[i].vy
            
            if sorted([self.Citizens[i].status,self.Citizens[j].status]) == ['Healthy', 'SICK']:
                self.Citizens[i].status = "SICK"
                self.Citizens[j].status = "SICK"
            
            self.CN += 1
            self.Citizens[i].CS += 1 ; self.Citizens[j].CS += 1
            
        # Anticonstrains protocol
        
        if len(Ctuple) == 0:
            for cit in self.Citizens: cit.CS = 0

        for cit in self.Citizens:
            if cit.CS > 10:
                d = np.random.random()*2*π
                cit.vx = np.cos(d) ; cit.vy = np.sin(d)
                 
    def Simulate(self,epochs):

        self.epochs = epochs
        X, Y, St = [], [], []
        self.Healthy, self.Sick, self.Recovered = [],[],[]
        
        for e in range(epochs):
            
            X.append([cit.x for cit in self.Citizens])
            Y.append([cit.y for cit in self.Citizens])
            St.append([cit.status for cit in self.Citizens])

            unique, counts = np.unique(St[e], return_counts=True)
            CounterDict = dict(zip(unique,counts))

            try: H = CounterDict['Healthy']
            except KeyError:H = 0
            try: S = CounterDict['SICK']
            except KeyError:S = 0
            try: R = CounterDict['Recovered']
            except KeyError:R = 0

            self.Healthy.append(H)
            self.Sick.append(S)
            self.Recovered.append(R)    

            if e%100 == 0: print ("Epoch=",e)
            
            self.Move()
            
        X = np.array(X) ; Y = np.array(Y) ; St = np.array(St)
        self.XData = X ; self.YData = Y ; self.SData = St
        
        print ("There will be",self.CN,"collisions")   


    def PlotStatusProgression(self):

        plt.plot(self.Healthy,label="Healthy", color = "yellow" )
        plt.plot(self.Sick,label="SICK",color = "black")
        plt.plot(self.Recovered,label="Recovered",color = "blue")
        plt.legend(loc ="upper left")

        plt.title("Population status evolution",fontsize=14)
        plt.grid()
        plt.xlabel("Epoch",fontsize = 12)
        plt.ylabel("Number of citizens",fontsize=12)

        plt.show()


    def Colormapping(self,Status):
    
        if Status == "SICK": return 0               # Purple
        elif Status == "Healthy": return 0.5        # Yellow
        elif Status == "Recovered":  return 0.3     # Kind of blue (?)


    def update_plot(self,i,X,Y,Status,scat):

        # Axis 1
        scat.set_offsets(np.array([X[i],Y[i]]).T)
        scat.set_array( np.array(list(map(self.Colormapping,Status[i]))) )
        
        self.info.set_text( '\n'.join(( 'Epoch={}'.format(i),
                                        'Healthy = {}'.format(self.Healthy[i]),
                                        'Sick = {}'.format(self.Sick[i]),
                                        'Recovered = {}'.format(self.Recovered[i]) )))
        
        # Axis 2
        
        self.lineH.set_data(range(i),[self.Healthy[:i]])
        self.lineS.set_data(range(i),[self.Sick[:i]])
        self.lineR.set_data(range(i),[self.Recovered[:i]])
        
        if i > 2:
        
            self.ax2.set_xlim(0,self.epochs)
            self.ax2.set_ylim(0,len(self.Citizens))
        
        return scat, self.info, self.lineH, self.lineS, self.lineR,

    def Animate(self):
        
        from matplotlib import animation, rc
        X,Y, Status = self.XData , self.YData , self.SData

        fig = plt.figure(figsize = (10,5))
        self.ax1 = fig.add_subplot(121)

        # Axis 1
        
        self.ax1.set_aspect("equal")

        R = self.Citizens[0].Rad
        vmin, vmax, ext = 0,1,R

        self.ax1.set_xlim(vmin-ext,vmax+ext)
        self.ax1.set_ylim(vmin-ext,vmax+ext)
        self.ax1.set_xticks([]) ; self.ax1.set_yticks([])
        
        self.info = self.ax1.text(0.02,0.82,"",transform = self.ax1.transAxes, fontsize = 9)
        s = ((self.ax1.get_window_extent().width  / (vmax-vmin+2*ext) * 72./fig.dpi) ** 2)
        scat = self.ax1.scatter(X[0],Y[0],s= (2*R)**2 *s)

        # Axis 2

        self.ax2 = fig.add_subplot(122)       

        self.ax2.set_xlabel("Epoch",fontsize=10)
        self.ax2.set_ylabel("Number of citizens",fontsize=10)

        self.lineH, = self.ax2.plot([],[],color = "#FEFE0F",label="Healthy")
        self.lineS, = self.ax2.plot([],[],color = "#6D2D5A",label="Sick")
        self.lineR, = self.ax2.plot([],[],color = "#3DA8A6",label="Recovered")
        
        self.ax2.set_xticks(np.linspace(0,self.epochs,5,endpoint=True))
        self.ax2.set_yticks(np.linspace(0,len(self.Citizens),5,endpoint=True))
        
        self.ax2.grid(True)

        fig.canvas.draw()
        
        ani = animation.FuncAnimation(fig, self.update_plot, frames = self.epochs, blit = True,
                                      interval = 5, fargs=(X,Y,Status,scat))

        plt.show()

        a = input("Wanna save (y/n)?")

        if a == "y":

            Writer = animation.writers['ffmpeg']
            writer = Writer(fps=60, metadata=dict(artist='Me'), bitrate=1800)
        
            ani.save('ani.mp4',writer = writer)

######################################################################################################
# Partes modificables del programa

N = 40          # Numero de particulas
E = 2000        # Numero de epocas
A = 0.05        # Area relativa cubierta por bolitas

#####################################################################################################

Popp = Population(N,Arel=A)
Popp.Simulate(E)
Popp.Animate()
Popp.PlotStatusProgression()


