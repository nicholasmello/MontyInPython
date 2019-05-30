import math
import time
from rlbot.agents.base_agent import  SimpleControllerState
from Util import *


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

    #dodging
    time_difference = time.time() - agent.start
    if time_difference > 2.2 and distance2D(target_object,agent.me) > (velocity2D(agent.me)*2.5) and abs(angle_to_ball) < 1.3:
        agent.start = time.time()
    elif time_difference <= 0.1:
        controller_state.jump = True
        controller_state.pitch = -1
    elif time_difference >= 0.1 and time_difference <= 0.15:
        controller_state.jump = False
        controller_state.pitch = -1
    elif time_difference > 0.15 and time_difference < 1:
        controller_state.jump = True
        controller_state.yaw = controller_state.steer
        controller_state.pitch = -1

    return controller_state


class wait():
    def __init__(self):
        self.expired = False
    def available(self, agent):
        if timeZ(agent.ball) > 2:
            return True
    def execute(self,agent):
        #taking a rough guess at where the ball will be in the future, based on how long it will take to hit the ground
        ball_future = future(agent.ball, timeZ(agent.ball))
        if agent.me.boost < 35: #if we are low on boost, we'll go for boot
            closest = 0
            closest_distance =  distance2D(boosts[0], ball_future) 

            #going through every large pad to see which one is closest to our ball_future guesstimation
            for i in range(1,len(boosts)):
                if distance2D(boosts[i], ball_future) < closest_distance:
                    closest = i
                    closest_distance =  distance2D(boosts[i], ball_future)

            target = boosts[closest]
            speed = 2300
        else:
            #if we have boost, we just go towards the ball_future position, and slow down just like in exampleATBA as we get close
            target = ball_future
            current = velocity2D(agent.me)
            ratio = distance2D(agent.me,target)/(current + 0.01)
            
            speed = cap(600 * ratio,0,2300)
        if speed <= 100:
            speed = 0

        if agent.ball.location.data[2] < 170:
            self.expired = True

        return frugalController(agent,target,speed)
