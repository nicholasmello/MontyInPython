import math
import time
from rlbot.agents.base_agent import  SimpleControllerState
from Util import *
from enum import Enum, auto

''' KICKOFF STATE '''
class kickoff:
    def __init__(self):
        self.expired = False
    def available(self, agent):
        if agent.me.isRoundActive == False:
            return True
        return False
    def execute(self, agent):
        agent.controller = kickoffController

        if agent.ball.location.data[0] != 0 and agent.ball.location.data[1] != 0:
            global FLIP_CAR_CALLED
            FLIP_CAR_CALLED = False
            self.expired = True # <-- Expired condition is when the ball is no longer in the center of the field for the first time after the round becomes active
        return agent.controller(agent)
        
def kickoffController(agent):
    controller_state = SimpleControllerState()
    localBall = toLocal(agent.ball, agent.me)
    ballDistance = math.sqrt((localBall.data[0])**2+(localBall.data[1])**2)
    controller_state.throttle = 1 # <-- Drive Forward.
    controller_state.boost = 1
    angle_to_ball = math.atan2(localBall.data[1], localBall.data[0])
    controller_state.steer = steer(angle_to_ball) 
    if ballDistance < 900:
        controller_state.boost = 0
        controller_state = flipCar(agent, controller_state, flipDirection.FORWARD) # <-- Flip the car in the forward direction.

    return controller_state

''' RETREAT STATE '''
class retreat:
    def __init__(self):
        self.expired = False
    def available(self,agent):
        if teamify(agent.me.location.data[1], agent) > (agent.ball.location.data[1] + teamify(600, agent)):
            return True
        else:
            return False
    def execute(self,agent):
        agent.controller = retreatController
        target_location = Vector3([0,teamify(-4500, agent),0])
        if teamify(agent.me.location.data[1], agent) < teamify(-2500,agent):
            self.expired = True
        return agent.controller(agent, target_location)

def retreatController(agent, goal):
    location = toLocal(goal,agent.me)
    controller_state = SimpleControllerState()
    angle_to_goal = math.atan2(location.data[1],location.data[0])
    controller_state.steer = steer(angle_to_goal)
    controller_state.throttle = 1

    return controller_state

''' TOWARD BALL STATE '''
class towardball:
    def __init__(self):
        self.expired = False
    def available(self,agent):
        return True
    def execute(self,agent):
        agent.controller = towardballController
        target_location = agent.ball
        target_speed = velocity2D(agent.ball) + (distance2D(agent.ball,agent.me)/1.5)
        self.expired = True
        return agent.controller(agent, target_location, target_speed)

def towardballController(agent, target_object,target_speed):
    location = toLocal(target_object,agent.me)
    controller_state = SimpleControllerState()

    current_speed = velocity2D(agent.me)

    #throttle
    if target_speed > current_speed:
        controller_state.throttle = 1.0
        if agent.ball.location.data[0] > 50 and teamify(agent.me.location.data[1], agent) > agent.ball.location.data[1]:
            location.data[0] = location.data[0] + 200
        elif agent.ball.location.data[0] < -50 and teamify(agent.me.location.data[1], agent) > agent.ball.location.data[1]:
            location.data[0] = location.data[0] - 200
        if target_speed > 1400 and agent.start > 2.2 and current_speed < 2250:
            if agent.ball.location.data[0] > 50 and teamify(agent.me.location.data[1], agent) > agent.ball.location.data[1]:
                location.data[0] = location.data[0] + 300
            elif agent.ball.location.data[0] < -50 and teamify(agent.me.location.data[1], agent) > agent.ball.location.data[1]:
                location.data[0] = location.data[0] - 300
            controller_state.boost = True
    elif target_speed < current_speed:
        controller_state.throttle = 0
        if agent.ball.location.data[0] > 50 and teamify(agent.me.location.data[1], agent) > agent.ball.location.data[1]:
            location.data[0] = location.data[0] + 150
        elif agent.ball.location.data[0] < -50 and teamify(agent.me.location.data[1], agent) > agent.ball.location.data[1]:
            location.data[0] = location.data[0] - 150

    angle_to_ball = math.atan2(location.data[1],location.data[0])
    controller_state.steer = steer(angle_to_ball)

    return controller_state


''' WAIT STATE '''
class wait():
    def __init__(self):
        self.expired = False
    def available(self, agent):
        if timeZ(agent.ball) > 2:
            return True
    def execute(self,agent):
        self.expired = True
        controller_state = SimpleControllerState()
        print("Error: All states bypassed to wait state.")
        return controller_state
