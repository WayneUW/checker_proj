
from __future__ import absolute_import
import collections
import logging
from time import sleep
from checkerboard import Checkerboard
from checker import Checker
from player import Player
from computerplayer import ComputerPlayer
from simpleplayer import SimplePlayer


logger = logging.getLogger(__name__)

class Game(object):
    u""" Controlling class for a game of checkers """

    def __init__(self, black_player, white_player):
        u""" Initialize a new game """
        self.black_player = black_player
        self.white_player = white_player

        self.chb = Checkerboard()
        self.chb.setup_new_board()

        self.black_player.color = u'black'
        self.black_player.checkerboard = self.chb
        self.black_player.checkers = self.chb.black_checkers

        self.white_player.color = u'white'
        self.white_player.checkerboard = self.chb
        self.white_player.checkers = self.chb.white_checkers

        self.pos_counter = collections.Counter()

        
    def start_game():
        u""" Begin play """
        pass


if __name__ == u'__main__':
    #black_player = ComputerPlayer()
    logger.setLevel(logging.INFO)
    black_player = SimplePlayer()
    white_player = SimplePlayer()

    game = Game(black_player, white_player)

    game.chb.print_board()
    print u'Starting game\n'
    
    turn = u'black'

    game_on = True
    while game_on:
        # Get hash value of all checkers' positions
        ch_black_pos = [ch.position for ch in black_player.checkers]
        ch_white_pos = [ch.position for ch in white_player.checkers]
        checkers_hash = hash(tuple(ch_black_pos + ch_white_pos))
        # Game ends in draw if all checkers' positions repeat 3 times
        #print('type(game.pos_counter) = {}'.format(type(game.pos_counter)))
        print u'len(game.pos_counter) = {}'.format(len(game.pos_counter))
        print u'checkers_hash = {}'.format(checkers_hash)
        game.pos_counter.update([checkers_hash])
        print u'game.pos_counter[checkers_hash] = {}'.format(game.pos_counter[checkers_hash])
        if game.pos_counter[checkers_hash] >= 4:
            print u'The game is a draw due to repeating positions'
            game_on = False
            break

        sleep(1)
        if turn == u'black':
            if black_player.play() == u'surrender':
                msg = u'Black surrenders'
                game_on = False
            else:
                msg = u'Black move complete'
                turn = u'white'
        else:
            if white_player.play() == u'surrender':
                msg = u'White surrenders'
                game_on = False
            else:
                msg = u'White move complete'
                turn = u'black'

        game.chb.print_board()
        #print(msg)
        #print()

    print u"Game over"
