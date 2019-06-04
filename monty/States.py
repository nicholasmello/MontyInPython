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
    global KICKOFFOFFSET
    localBall = toLocal(agent.ball, agent.me)
    localDistance = math.sqrt((localBall.data[0])**2+(localBall.data[1])**2)
    controller_state.throttle = 1
    if agent.me.istouching:
        controller_state.boost = 1
    else:
        controller_state.boost = 0
    localAngle = math.atan2(localBall.data[1], localBall.data[0])
    if KICKOFFOFFSET == "Close":
        controller_state.boost = 1
        controller_state.throttle = 1
        if localDistance < 1350:
            controller_state.steer = steer(localAngle)/1.5
        if localDistance < 750:
            controller_state = flipCar(agent, controller_state, flipDirection.FORWARD, 1)
    elif KICKOFFOFFSET == "Far":
        if localDistance < 1100:
            controller_state.steer = steer(localAngle)
            controller_state = flipCar(agent, controller_state, flipDirection.FORWARD, 1.3)
        elif localDistance < 3750:
            controller_state = flipCar(agent, controller_state, flipDirection.FORWARD, 1.3)
        elif localDistance > 3750:
            controller_state.steer = steer(localAngle)
    else:
        if localDistance < 1100:
            controller_state.steer = steer(localAngle)
            controller_state = flipCar(agent, controller_state, flipDirection.FORWARD, 1.5)
        elif localDistance < 3500:
            controller_state = flipCar(agent, controller_state, flipDirection.FORWARD, 1.5)
        elif localDistance > 3500:
            controller_state.steer = steer(localAngle)
    if round(localDistance) == 3278 and agent.me.isRoundActive == False:
        KICKOFFOFFSET = "Close"
    elif localDistance > 3900 and agent.me.isRoundActive == False:
        KICKOFFOFFSET = "Far"
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


''' OFFENSIVE CORNER STATE '''
class offensiveCorner:
    def __init__(self):
        self.expired = False
    def available(self, agent):
        if abs(agent.ball.location.data[0]) < 4120 and abs(agent.ball.location.data[0]) > 2400 and agent.ball.location.data[1] > teamify(2000, agent):
            return True
        return False
    def execute(self, agent):
        agent.controller = offensiveCornerController
        if agent.ball.location.data[0] >= 0:
            midField = Vector3([2000,teamify(200, agent),0])
        else:
            midField = Vector3([-2000,teamify(200, agent),0])
        prediction_slice60 = agent.ball.ball_prediction.slices[60]
        location60 = prediction_slice60.physics.location
        if abs(location60.x) < 2000 or location60.y < teamify(2250, agent):
            self.expired = True
        return agent.controller(agent, midField)

def offensiveCornerController(agent, mid):
    controller_state = SimpleControllerState()
    localMid = toLocal(mid, agent.me)
    localAngle = math.atan2(localMid.data[1], localMid.data[0])
    localDistance = math.sqrt((localMid.data[0])**2+(localMid.data[1])**2)
    controller_state.steer = steer(localAngle)
    if localDistance > 1250:
        controller_state.throttle = 1
    elif localDistance > 500:
        controller_state.throttle = .2
    else:
        controller_state.throttle = 0
    return controller_state


''' CENTER ATTACK STATE '''
class centerAttack:
    def __init__(self):
        self.expired = False
    def available(self, agent):
        if teamify(agent.ball.location.data[1], agent) > 200:
            return True
        return False
    def execute(self, agent):
        agent.controller = centerAttackController
        if abs(agent.ball.location.data[0]) < 4120 and abs(agent.ball.location.data[0]) > 2400 and agent.ball.location.data[1] > teamify(2000, agent):
            cornerCondition = True
        else:
            cornerCondition = False
        if teamify(agent.ball.location.data[1], agent) < 200 or cornerCondition == True:
            self.expired = True
        return agent.controller(agent)

