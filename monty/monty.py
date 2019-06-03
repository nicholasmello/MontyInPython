import math
import time
from Util import *
from States import *

from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from rlbot.utils.game_state_util import GameState, BallState, CarState, Physics, Vector3 as vector3, Rotator

class Monty(BaseAgent):

    def initialize_agent(self):
        self.me = obj()
        self.ball = obj()
        self.players = [] #holds other players in match
        self.start = time.time()

        self.state = kickoff()
        changeBotState("kickoff")
        self.controller = kickoffController

    def checkState(self):
        if self.state.expired:
            resetGlobalVariables()
            if kickoff().available(self) == True:
                self.state = kickoff()
                changeBotState("Kickoff")
            elif falling().available(self) == True:
                self.state = falling()
                changeBotState("Falling")
            elif offensiveCorner().available(self) == True:
                self.state = offensiveCorner()
                changeBotState("Offensive Corner")
            elif centerAttack().available(self) == True:
                self.state = centerAttack()
                changeBotState("Center Attack")
            elif defensiveCorner().available(self) == True:
                self.state = defensiveCorner()
                changeBotState("Defensive Corner")
            elif retreat().available(self) == True:
                self.state = retreat()
                changeBotState("Retreat")
            elif towardball().available(self) == True:
                self.state = towardball()
                changeBotState("Toward Ball")
            else:
                self.state = wait()
                changeBotState("Wait")
    

    def get_output(self, game: GameTickPacket) -> SimpleControllerState:
        self.preprocess(game)
        self.checkState()
        return self.state.execute(self)

    def preprocess(self,game):
        self.players = []
        car = game.game_cars[self.index]
        self.me.location.data = [car.physics.location.x, car.physics.location.y, car.physics.location.z]
        self.me.velocity.data = [car.physics.velocity.x, car.physics.velocity.y, car.physics.velocity.z]
        self.me.rotation.data = [car.physics.rotation.pitch, car.physics.rotation.yaw, car.physics.rotation.roll]
        self.me.rvelocity.data = [car.physics.angular_velocity.x, car.physics.angular_velocity.y, car.physics.angular_velocity.z]
        self.me.istouching = game.game_cars[self.index].has_wheel_contact
        self.me.isRoundActive = game.game_info.is_round_active
        self.me.matrix = rotator_to_matrix(self.me)
        self.me.boost = car.boost
        self.me.team = (game.game_cars[self.index].team - .5)*2 #-1 is blue, 1 is orange

        ball = game.game_ball.physics
        self.ball.location.data = [ball.location.x, ball.location.y, ball.location.z]
        self.ball.velocity.data = [ball.velocity.x, ball.velocity.y, ball.velocity.z]
        self.ball.rotation.data = [ball.rotation.pitch, ball.rotation.yaw, ball.rotation.roll]
        self.ball.rvelocity.data = [ball.angular_velocity.x, ball.angular_velocity.y, ball.angular_velocity.z]

        self.ball.local_location = to_local(self.ball,self.me)

        self.ball.ball_prediction = self.get_ball_prediction_struct()

        #collects info for all other cars in match, updates objects in self.players accordingly
        for i in range(game.num_cars):
            if i != self.index:
                car = game.game_cars[i]
                temp = obj()
                temp.index = i
                temp.team = car.team
                temp.location.data = [car.physics.location.x, car.physics.location.y, car.physics.location.z]
                temp.velocity.data = [car.physics.velocity.x, car.physics.velocity.y, car.physics.velocity.z]
                temp.rotation.data = [car.physics.rotation.pitch, car.physics.rotation.yaw, car.physics.rotation.roll]
                temp.rvelocity.data = [car.physics.angular_velocity.x, car.physics.angular_velocity.y, car.physics.angular_velocity.z]
                temp.boost = car.boost
                flag = False
                for item in self.players:
                    if item.index == i:
                        item = temp
                        flag = True
                        break
                if not flag:
                    self.players.append(temp)
