#!/usr/bin/env python

import roslib; roslib.load_manifest('r5cop_state_machines')
import rospy
from zmq_object_exchanger import zmqObjectExchanger
import time
import tf
import actionlib
import frontier_exploration.msg
from robot_position import robotPosition
    
class PR2RobotBrain():

    def __init__(self, boundary, center):
    
        self.tfl = tf.TransformListener()
        
        self.comm = zmqObjectExchanger("PR2", "pr2", 1234)
        self.comm.zmq.add_remote("Toad", "toad", 1234)
        
        self.boundary = boundary
        self.center = center
        self.action_client = actionlib.SimpleActionClient('explore_server', frontier_exploration.msg.ExploreTaskAction)
        
        rospy.Timer(rospy.Duration(0.25), outDataTimer)
        rospy.Timer(rospy.Duration(0.25), inDataTimer)
        
        self.stop_exploring = False
        
    def getReady(self):
    
        self.action_client.wait_for_server()
    
    def outDataTimer(self, evt):
    
        now = rospy.time.now()
        ps = robotPosition(self.tfl).get(now)
        
        msg = {}
        
        msg['robot_position'] = ps
        msg['current_state'] = "exploring"
        
        self.comm.send_msg("state_info", msg)
        
    def inDataTimer(self, evt):
    
        msgs = self.comm.get_msgs()
        
        for msg in msgs:
        
            rospy.loginfo(msg["name"] + ": " + msg["topic"])
        
            if msg["topic"] == "state_info":
            
                # TODO store it somehow
                pass            
    
    def explorationFeedbackCallback(self, fb):
  
        pass
        
    def explore(self):
    
        while not self.stop_exploring:
    
            goal = frontier_exploration.msg.ExploreTaskGoal()
            goal.explore_boundary = self.boundary
            goal.explore_center = self.center
            
            self.action_client.send_goal(goal, explorationFeedbackCallback)
            
            while not (self.stop_exploring or self.client.wait_for_result(time.Duration(0.25))):
            
                if self.stop_exploring:
                    self.action_client.cancel_goal()
                    
        self.stop_exploring = False
    
def main():
  
    rospy.init_node('pr2_state_machine')
    brain = PR2RobotBrain()
    brain.getReady()
    
    rospy.spin()
    
if __name__ == '__main__':
    main()
