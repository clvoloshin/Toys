'''
Author: Cameron Voloshin
Galton Board
Binomial Distribution converging to Gaussian
'''

import numpy as np
import matplotlib
import pdb
from scipy.stats import norm

from Tkinter import *
import time


WIDTH = 800
HEIGHT = 500


tk = Tk()
n_rows = Scale(tk, from_=0, to=10, orient=HORIZONTAL, tickinterval=2, label = 'Rows of Pegs')
n_rows.set(4)
n_rows.pack()
n_balls = Scale(tk, from_=0, to=400, orient=HORIZONTAL, tickinterval=50, length=600, label = '# balls')
n_balls.set(100)
n_balls.pack()

def reset():
    global world
    canvas.delete("all")
    world = World(2,n_rows.get(),n_balls.get())

def step():
    global world
    world.update()
    tk.update_idletasks()
    tk.update()

def main():
    global world
    while world.is_active():
        world.update()
        tk.update_idletasks()
        tk.update()

def close():
    global tk
    tk.destroy()

Button(tk, text='Step', command=step).place(x=0,y=0)
Button(tk, text='Run', command=main).place(x=75,y=0)
Button(tk, text='Reset', command=reset).place(x=0,y=30)
Button(tk, text='Close', command=close).place(x=75,y=30)

canvas = Canvas(tk, width=WIDTH, height=HEIGHT, bg="grey")
canvas.pack()

class Grid:
    def __init__(self, x_start, y_start, size, num_rows_of_pegs = 5, spacing = 3):
        self.num_rows_of_pegs = num_rows_of_pegs
        self.size_of_pegs = size
        self.pegs = {}
        self.x_start = x_start
        self.y_start = y_start
        self.spacing = spacing
        self.create_grid()

    def create_grid(self):
        for row in range(1,self.num_rows_of_pegs+1):
            centers = [[self.x_start + self.spacing*2*n*self.size_of_pegs, self.y_start] for n in range(row)]
            self.pegs[row] = []
            for peg in range(row):  
                self.pegs[row] += [Peg(centers[peg], self.size_of_pegs, row)]

            self.x_start -= self.spacing*self.size_of_pegs
            self.y_start += self.spacing*self.size_of_pegs

class Peg:
    def __init__(self, center, size, row, color = 'black'):
        self.size = size
        self.center = center
        self.shape = canvas.create_oval(self.center[0]-self.size/2,
                                        self.center[1]-self.size/2, 
                                        self.center[0]+self.size/2,
                                        self.center[1]+self.size/2,
                                        fill=color)
        self.row = row

    def draw(self):
        pass

class Ball:
    def __init__(self, center, size, color = 'blue'):
        self.size = size
        self.center = center
        self.shape = canvas.create_oval(self.center[0]-self.size/2,
                                        self.center[1]-self.size/2, 
                                        self.center[0]+self.size/2,
                                        self.center[1]+self.size/2,
                                        fill=color)
        self.speedx = 0 # changed from 3 to 9
        self.speedy = size # changed from 3 to 9
        self.active = True
        self.row = 1 

    def ball_update(self):
        canvas.move(self.shape, self.speedx, self.speedy)
        pos = canvas.coords(self.shape)
        bottom = False

        if pos[2] >= WIDTH or pos[0] <= 0:
            self.speedx *= 0
        if pos[3] >= HEIGHT or pos[1] <= 0:
            self.speedy *= -1
            self.active = False
            bottom = True

        return bottom

    def hit_peg(self, last_peg, spacing):
        self.row += 1

        if self.speedx == 0:
            self.speedx = 1

        self.speedx = np.random.choice(np.arange(2)*2-1, p = [.5,1-.5]) * self.size
        
        if last_peg:
            for _ in range(spacing):
                self.move_active()
            self.speedx = 0
            self.row = 1
        
    def move_active(self):
        if self.active:
            return self.ball_update()
        else:
            return False
            #tk.after(40, self.move_active) # changed from 10ms to 30ms

    def draw(self):
        pass

class World():
    def __init__(self, spacing=2, num_rows=4, num_balls = 100):

        # size = HEIGHT-20-num_rows*spacing num_balls

        N = num_rows 
        p = .5
        x = np.linspace(0,N,500)
        centered = norm.pdf(x, N*p, np.sqrt(N*p*(1-p)))
        self.size_of_ball = int(50/np.sqrt(num_balls/2))

        gauss = canvas.create_line(zip( (x-N*p)*spacing*2*self.size_of_ball + WIDTH/2., HEIGHT-centered*num_balls*self.size_of_ball), fill='blue')

        self.grid = Grid(WIDTH/2., self.size_of_ball*2, self.size_of_ball, num_rows, spacing)
        self.num_balls = num_balls
        self.balls = [Ball([WIDTH/2.,1], self.size_of_ball)]
        self.active_balls = [x for x,ball in enumerate(self.balls) if ball.active]
        self.wait = 0

        self.top_of_stack = []

    @staticmethod
    def intersection(obj1, obj2):
        obj1_coord = canvas.coords(obj1.shape)
        obj2_coord = canvas.coords(obj2.shape)
        x1 = sum(obj1_coord[::2])/2.
        y1 = sum(obj1_coord[1::2])/2.
        x2 = sum(obj2_coord[::2])/2.
        y2 = sum(obj2_coord[1::2])/2.
        return (abs(x1 - x2) * 2 < (obj1.size + obj1.size)) and (abs(y1 - y2) * 2 <= (obj1.size + obj1.size))

    def update(self):
        for i in self.active_balls:
            ball = self.balls[i]
            row = self.balls[i].row
            for peg in self.grid.pegs[row]:
                if self.intersection(ball, peg):
                    ball.hit_peg(peg.row == self.grid.num_rows_of_pegs, self.grid.spacing)
                    break

        for i in self.active_balls:
            balli = self.balls[i]
            for j, ballj in enumerate(self.top_of_stack):
                if i != j:
                    if self.intersection(balli, ballj):
                        balli.speedx = 0
                        balli.speedy = 0
                        ballj.speedy = 0
                        ballj.speedy = 0
                        balli.active = False
                        ballj.active = False
                        self.top_of_stack[j] = balli
                        break

        for ball in self.balls:
            bottom = ball.move_active()
            if bottom is True:
                self.top_of_stack += [ball]
        for key in self.grid.pegs:
            for peg in self.grid.pegs[key]:
                peg.draw()

        self.wait += 1
        if (self.wait % 2 == 0) and (len(self.balls) < self.num_balls):
            self.balls += [Ball([WIDTH/2.,1], self.size_of_ball)]

        self.active_balls = [x for x,ball in enumerate(self.balls) if ball.active]

    def is_active(self):
        return any([ball.active for ball in self.balls])

world = World(2,n_rows.get(),n_balls.get())
tk.mainloop()




