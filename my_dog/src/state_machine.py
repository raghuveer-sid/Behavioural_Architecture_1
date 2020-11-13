#!/usr/bin/env python3

"""
This is a state machine file which changes states between sleep,normal and play

"""

import roslib
import rospy
import smach
import smach_ros
import time
import random
from geometry_msgs.msg import Point
from std_msgs.msg import String

"""
The parameters home_pos_x and home_pos_y gives a rondom destination for home
"""

home_pos_x = random.randint(0,50)
home_pos_y = random.randint(0,50)

"""
The parameters person_pos_x and person_pos_y places the person who is giving the command at a random position every time between the limits i.e, (0,50)

"""

person_pos_x = random.randint(0,50)
person_pos_y = random.randint(0,50)
state = "sleep"

def user_action():
    """This function decides between sleep, normal and play """
    return random.choice(['sleep', 'normal', 'play'])

# Class for Normal state

class Normal(smach.State):
    """

    In Normal state the dog is just moving arount in the laypput and waiting for the persons command
   
    """

    def __init__(self):
        smach.State.__init__(self,
                             outcomes=['gotoSleep', 'gotoPlay'])
        rospy.Subscriber('position', Point, self.Normal_callback)
        rospy.Subscriber('command', String, self.Normal_callback1)
        self.target = Point()

    def Normal_callback(self, arg):
        if(rospy.get_param('state' == 'normal')):
            if(rospy.wait_for_message('position', Point)):
                rospy.set_param('position_x', target.x)
                rospy.set_param('position_y', target.y)

    def Normal_callback1(self, arg):
        if rospy.get_param('state') == 'normal':
            rospy.loginfo('Voice command registered')

    def execute(self, userdata):
        rospy.set_param('state', 'normal')
        rospy.loginfo('NORMAL STATE')
        while (rospy.get_param('state') == 'normal' and not rospy.is_shutdown()):
            pub = rospy.Publisher("control", Point, queue_size=1)
            self.target.x = random.randrange(1, 50, 1)
            self.target.y = random.randrange(1, 50, 1)
            self.target.z = 0
            pub.publish(self.target)
            time.sleep(5)
            state = user_action()
            if(state == 'sleep'):
                return 'gotoSleep'
            elif (state == 'play'):
                return 'gotoPlay'

# Class for Sleep state


class Sleep(smach.State):
    
    """

    In Sleep state the dog goes to the home location and sleeps.This Class initiates and sets the home position and publishes the position to the node 

    """

    def __init__(self):
        smach.State.__init__(self,
                             outcomes=['gotoNormal'])
        rospy.Subscriber('position', Point, self.Sleep_callback)
        self.home_position = Point()

    def Sleep_callback(self, arg):
        rospy.set_param('position_x', home_pos_x)
        rospy.set_param('position_y', home_pos_y)

    def execute(self, userdata):
        rospy.set_param('state', 'sleep')
        rospy.loginfo('SLEEP STATE')
        self.home_position.x = home_pos_x
        self.home_position.y = home_pos_y
        pub = rospy.Publisher("control", Point, queue_size=10)
        pub.publish(self.home_position)
        rospy.sleep(5)
        rospy.loginfo('Dog came to home')
        time.sleep(5)
        return 'gotoNormal'

# Class for Play state


class Play(smach.State):
    """

    In Play state the dog receives a comman from the person and goes to that position if the command is not received after somtime it will go back to normal state

    """

    def __init__(self):
        smach.State.__init__(self,
                             outcomes=['gotoNormal'])

        rospy.Subscriber('command_point', Point, self.Play_callback_gesture)
        self.target = Point()
        self.gesture = Point()

    def execute(self, userdata):
        rospy.set_param('state', 'play')
        pub = rospy.Publisher("control", Point, queue_size=1)
        rospy.loginfo('PLAY STATE')
        while (rospy.get_param('state') == 'play' and not rospy.is_shutdown()):
            self.target.x = random.randint(0,50)
            self.target.y = random.randint(0,50)
            self.target.z = 0
            rospy.loginfo('The dog is sent to position %i %i',
                          self.target.x, self.target.y)
            pub.publish(self.target)
            time.sleep(5)
            return 'gotoNormal'

    def Play_callback_gesture(self, arg):
        if(rospy.get_param('state' == 'play')):
            if(rospy.wait_for_message('position', Point)):
                self.gesture.x = arg.x
                self.gesture.y = arg.y
                rospy.loginfo('the dog reached %i %i',self.gesture.x, self.gesture.y)
                pub.publish(self.gesture)
                time.sleep(5)


def main():
    """

    The main file shows transitions between the three states

    """
    rospy.init_node('state_machine')

    # Create a SMACH state machine
    sm = smach.StateMachine(outcomes=['container_interface'])
    sm.userdata.sm_counter = 0

    # Open the container
    with sm:
        # Add states to the container
        smach.StateMachine.add('SLEEP', Sleep(),
                               transitions={'gotoNormal': 'NORMAL'})
        smach.StateMachine.add('NORMAL', Normal(),
                               transitions={'gotoSleep': 'SLEEP',
                                            'gotoPlay': 'PLAY'})
        smach.StateMachine.add('PLAY', Play(),
                               transitions={'gotoNormal': 'NORMAL'})

    # Create and start the introspection server for visualization
    sis = smach_ros.IntrospectionServer('server_name', sm, '/SM_ROOT')
    sis.start()

    # Execute the state machine
    outcome = sm.execute()

    # Wait for ctrl-c to stop the application
    rospy.spin()
    sis.stop()


if __name__ == '__main__':
    main()
