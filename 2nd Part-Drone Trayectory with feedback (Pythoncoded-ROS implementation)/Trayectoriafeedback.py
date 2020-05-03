#!/usr/bin/env python

import rospy
import time
import math
from std_msgs.msg import String 
from std_msgs.msg import Empty 
from geometry_msgs.msg import Twist
from ardrone_autonomy.msg import Navdata
from nav_msgs.msg import Odometry
import numpy as np

def callback(navdata):
    global Yaw, poseZ
    Current_Time = 0.0
    poseZ = navdata.altd
    Yaw = navdata.rotZ
    if poseZ <= 40:
	poseZ = 0
    if (poseZ > 40) or (poseZ < 0):
	poseZ = (poseZ - 40)
    print(poseZ)
    return Yaw, poseZ

def Trayectoria():
	#Tamano de cola o queue size 10, permite que hayan 10 sentencias en cola
    pub = rospy.Publisher("cmd_vel", Twist, queue_size = 10)
    pub2 = rospy.Publisher("ardrone/takeoff", Empty, queue_size = 10 ) 
    pub3 = rospy.Publisher("ardrone/land", Empty, queue_size = 10 )

    #se asigna el atributo tipo Twist a command
    command = Twist()
    Current_Time = 0.0
    Current_Time1 = 0.0
    T = 0

    #Se declara el arreglo de puntos (x, y, z)
    #Coordenadas (1 2 6), (2 3 7), (3 4 6), (4 4 7), (5 4 7), (6 5 6), (6 6 5), (7 7 4), (8 8 3), (8 9 2), (9 9 1)
    Pts=[[0, 0, .85], [1, 1, 6], [2, 2, 6], [2, 3, 6], [3, 4, 7], [4, 5, 6], [5, 6, 5], [6, 7, 4], [7, 6, 3], [8, 6, 3], [9, 6, 3], [9, 6, 2],[10, 7, 1], [10, 8, 1], [9, 9, 1]]
    print(Pts)

    rate = rospy.Rate(10) # 10hz, standard

    while not rospy.is_shutdown():
      while (T < 1):
         #Utilizando funcion de rospy para el tiempo actual
        t0 = rospy.Time.now().to_sec()

	while (Current_Time <= 2):
	#Se da tiempo para el Takeoff
	    pub2.publish(Empty())
	    t1=rospy.Time.now().to_sec()
	    Current_Time = t1-t0
	#Termina Takeoff

        ti = rospy.Time.now().to_sec()

	command.linear.x = 0;
	command.linear.y = 0;
	command.linear.z = 0;

	while (Current_Time1 <= 1.5):
	#Se lanza el Hover
	    pub.publish(command)

	    #Da tiempo para hacer el hover
	    tf=rospy.Time.now().to_sec()
	    Current_Time1 = tf-ti
	#Termina Hover

	print(poseZ)
	print(Yaw)
	while((abs(Yaw)< 0.0 or abs(Yaw)> 0.03) and (poseZ < 835 or poseZ > 865)):
	#Mientras Yaw no sea igual a 0 no va a continuar
	     while(Yaw > 0.01):
		command.angular.z = -.5
		pub.publish(command)
		print(Yaw)
	     while(Yaw < 0.01):
		command.angular.z = .5
		print(Yaw)
		pub.publish(command)

	ti = rospy.Time.now().to_sec()

	command.linear.x = 0;
	command.linear.y = 0;
	command.linear.z = 0;
	command.angular.z = 0;

	while (Current_Time1 <= 1):
	#Se lanza el Hover
	    pub.publish(command)

	    #Da tiempo para hacer el hover
	    tf=rospy.Time.now().to_sec()
	    Current_Time1 = tf-ti
	#Termina Hover

	n = 17 #Numero de coodernadas
        for i in range(0, n-2):

	    r = math.sqrt((Pts[i+1][0]-Pts[i][0])**2+(Pts[i+1][1]-Pts[i][1])**2+(Pts[i+1][2]-Pts[i][2])**2)#r = root((Xi+1-xi)2+(yi+1-yi)2...)
	    print("r", r, i)

	    theta = math.atan2((Pts[i+1][1]-Pts[i][1]),(Pts[i+1][0]-Pts[i][0])) #theta = atan2((Yi+1-yi),(Xi+1-Xi))
	    print("theta", theta, i)

	    #phi = atan2(root((Xi+1-xi)2+(yi+1-yi)2), (zi+1-zi))
	    phi = math.atan2 (math.sqrt((Pts[i+1][0]-Pts[i][0])**2+(Pts[i+1][1]-Pts[i][1])**2), (Pts[i+1][2]-Pts[i][2])) 
	    print("phi", phi, i)
	
	    Vx = math.sin(phi) * math.cos(theta) #Velocidad en X para asignar al drone
	    Vy = math.sin(phi) * math.sin(theta) #Velocidad en Y para asignar al drone
	    Vz = math.cos(phi)		         #Velocidad en Z para asignar al drone
	    print("Vx =", Vx, "Vy = ", Vy, "Vz = ", Vz)

	    Vt = ((Vx)**2+(Vy)**2+(Vz)**2)
	    print("Vt=", Vt)
	
	    Distance = r #Distancia es igual a rho

	    #Se asignan las velocidades en el drone
	    command.linear.x = Vx		
	    command.linear.y = Vy
	    command.linear.z = Vz

	    
	    Current_Distance = 0
            Ti = rospy.Time.now().to_sec()	#Reinicializa TiempoInicial para el siguiente while
	    while((Current_Distance <= Distance) or ((poseZ/1000) != Pts[i+1][2])):
	
                #Publica la velocidad
                pub.publish(command)
                #Toma el tiempo actual
                Tf=rospy.Time.now().to_sec() #Tiempo Final
                #Calcula la distancia actual, teorica
                Current_Distance= Vt*(Tf-Ti)
		#print("Current Distance", Current_Distance)
		#print("Distance", Distance)
		#print("Dx", Vx*Current_Distance)
		#print("Dy", Vy*Current_Distance)
		#print("Dz", Vz*Current_Distance)


            #Hover
            command.linear.x = 0 	
            command.linear.y = 0
            command.linear.z = 0
	    command.angular.z = 0
	
	    Current_Time1 = 0.0

            ti = rospy.Time.now().to_sec()
	    while (Current_Time1 <= 1.5):
	       #Se lanza el hover
	       pub.publish(command)

	       #Da tiempo para hacer el hover
	       tf=rospy.Time.now().to_sec()
	       Current_Time1 = tf-ti
	       #Termina Hover
	    
	T = 1
    rate.sleep() #Hace que el loop se mantenga a 10 Hz





def move_forward():

    	rospy.init_node('Trayectoria', anonymous=True)
    	rospy.Subscriber("/ardrone/navdata", Navdata, callback)
        Trayectoria()
	rospy.spin()


if __name__ == '__main__':

   try: 
       move_forward()
 
   except rospy.ROSInterruptException: 
       pass
