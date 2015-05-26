
from __future__ import absolute_import
import logging
import random
import checkerboard as cb
import checker as ch
from computerplayer import ComputerPlayer
from copy import deepcopy


logger = logging.getLogger(__name__)

class RandomPlayer(ComputerPlayer):
    u""" This player makes random moves in the game of Checkers """

    def __init__(self):
        ComputerPlayer.__init__(self)
        random.seed()



    def evaluate_board(self):
        u""" Evaluate the checkerboard, to determine next move """

        jumps_list = self.list_jumps()
        if jumps_list:
            return (u'jump', random.choice(jumps_list))

        moves_list = self.list_moves()
        if moves_list:
            return (u'move', random.choice(moves_list))

        return (u'surrender',)


    def play(self):
        u""" Determine action in game of checkers """

        evaluation = self.evaluate_board()
        if evaluation[0] == u'jump':
            self.jump_checkers(evaluation[1])
            print u"Jump move completed"
            return u"jump"

        elif evaluation[0] == u'move':
            self.move_checker(evaluation[1])
            print u"Move completed"
            return u"move"

        else:
            print u"I surrender"
            return u"surrender"

        