def centerAttackController(agent):
    controller_state = SimpleControllerState()
    velocityMagnitude = math.sqrt(agent.ball.velocity.data[0]**2+agent.ball.velocity.data[1]**2)
    prediction_slice = agent.ball.ball_prediction.slices[int(round(velocityMagnitude/100))]
    location = prediction_slice.physics.location
    localBall = toLocal(Vector3([location.x,location.y,location.z]), agent.me)
    localDistance = math.sqrt((localBall.data[0])**2+(localBall.data[1])**2)
    localAngle = math.atan2(localBall.data[1], localBall.data[0])
    controller_state.throttle = 1 # abs(abs(localAngle/math.pi)-1)
    if teamify(agent.ball.location.data[1], agent) > teamify(agent.me.location.data[1], agent):
        controller_state.steer = steer(localAngle)
        if localDistance < 500:
            if localAngle <= .3 and -.3 <= localAngle:
                controller_state = flipCar(agent, controller_state, flipDirection.FORWARD, 2)
            elif localAngle <= (math.pi / 2) and 1.14 <= localAngle:
                controller_state = flipCar(agent, controller_state, flipDirection.RIGHT, 2)
            elif localAngle <= -1.14 and -(math.pi / 2) <= localAngle:
                controller_state = flipCar(agent, controller_state, flipDirection.LEFT, 2)
            elif localAngle <= 1.14 and .3 <= localAngle:
                controller_state = flipCar(agent, controller_state, flipDirection.FRONT_RIGHT, 2)
            elif localAngle <= -.3 and -1.14 <= localAngle:
                controller_state = flipCar(agent, controller_state, flipDirection.FRONT_LEFT, 2)
    else:
        controller_state = retreatController(agent, Vector3([0,teamify(-4500, agent),0]))
    if localDistance > 2000:
        controller_state.boost = 1
    else:
        controller_state.boost = 0
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
        if abs(agent.ball.location.data[0]) < 1300 or agent.ball.location.data[1] > teamify(-2250, agent):
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
                controller_state = flipCar(agent, controller_state, flipDirection.FORWARD, 1)
            elif localAngle <= (math.pi / 2) and 1.14 <= localAngle:
                controller_state = flipCar(agent, controller_state, flipDirection.RIGHT, 1)
            elif localAngle <= -1.14 and -(math.pi / 2) <= localAngle:
                controller_state = flipCar(agent, controller_state, flipDirection.LEFT, 1)
            elif localAngle <= 1.14 and .3 <= localAngle:
                controller_state = flipCar(agent, controller_state, flipDirection.FRONT_RIGHT, 1)
            elif localAngle <= -.3 and -1.14 <= localAngle:
                controller_state = flipCar(agent, controller_state, flipDirection.FRONT_LEFT, 1)
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
    controller_state = SimpleControllerState()
    location = toLocal(agent.ball,agent.me)
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


class testingState:
    def __init__(self):
        self.expired = False
    def available(self, agent):
        return True
    def execute(self, agent):
        agent.controller = testingStateController
        changeBotState("Error: Testing State Triggered")
        # Testing Half Flip Ability
        return agent.controller(agent)

def testingStateController(agent):
    controller_state = SimpleControllerState()
    #controller_state = retreatController(agent, Vector3([0,0,0]))
    global FLIP_CAR_CALLED
    global FLIP_CAR_START
    if FLIP_CAR_CALLED == False:
        FLIP_CAR_START = time.time() - agent.start
    FLIP_CAR_CALLED = True
    diff = (time.time() - agent.start) - FLIP_CAR_START

    if diff <= 0.1:
        controller_state.jump = True
        controller_state.pitch = 1
    elif diff >= 0.1 and diff <= 0.15:
        controller_state.jump = False
        controller_state.boost = 0
        controller_state.pitch = 1
    elif diff > 0.15 and diff < 0.35:
        controller_state.jump = True
        controller_state.boost = 0
        controller_state.pitch = 1
    elif diff > 0.35 and diff < .7:
        controller_state.pitch = -1
    elif diff > .7 and diff < 2:
        controller_state.pitch = -1
        if agent.me.rotation.data[2] > .1:
            controller_state.roll = -1
        if agent.me.rotation.data[2] < -.1:
            controller_state.roll = 1
    else:
        FLIP_CAR_CALLED = False
    controller_state.yaw = 0
    #controller_state.throttle = 1
    return controller_state