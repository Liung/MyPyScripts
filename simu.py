#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import sin, cos, pi, atan, asin, acos, sqrt
import itertools
import os
from scipy.interpolate import interp1d

from scipy.fftpack import fft, ifft, fftshift, ifftshift
import numpy as np
from scipy.optimize import leastsq

from matplotlib import rc
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


phi_lst = [-180,-175, -170, -165, -160, -155, -150, -145, -140, -135, -130, -125, -120, -115, -110, -105,-100, -95, -90, -85, -80, -75, -70, -65, -60, -55, -50, -45, -40, -35, -30, -25, -20, -15,  -10,    -5, 0,        5,       10,    15,   20,   25,   30,   35,    40,   45,   50,   55,   60,   65,   70,   75,   80,   85,  90,    95,   100,  105,  110,   115,   120,  125,   130,   135,   140, 145, 150, 155,   160,   165,   170,  175,  180]
Cl_st   = [0.35,1, 1.16, 1.33, 1.68, 1.86,  1.6, 1.32, 0.36,-0.62,-1.16, -1.5,-1.83, -1.7,-1.15,-0.73,-0.2,-0.4,-0.8,-0.8,-0.5,   0,0.28,1.30,1.25,   1,0.53,   0,-0.6,-1.0,-1.2,-1.2,-0.8,-0.5,-0.21,  0.29, 0,     -0.1,     0.43,  0.88, 1.12, 1.48, 1.08, 0.66,   0.3, -0.3, -1.4, -1.9,   -2, -2.4, -2.2, -1.8, -1.6, -1.3,  -1, -0.70, -0.24, 0.23, 0.45,   0.7, 0.875, 0.85,   0.4, -0.04, -0.63,  -1, -1.1, -1, -0.85,  -0.6,  -0.3,  0.2, 0.35]
Clphi   = [1.4, 1.3, 1.16,    2,  2.4,   0,   -3,   -7,  -10,   -7,   -4, -3.5,  -3,    0,  2.9,  3.5,   4,   0,-1.8,   2,   4,   4, 4.6,   0,-2.6,  -4,-4.9,-4.5,-4.3,  -3,-1.3,-0.3, 3.7,   4,  4.6,     2, -1.53,    0,      5.3,     4,  3.8,    0, -3.8,   -4,    -5,   -6, -7.4,  -5 , -2.2,    0,  1.8,  1.8,  1.9,  2.5, 3.7,     4,   4.9,    4,  2.9,     2,   1.4,   -1,  -4.5,    -4,  -3.9,  -1,  0,    1,   3.3,     4,     5,    3,  1.4]
Clp     = [-130, -70,  -3.5,  -60, -160,  10,   53,  250,  400,  300,  200,  100,   7,  -70, -128, -200,-300, -90,  30,  40,  60,-100,-400,   0,160, 220, 305, 225, 155,   0,-100,-100,-108,-130, -160, -100 , -64,   -150,     -210,  -130,  -67,    0,  300,  200,   146,  175,  208,  150,  86,     0, -335, -100,   36,  -30, -70,  -110,  -185, -110,  -71,     0,   106,   30,    38,   100,   163, 100,265,    0,  -160,  -165,  -170, -150, -130]

'''
plt.figure(1)
plt.plot(phi_lst, Cl_st)
plt.ylabel( r'$Cl_{st}$')
plt.xlabel( r'$\phi / ^o$')
plt.figure(2)
plt.plot(phi_lst, Clp)
plt.ylabel( r'$Cl_{p}$')
plt.xlabel( r'$\phi / ^o$')
'''

#几何参数
deg2rad = pi/180.0
rad2deg = 180.0/pi

V = 25
s=0.0005586;        #模型参考面积（m2）
l=0.02667;          #模型展长（m）
ba=0.02667;         #模型平均气动弦长（m）
q=382.8125;         #来流速压（Pa）
dx=-0.04727;        #模型重心距天平中心位置（m）
dy=0.0;             #模型重心距天平中心位置（m）
dz=0.0;             #模型重心距天平中心位置（m）
Ix=1.359E-4         #模型对X轴的转动惯量（kg*m2）

Cl_st = interp1d(phi_lst, Cl_st)
Clp = interp1d(phi_lst, Clp)
pmax = interp1d([-180, -135, -90, -45,   0,  45,  90, 135, 180], \
                [ 300,  300, 350, 350, 350, 300, 400, 600, 600])

#resets = [[-140,10], [-45, 10], [45, -10], [140, 10],[-180,-50],[-180, 150],[-180, 450] , [-42, 258], [80, 600], [-160,20]]
#resets = [[-140,10],[-141,9],[-142,8],[-141.5,9], [-45,5],[-45,7],[-45,9],[-45,11],[44.3,5],[43.45,5],[43.15,5],[43,5],[42.7,5],[135.9,9],[136.2,9],[136.4,9],[136.7,9], [46,600], [46,650], [0,-60]]
#resets = [[-140,10],[-141,9],[-142,8],[-141.5,9], [-45,5],[-45,7],[-45,9],[-45,11],[44.3,5],[43.45,5],[43.15,5],[43,5],[42.7,5],[135.9,9],[136.2,9],[136.4,9],[136.7,9], [46,600], [46,650], [0,-60]]
resets = [[0,50],[42,0], [-50, 0], [100,100], [135,30], [105,200]]
dt = 0.005

plt.figure(3)
plt.ylabel( r'$p / ^o/s$')
plt.xlabel( r'$\phi / ^o$')
plt.figure(4)
plt.ylabel( r'$\phi / ^o$')
plt.xlabel( r'$t / s$')
for inits in resets :
    phi_hist = []
    p_hist = []
    t_hist = []
    phi = inits[0]
    p = inits[1]
    t = 0
    for i in xrange(2000) :
       phi_hist.append(phi)
       p_hist.append(p)
       t_hist.append(t)
       phi += p * dt
       while phi > 180 :
           phi -= 360
       while phi < -180 :
           phi += 360
       pbar = p*deg2rad*l/(2*V)
       Clpc = Clp(phi)
       if Clpc > 0 :
           Clpc = Clpc*(1-(p/pmax(phi))**2)
       pdot = q*s*l*(Cl_st(phi)+Clpc*pbar)/Ix
       p += pdot * rad2deg * dt
       t += dt
       if abs(p)>1000 :
           break
       if abs(pdot)<1e-2 and abs(p)<1e-2 :
           break
    plt.figure(3)
    plt.plot(phi_hist, p_hist, '.')
    plt.figure(4)
    plt.plot(t_hist, phi_hist, '.')

plt.show()

