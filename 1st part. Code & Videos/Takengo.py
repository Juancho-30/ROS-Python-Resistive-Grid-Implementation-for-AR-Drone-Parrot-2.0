#!/usr/bin/env python
import rospy
import time
from std_msgs.msg import String 
from std_msgs.msg import Empty 
from geometry_msgs.msg import Twist

def move_forward():

    #Se inicia el nodo con cualquier nombre y los publicadores
    #Tamano de cola o queue size 10, permite que hayan 10 "sentencias" en cola

    rospy.init_node('Takengo', anonymous=True)
    pub = rospy.Publisher("cmd_vel", Twist, queue_size=10)
    pub2 = rospy.Publisher("ardrone/takeoff", Empty, queue_size=10 ) 
    pub3 = rospy.Publisher("ardrone/land", Empty, queue_size=10 )

    #se asigna el atributo tipo Twist a command
    command = Twist()

    #Distancia y velocidad que quieres que se mueva el drone
    print("El drone se movera hacia delante y aterrizar ")
    speed = input("Introduce la velocidad del drone ")
    distance = input("Introduce la distancia que quieres que se mueva ")

    #Se asigna la velocidad teorica del dron puede ir de (-1 a 1)
    command.linear.x = abs(speed)		
    command.linear.y = 0
    command.linear.z = 0
    command.angular.x = 0
    command.angular.y = 0
    command.angular.z = 0
    current_time = 0
    current_time1 = 0
    current_time2 = 0

    rate = rospy.Rate(10) # 10hz, standard

    while not rospy.is_shutdown():

        #Utilizando funcion de rospy para el tiempo actual
        t0 = rospy.Time.now().to_sec()

	#Poniendo la distancia actual como 0
        current_distance = 0

	while (current_time < 3):
	   #Se lanza el takeoff
       	   pub2.publish(Empty())

	   #Da tiempo para hacer el takeoff, 3 segundos
	   t2=rospy.Time.now().to_sec()
	   current_time = t2-t0

        t0 = rospy.Time.now().to_sec()	#Reinicializa t0 para el siguiente while

        #Hacer un loop para que el drone se mueva la distancia teorica
        while(current_distance < distance):
	
            #Publica la velocidad
            pub.publish(command)
            #Toma el tiempo actual
            t1=rospy.Time.now().to_sec()
            #Calcula la distancia actual, teorica
            current_distance= speed*(t1-t0)
	    #Imprime la distancia actual

        #Despues del loop para que el dron se pare
        command.linear.x = 0 #Velocidad igual a 0

        #Forzarlo a parar y aterrizar
	t0 = rospy.Time.now().to_sec() #Reinicializacion de t0

	while (current_time1 < 2):
	   #Se lanza el hover (Todas las velocidades son iguales a 0)
           pub.publish(command)

	   #Da tiempo para hacer el hover, 2 segundos
	   t2=rospy.Time.now().to_sec()
	   current_time1 = t2-t0

	t0 = rospy.Time.now().to_sec()
	while (current_time2 < 2):
	   #Se lanza el land
	   pub3.publish(Empty())

	   #Da tiempo para hacer el land
	   t2=rospy.Time.now().to_sec()
	   current_time2 = t2-t0


	rate.sleep() #Hace que el loop se mantenga a 10 Hz


if __name__ == "__main__": #Main donde ejecuta la funcion, el except es el ctrl+c
   try: 
       move_forward() 
   except rospy.ROSInterruptException: 
       pass
