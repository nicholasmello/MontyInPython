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
            self.expired = True
        return agent.controller(agent)
        
def kickoffController(agent):
    controller_state = SimpleControllerState()
    localBall = toLocal(agent.ball, agent.me)
    localDistance = math.sqrt((localBall.data[0])**2+(localBall.data[1])**2)
    controller_state.throttle = 1 # <-- Drive Forward.
    controller_state.boost = 1
    localAngle = math.atan2(localBall.data[1], localBall.data[0])
    controller_state.steer = steer(localAngle) 
    if localDistance < 900:
        controller_state.boost = 0
        controller_state = flipCar(agent, controller_state, flipDirection.FORWARD)
    return controller_state


''' FALLING STATE '''
class falling:
    def __init__(self):
        self.expired = False
    def available(self,agent):
        if agent.me.istouching:
            return False
        return True
    def execute(self,agent):
        agent.controller = fallingController
        if agent.me.istouching:
            self.expired = True
        return agent.controller(agent)

def fallingController(agent):
    controller_state = SimpleControllerState()
    controller_state.throttle = 1
    if agent.me.rotation.data[2] > .1:
        controller_state.roll = -1
    if agent.me.rotation.data[2] < -.1:
        controller_state.roll = 1
    return controller_state


''' FLIP ATTACK STATE '''
class flipAttack:
    def __init__(self):
        self.expired = False
    def available(self, agent):
        if teamify(agent.ball.location.data[1], agent) > 200:
            return True
        return False
    def execute(self, agent):
        agent.controller = flipAttackController
        if teamify(agent.ball.location.data[1], agent) < 200:
            self.expired = True
        return agent.controller(agent)

def flipAttackController(agent):
    controller_state = SimpleControllerState()
    localBall = toLocal(agent.ball, agent.me)
    localAngle = math.atan2(localBall.data[1], localBall.data[0])
    localDistance = math.sqrt((localBall.data[0])**2+(localBall.data[1])**2)
    controller_state.throttle = abs(abs(localAngle/math.pi)-1)
    controller_state.steer = steer(localAngle)
    if localAngle <= 30 and localDistance >= 2000:
        controller_state.throttle = 1
        controller_state.boost = 1
    if localAngle <= math.pi/2 and -math.pi/2 <= localAngle:
        controller_state = flipCar(agent, controller_state, chooseflip(localAngle))
    return controller_state


''' DEFENSIVE CORNER STATE '''
class defensiveCorner:
    def __init__(self):
        self.expired = False
    def available(self, agent):
        if abs(agent.ball.location.data[0]) < 4120 and abs(agent.ball.location.data[0]) > 1300 and agent.ball.location.data[1] < teamify(-2250, agent):
            return True
        return False
    def execute(self, agent):
        agent.controller = defensiveCornerController
        if abs(agent.ball.location.data[0]) > 4120 and abs(agent.ball.location.data[0]) < 1300 and agent.ball.location.data[1] > teamify(-2250, agent):
            self.expired = True
        return agent.controller(agent)

def defensiveCornerController(agent):
    controller_state = SimpleControllerState()
    localBall = toLocal(agent.ball, agent.me)
    localDistance = math.sqrt((localBall.data[0])**2+(localBall.data[1])**2)
    localAngle = math.atan2(localBall.data[1], localBall.data[0])
    controller_state.throttle = abs(abs(localAngle/math.pi)-1)
    if teamify(agent.me.location.data[1], agent) < teamify(-5140, agent):
        controller_state.throttle = .15
        steer(math.atan2(teamify(-5100, agent), 0))
    if abs(agent.me.location.data[0]) < abs(agent.ball.location.data[0]) and teamify(agent.me.location.data[1], agent) < teamify(agent.ball.location.data[1], agent):
        inPosition = True
    else:
        inPosition = False
    if inPosition == True:
        controller_state.steer = steer(localAngle)
        if localDistance < 500:
            if localAngle <= .3 and -.3 <= localAngle:
                controller_state = flipCar(agent, controller_state, flipDirection.FORWARD)
            elif localAngle <= (math.pi / 2) and 1.14 <= localAngle:
                controller_state = flipCar(agent, controller_state, flipDirection.RIGHT)
            elif localAngle <= -1.14 and -(math.pi / 2) <= localAngle:
                controller_state = flipCar(agent, controller_state, flipDirection.LEFT)
            elif localAngle <= 1.14 and .3 <= localAngle:
                controller_state = flipCar(agent, controller_state, flipDirection.FRONT_RIGHT)
            elif localAngle <= -.3 and -1.14 <= localAngle:
                controller_state = flipCar(agent, controller_state, flipDirection.FRONT_LEFT)
    else:
        controller_state = retreatController(agent, Vector3([0,teamify(-4500, agent),0]))
    return controller_state


''' RETREAT STATE '''
class retreat:
    def __init__(self):
        self.expired = False
    def available(self, agent):
        if teamify(agent.me.location.data[1], agent) > (agent.ball.location.data[1] + teamify(600, agent)):
            return True
        else:
            return False
    def execute(self, agent):
        agent.controller = retreatController
        retreatPoint = Vector3([0,teamify(-4500, agent),0])
        if teamify(agent.me.location.data[1], agent) < teamify(-2500,agent):
            self.expired = True
        return agent.controller(agent, retreatPoint)

def retreatController(agent, retreatPoint):
    controller_state = SimpleControllerState()
    localRetreatPoint = toLocal(retreatPoint, agent.me)
    localAngle = math.atan2(localRetreatPoint.data[1],localRetreatPoint.data[0])
    controller_state.steer = steer(localAngle)
    controller_state.throttle = 1
    if localAngle <= .3 and -.3 <= localAngle:
        controller_state.boost = 1
    else:
        controller_state.boost = 0
    return controller_state


''' TOWARD BALL STATE '''
class towardball:
    def __init__(self):
        self.expired = False
    def available(self, agent):
        return True
    def execute(self, agent):
        agent.controller = towardballController
        speed = velocity2D(agent.ball) + (distance2D(agent.ball,agent.me)/1.5)
        self.expired = True
        return agent.controller(agent, speed)

def towardballController(agent, target_speed):
    location = toLocal(agent.ball,agent.me)
    controller_state = SimpleControllerState()
    current_speed = velocity2D(agent.me)
    localAngle = math.atan2(location.data[1],location.data[0])
    controller_state.steer = steer(localAngle)
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
    return controller_state


''' WAIT STATE '''
class wait():
    def __init__(self):
        self.expired = False
    def available(self, agent):
        if timeZ(agent.ball) > 2:
            return True
    def execute(self, agent):
        controller_state = SimpleControllerState()
        print("Error: All states bypassed to wait state.")
        self.expired = True
        return controller_state