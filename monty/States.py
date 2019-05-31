import math
import time
from rlbot.agents.base_agent import  SimpleControllerState
from Util import *
from enum import Enum, auto


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
            self.expired = True
        return agent.controller(agent)
        
def kickoffController(agent):
    controller_state = SimpleControllerState()
    localBall = toLocal(agent.ball, agent.me)
    controller_state.throttle = 1
    flipCar(agent, controller_state, flipDirection.FORWARD)

    return controller_state

class towardball:
    def __init__(self):
        self.expired = False
    def available(self,agent):
        return True
    def execute(self,agent):
        agent.controller = towardballController
        target_location = agent.ball
        target_speed = velocity2D(agent.ball) + (distance2D(agent.ball,agent.me)/1.5)
        
        return agent.controller(agent, target_location, target_speed)

def towardballController(agent, target_object,target_speed):
    location = toLocal(target_object,agent.me)
    controller_state = SimpleControllerState()
    angle_to_ball = math.atan2(location.data[1],location.data[0])

    current_speed = velocity2D(agent.me)
    #steering
    controller_state.steer = steer(angle_to_ball)

    #throttle
    if target_speed > current_speed:
        controller_state.throttle = 1.0
        if target_speed > 1400 and agent.start > 2.2 and current_speed < 2250:
            controller_state.boost = True
    elif target_speed < current_speed:
        controller_state.throttle = 0

    return controller_state

class wait():
    def __init__(self):
        self.expired = False
    def available(self, agent):
        if timeZ(agent.ball) > 2:
            return True
    def execute(self,agent):
        
        self.expired = True
        controller_state = SimpleControllerState()

        return controller_state
