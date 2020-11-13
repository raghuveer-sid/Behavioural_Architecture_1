#!/usr/bin/env python3

'''
In this task ros noetic and python 3 are used.

'''

import rospy
import time
import random
from std_msgs.msg import String
from geometry_msgs.msg import Point

"""
Limit for the layout is set to 0 to 50
A random number is generated between 0 and 50 and assigned to the respective varable

"""

per_x = random.randint(0,50)
per_y = random.randint(0,50)
state = "sleep"
"""

This function decides wether the  person is comanding the dog to either sleep ar to play

"""

def person_command():
    """
    In this function initiate the node person_command
    Checks wether the command is play if it play then sets the position to generated coordinate
    """
    rospy.init_node('person_command', anonymous=True)
    pub_command = rospy.Publisher('command', String, queue_size=1)
    rate = rospy.Rate(200)
    while not rospy.is_shutdown():
        time.sleep(5)
        if rospy.get_param('state') == 'normal':
            voice = random.choice(['play', 'sleep'])
            if (voice == 'play'):
                pub_command.publish(voice)
                rospy.set_param('position_x', per_x)
                rospy.set_param('position_y', per_y)
                time.sleep(5)
                rate.sleep()


def getpoint():
    """
    In getpoint state is checked wether it is in play or not.If its in play then the persons command coordinate is set to pointed locations

    """
    rospy.init_node('getpoint', anonymous=True)
    pub_gesture_loc = rospy.Publisher('command_point', Point, queue_size=1)
    gesture_target = Point()

    while not rospy.is_shutdown():
        if rospy.get_param('state') == 'play':
            gesture_target.x = random.randint(0, 50)
            gesture_target.y = random.randint(0, 50)
            rospy.set_param('pointed_x', gesture_target.x)
            rospy.set_param('pointed_y', gesture_target.y)
            rospy.loginfo('The operator points to a location %i %i',gesture_target.x, gesture_target.y)
            pub_gesture_loc.publish(gesture_target)
            
            rospy.sleep(5)
            

def check_limits(x, y):
    """This method checks if the provided position is reachable

    It checks whether the given coordinates lies in the world described for 
    the experiment.If the given position is not reachable , it provides an 
    error message and will not move to that location.

    """
    if x >= 0 and x <= 50 and y >= 0 and y <= 50:
        return True
    else:
        print('Please give a different coordinate Becuse it is out of bounds')
        return False


def sub_callback(loc):
    """

    This callback function is to check if constrains is satisfied the send the dog to the location
    """
    pub = rospy.Publisher('position', Point, queue_size=1)
    isValid = check_limits(loc.x, loc.y)
    if isValid:
        time.sleep(random.randint(10))
        rospy.loginfo('The robot reached destination %i %i', loc.x, loc.y)
        pub.publish(loc)


def sub_callback_command(command_point):
    """

    This callback function subscribes commanpoint

    """
    pub = rospy.Publisher('position', Point, queue_size=1)
    isValid = check_limits(command_point.x, command_point.y)
    if isValid:
        time.sleep(random.randint(10))
        rospy.loginfo('The robot came to command point %i %i',command_point.x, command_point.y)
        pub.publish(command_point)


def gotopoint():
    """
    In gotopoint node is initialized and topics are subscribed

    """
    rospy.init_node('gotopoint', anonymous=True)
    rospy.Subscriber('control', Point, sub_callback)
    rospy.Subscriber('command_point', Point, sub_callback_command)
    rospy.spin()



if __name__ == '__main__':
    person_command()
    getpoint()
    gotopoint()
