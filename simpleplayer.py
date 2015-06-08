
from __future__ import absolute_import
import functools
import logging
import random
import checkerboard as cb
import checker as ch
from computerplayer import ComputerPlayer
from copy import deepcopy


logger = logging.getLogger(__name__)

class SimplePlayer(ComputerPlayer):
    u""" This player uses simple heuristics to make moves in the game of Checkers """

    def __init__(self):
        ComputerPlayer.__init__(self)
        random.seed()
        logger.info(u'Initialized player {}'.format(self.__repr__()))
        logger.setLevel(logging.INFO)
        #logger.setLevel(logging.DEBUG)


    def select_jumps(self, jumps_list):
        u""" Pick the best jump move in list of jumps """
        
        logger.debug(u'select_jumps({})'.format(jumps_list))

        # If only one jump available, there is no choice to make
        if len(jumps_list) == 1:
            return (u'jump', jumps_list[0])

        # Prefer jumping more checkers to fewer
        max_jumps = max([len(jumps) for jumps in jumps_list])

        for jumps in jumps_list:
            long_jumps = []
            if len(jumps) == max_jumps:
                long_jumps.append(deepcopy(jumps))

        # Avoid leaving checker in vulnerable position
        for jumps in long_jumps:
            ch = self.checkerboard.get_checker(jumps[0])

            if not self.checker_vulnerable(ch, jumps[-1]):
                logger.debug(u'select_jumps(): random long jump, not vulnerable')
                return (u'jump', jumps)

        # Try to find any jump that does not leave jumping checker vulnerable
        for jumps in jumps_list:
            ch = self.checkerboard.get_checker(jumps[0])
            if not self.checker_vulnerable(ch, jumps[-1]):
                logger.debug(u'select_jumps(): random jump, not vulnerable')
                return (u'jump', jumps)

        # With no better option, randomly choose between longest available jumps
        logger.debug(u'select_jumps(): random long jump, vulnerable')
        return (u'jump', random.choice(long_jumps))


    def get_neighboring_checkers(self, square):
        u""" Get checkers next to square.
            Squares are stored in a dictionary, keyed on 'ne' for northeast,
            'nw' for northwest, 'se' for southeast, and 'sw' for southwest.
            Normal, not crowned, black checkers move towards the north.
            White checkers move towards the south. """

        logger.debug(u'get_neighboring_checkers({})'.format(square))

        return {u'nw':self.checkerboard.get_checker((square[0]-1, square[1]-1)),
                u'ne':self.checkerboard.get_checker((square[0]-1, square[1]+1)),
                u'sw':self.checkerboard.get_checker((square[0]+1, square[1]-1)),
                u'se':self.checkerboard.get_checker((square[0]+1, square[1]+1))}


    def checker_vulnerable(self, checker, square=None):
        u""" Determine if checker is vulnerable to being jumped """

        logger.debug(u'checker_vulnerable({}, {})'.format(checker, square))
        logger.debug(u'checker_vulnerable(): checker.position={}'.format(checker.position))

        if square == None:
            square = checker.position

        # Checkers are not vulnerable if located on one edge of the board
        if (square[0] == 0 or square[0] == 7 or
            square[1] == 0 or square[1] == 7 ):
            return False

        # Get neighboring squares so we can check for opponent pieces
        neighbors = self.get_neighboring_checkers(square)

        if checker.color == u'black':
            if (neighbors[u'ne'] and neighbors[u'ne'].color == u'white' and
                (not neighbors[u'sw'] or neighbors[u'sw'] == checker)):
                return True
            if (neighbors[u'nw'] and neighbors[u'nw'].color == u'white' and
                (not neighbors[u'se'] or neighbors[u'se'] == checker)):
                return True
            if (neighbors[u'se'] and neighbors[u'se'].color == u'white' and
                neighbors[u'se'].king and 
                (not neighbors[u'nw'] or neighbors[u'nw'] == checker)):
                return True
            if (neighbors[u'sw'] and neighbors[u'sw'].color == u'white' and
                neighbors[u'sw'].king and 
                (not neighbors[u'ne'] or neighbors[u'ne'] == checker)):
                logger.debug(u'checker_vulnerable(): black checker vulnerable')

                return True
            
        else:   # checker.color == 'white'
            if (neighbors[u'se'] and neighbors[u'se'].color == u'black' and
                (not neighbors[u'nw'] or neighbors[u'nw'] == checker)):
                return True
            if (neighbors[u'sw'] and neighbors[u'sw'].color == u'black' and
                (not neighbors[u'ne'] or neighbors[u'ne'] == checker)):
                return True
            if (neighbors[u'ne'] and neighbors[u'ne'].color == u'black' and
                neighbors[u'ne'].king and 
                (not neighbors[u'sw'] or neighbors[u'sw'] == checker)):
                return True
            if (neighbors[u'nw'] and neighbors[u'nw'].color == u'black' and
                neighbors[u'nw'].king and 
                (not neighbors[u'se'] or neighbors[u'se'] == checker)):
                logger.debug(u'checker_vulnerable(): white checker vulnerable')
                return True

        logger.debug(u'checker_vulnerable(): checker not vulnerable')
        return False


    def get_open_king_squares(self, color):
        u""" Get open squares from opponent's home row """

        logger.debug(u'get_open_king_squares({})'.format(color))

        if color == u'black':
            row = 0
            starting_column = 0
        else:
            row = 7
            starting_column = 1

        open_squares = []
        for column in xrange(starting_column, starting_column + 7, 2):
            if self.checkerboard.get_checker((row, column)) == None:
                open_squares.append((row, column))

        logger.debug(u'get_open_king_squares(): open_squares={}'.format(open_squares))
        return open_squares


    def valid_attack(self, mycolor, square, directions):
        u""" Determine if moving a checker to square would attack opponent """

        logger.debug(u'valid_attack({}, {}, {})'.format(mycolor, square, directions))

        row, column = square

        for attack_direction in directions:
            # Cannot attack in specified direction if too close to edge of checkerboard
            if ((attack_direction in (u'nw', u'sw') and square[1] < 2) or
                (attack_direction in (u'ne', u'se') and square[1] > 5) or
                (attack_direction in (u'nw', u'ne') and square[0] < 2) or
                (attack_direction in (u'sw', u'se') and square[0] > 5)):
                logger.debug(u'valid_attack(): False')
                return False

            if attack_direction == u'nw': 
                ch1 = self.checkerboard.get_checker((row - 1, column - 1))
                ch2 = self.checkerboard.get_checker((row - 2, column - 2))

                if ch1 and ch1.color != mycolor and not ch2:
                    logger.debug(u'valid_attack(): nw True')
                    return True

            if attack_direction == u'ne': 
                ch1 = self.checkerboard.get_checker((row - 1, column + 1))
                ch2 = self.checkerboard.get_checker((row - 2, column + 2))
                if ch1 and ch1.color != mycolor and not ch2:
                    logger.debug(u'valid_attack(): ne True')
                    return True

            if attack_direction == u'sw': 
                ch1 = self.checkerboard.get_checker((row + 1, column - 1))
                ch2 = self.checkerboard.get_checker((row + 2, column - 2))
                if ch1 and ch1.color != mycolor and not ch2:
                    logger.debug(u'valid_attack(): sw True')
                    return True

            if attack_direction == u'se': 
                ch1 = self.checkerboard.get_checker((row + 1, column + 1))
                ch2 = self.checkerboard.get_checker((row + 2, column + 2))
                if ch1 and ch1.color != mycolor and not ch2:
                    logger.debug(u'valid_attack(): se True')
                    return True


    def count_opponent_checkers(self):
        u""" Determine how many checkers opponent has remaining """

        logger.debug(u'count_opponent_checkers()')

        if self.color == u'black':
            return len(self.checkerboard.white_checkers)
        else:
            return len(self.checkerboard.black_checkers)


    #def check_forward_move(self, move, columns=(0, 1, 2, 3, 4, 5, 6, 7)):
    #    """ Determine of checker can safely move forward to specified columns """
    #    pass


    def nearest_opponent(self, checker):
        u""" Find square containing nearest opponent checker """

        logger.debug(u'nearest_opponent({})'.format(checker))

        row, column = checker.position

        # Search perimeter of expanding squares around checker, until opponent is found
        for offset in xrange(8):
            # Search the next row north of checker
            offset_row = row - offset
            for offset_column in xrange(column - offset, column + offset + 1):
                if offset_row in xrange(8) and offset_column in xrange(8):
                    target_checker = self.checkerboard.get_checker((offset_row, offset_column))
                    if target_checker and target_checker.color != self.color:
                        logger.debug(u'nearest_opponent(): north at square {}'.format((offset_row, offset_column)))
                        return ((offset_row, offset_column))

            # Search the next row south of checker
            offset_row = row + offset
            for offset_column in xrange(column - offset, column + offset + 1):
                if offset_row in xrange(8) and offset_column in xrange(8):
                    target_checker = self.checkerboard.get_checker((offset_row, offset_column))
                    if target_checker and target_checker.color != self.color:
                        logger.debug(u'nearest_opponent(): south at square {}'.format((offset_row, offset_column)))
                        return ((offset_row, offset_column))

            # Search the next column west of checker
            offset_column = column - offset
            for offset_row in xrange(row - offset, row + offset + 1):
                if offset_row in xrange(8) and offset_column in xrange(8):
                    target_checker = self.checkerboard.get_checker((offset_row, offset_column))
                    if target_checker and target_checker.color != self.color:
                        logger.debug(u'nearest_opponent(): west at square {}'.format((offset_row, offset_column)))
                        return ((offset_row, offset_column))

            # Search the next column east of checker
            offset_column = column + offset
            for offset_row in xrange(row - offset, row + offset + 1):
                if offset_row in xrange(8) and offset_column in xrange(8):
                    target_checker = self.checkerboard.get_checker((offset_row, offset_column))
                    if target_checker and target_checker.color != self.color:
                        logger.debug(u'nearest_opponent(): east at square {}'.format((offset_row, offset_column)))
                        return ((offset_row, offset_column))


    def select_move(self, moves_list):
        u""" Select best move in list """

        logger.debug(u'select_move({})'.format(moves_list))

        # If only one move available, there is no choice to make
        if len(moves_list) == 1:
            logger.debug(u'select_move(): Only one move available {}'.format(moves_list[0]))
            return (u'move', moves_list[0])

        # Any checkers in danger of being jumped?
        for move in moves_list:
            # Get the checker that could be moved
            ch = self.checkerboard.get_checker(move[0])

            # If checker is vulnerable to being jumped, move it
            #   unless moving it still leaves it vulnerable to being jumped
            # Later, add ability to block jumps
            if self.checker_vulnerable(ch) and not self.checker_vulnerable(ch, move[1]):
                logger.debug(u'select_move(): Moving vulnerable checker {}'.format(move))
                return (u'move', move)

        # Any checkers in position to be crowned?
        for move in moves_list:
            # Get the checker that could be moved
            ch = self.checkerboard.get_checker(move[0])

            # If checker can become a king, move it
            if not ch.king and (move[1][0] in (0,7)):
                logger.debug(u'select_move(): Moving checker to be crowned {}'.format(move))
                return (u'move', move)

        # Attack if possible
        for move in moves_list:
            ch = self.checkerboard.get_checker(move[0])
            if not self.checker_vulnerable(ch, move[1]):
                # Will move attack opponent?
                if ch.king:
                    if self.valid_attack(ch.color, move[1], (u'nw', u'ne', u'sw', u'se')):
                        logger.debug(u'select_move(): Moving king to attack {}'.format(move))
                        return (u'move', move)

                # Delay moving home row checkers until later in the end game
                elif not (ch.position[0] in (0, 7) and 
                    self.count_opponent_checkers() + len(self.checkers) > 12):
                    if ch.color == u'black':
                        if self.valid_attack(ch.color, move[1], (u'nw', u'ne')):
                            logger.debug(u'select_move(): Moving black to attack {}'.format(move))
                            return (u'move', move)
                    else:   # ch.color == 'white'
                        if self.valid_attack(ch.color, move[1], (u'sw', u'se')):
                            logger.debug(u'select_move(): Moving white to attack {}'.format(move))
                            return (u'move', move)

        # Get kings away from opponent's home row, to clear space for potential new kings
        # for move in moves_list:
        #     ch = self.checkerboard.get_checker(move[0])
        #     if ch.king and ch.color == 'black':
        #         if ch.position[0] == 0:
        #             if not self.checker_vulnerable(ch, move[1]):
        #                 logger.debug('select_move(): Moving black king off opponent home row {}'.format(move))
        #                 return ('move', move)
        #         elif ch.position[0] == 1 and move[1][0] > 1:
        #             if not self.checker_vulnerable(ch, move[1]):
        #                 logger.debug('select_move(): Moving black king away from opponent home row {}'.format(move))
        #                 return ('move', move)

        #     elif ch.king and ch.color == 'white':
        #         if ch.position[0] == 7:
        #             if not self.checker_vulnerable(ch, move[1]):
        #                 logger.debug('select_move(): Moving white king off opponent home row {}'.format(move))
        #                 return ('move', move)
        #         elif ch.position[0] == 6 and move[1][0] < 6:
        #             if not self.checker_vulnerable(ch, move[1]):
        #                 logger.debug('select_move(): Moving white king away from opponent home row {}'.format(move))
        #                 return ('move', move)


        # Bias towards moving checkers closer to being crowned
        for move in moves_list:
            # Get the checker that could be moved
            # Target open squares in opponent's home row to crown checker
            ch = self.checkerboard.get_checker(move[0])
            if not ch.king:
                if ch.color == u'black' and ch.position[0] == 2:
                    open_king_squares = self.get_open_king_squares(u'white')
                    for open_king_square in open_king_squares:
                        if (open_king_square[1] == move[1][1] + 1 or
                            open_king_square[1] == move[1][1] - 1 or
                            open_king_square[1] == ch.position[1]):
                            if not self.checker_vulnerable(ch, move[1]):
                                logger.debug(u'select_move(): Moving black from row 2 towards open' +
                                             u' king square {}'.format(move))
                                return (u'move', move)
                elif ch.color == u'white' and ch.position[0] == 5:
                    open_king_squares = self.get_open_king_squares(u'black')
                    for open_king_square in open_king_squares:
                        if (open_king_square[1] == move[1][1] + 1 or
                            open_king_square[1] == move[1][1] - 1 or
                            open_king_square[1] == ch.position[1]):
                            if not self.checker_vulnerable(ch, move[1]):
                                logger.debug(u'select_move(): Moving white from row 5 towards open' +
                                             u' king square {}'.format(move))
                                return (u'move', move)

        # If nearing the end game, get home row checkers in play
        if len(self.checkers) + self.count_opponent_checkers() < 13:
            for move in moves_list:
                ch = self.checkerboard.get_checker(move[0])
                if not ch.king:
                    # possible_move = check_forward_move(move)
                    if (ch.color == u'black' and ch.position[0] == 7 and
                        not self.checker_vulnerable(ch, move[1])):
                            logger.debug(u'select_move(): Moving black home row checker {}'.format(move))
                            return (u'move', move)

                    elif (ch.color == u'white' and ch.position[0] == 0 and
                        not self.checker_vulnerable(ch, move[1])):
                            logger.debug(u'select_move(): Moving white home row checker {}'.format(move))
                            return (u'move', move)


        # Bias towards moving checkers towards rows opponent's home row,
        #   and towards center columns
        for move in moves_list:
            ch = self.checkerboard.get_checker(move[0])
            if not ch.king:
                # possible_move = check_forward_move(move)
                if (ch.color == u'black' and ch.position[0] == 3 and
                    move[1][1] in (1, 2, 3, 4, 5, 6)):
                    if not self.checker_vulnerable(ch, move[1]):
                        logger.debug(u'select_move(): Advancing black from row 3 {}'.format(move))
                        return (u'move', move)

                elif (ch.color == u'white' and ch.position[0] == 4 and
                    move[1][1] in (1, 2, 3, 4, 5, 6)):
                    if not self.checker_vulnerable(ch, move[1]):
                        logger.debug(u'select_move(): Advancing white from row 4 {}'.format(move))
                        return (u'move', move)

        for move in moves_list:
            ch = self.checkerboard.get_checker(move[0])
            if not ch.king:
                if (ch.color == u'black' and ch.position[0] == 4 and
                    move[1][1] in (1, 2, 3, 4, 5, 6)):
                    if not self.checker_vulnerable(ch, move[1]):
                        logger.debug(u'select_move(): Advancing black from row 4 {}'.format(move))
                        return (u'move', move)

                elif (ch.color == u'white' and ch.position[0] == 3 and
                    move[1][1] in (1, 2, 3, 4, 5, 6)):
                    if not self.checker_vulnerable(ch, move[1]):
                        logger.debug(u'select_move(): Advancing white from row 3 {}'.format(move))
                        return (u'move', move)

        for move in moves_list:
            ch = self.checkerboard.get_checker(move[0])
            if not ch.king:
                if (ch.color == u'black' and ch.position[0] == 5 and
                    move[1][1] in (1, 2, 3, 4, 5, 6)):
                    if not self.checker_vulnerable(ch, move[1]):
                        logger.debug(u'select_move(): Advancing black from row 5 {}'.format(move))
                        return (u'move', move)

                elif (ch.color == u'white' and ch.position[0] == 2 and
                    move[1][1] in (1, 2, 3, 4, 5, 6)):
                    if not self.checker_vulnerable(ch, move[1]):
                        logger.debug(u'select_move(): Advancing white from row 2 {}'.format(move))
                        return (u'move', move)

        for move in moves_list:
            ch = self.checkerboard.get_checker(move[0])
            if not ch.king:
                if (ch.color == u'black' and ch.position[0] == 6 and
                    move[1][1] in (1, 2, 3, 4, 5, 6)):
                    if not self.checker_vulnerable(ch, move[1]):
                        logger.debug(u'select_move(): Advancing black from row 6 {}'.format(move))
                        return (u'move', move)

                elif (ch.color == u'white' and ch.position[0] == 1 and
                    move[1][1] in (1, 2, 3, 4, 5, 6)):
                    if not self.checker_vulnerable(ch, move[1]):
                        logger.debug(u'select_move(): Advancing white from row 1 {}'.format(move))
                        return (u'move', move)

        # Move kings towards opponent pieces
        for move in moves_list:
            ch = self.checkerboard.get_checker(move[0])
            if ch.king:
                target_square = self.nearest_opponent(ch)
                # if target is northwest, and move is northwest
                if ((target_square[0] < ch.position[0] and 
                     move[1][0] < ch.position[0] and
                     target_square[1] < ch.position[1] and
                     move[1][1] < ch.position[1]) 
                    or # or if target is nw and move is nw
                    (target_square[0] < ch.position[0] and 
                     move[1][0] < ch.position[0] and
                     target_square[1] > ch.position[1] and
                     move[1][1] > ch.position[1])                    
                    or # or if target is sw and move is sw
                    (target_square[0] > ch.position[0] and 
                     move[1][0] > ch.position[0] and
                     target_square[1] < ch.position[1] and
                     move[1][1] < ch.position[1])                    
                    or # or if target is se and move is se
                    (target_square[0] > ch.position[0] and 
                     move[1][0] > ch.position[0] and
                     target_square[1] > ch.position[1] and
                     move[1][1] > ch.position[1])):

                    if self.checkerboard.get_checker(target_square).king:
                        # Avoid risk of moving to 2 squares from opponent on row or column
                        #   as this opens up risk of fork attack by a king
                        # Note: Add logic here.  This test is too restrictive.  This is sometimes a good move.
                        if (not (move[1][0] == target_square[0] and 
                                 move[1][1] in (target_square[1] + 2, target_square[1] - 2)) or
                                (move[1][1] == target_square[1] and
                                 move[1][0] in (target_square[0] + 2, target_square[0] - 2))):
                         
                            if not self.checker_vulnerable(ch, move[1]):
                                logger.debug(u'select_move(): Moving king towards opponent king {}'.format(move))
                                return (u'move', move)
                    else:
                        if not self.checker_vulnerable(ch, move[1]):
                            logger.debug(u'select_move(): Moving king towards opponent checker {}'.format(move))
                            return (u'move', move)

        # Move kings towards center of the board
        for move in moves_list:
            ch = self.checkerboard.get_checker(move[0])
            if ch.king:
                if ((ch.position[0] < 2 and move[1][0] > ch.position[0]) or
                    (ch.position[0] > 5 and move[1][0] < ch.position[0]) or
                    (ch.position[1] < 2 and move[1][1] > ch.position[1]) or
                    (ch.position[1] > 5 and move[1][1] < ch.position[1])):

                    if not self.checker_vulnerable(ch, move[1]):
                        logger.debug(u'select_move(): Moving king towards center of board {}'.format(move))
                        return (u'move', move)

        # Delay moving ordinary checkers from home row
        for move in moves_list:
            ch = self.checkerboard.get_checker(move[0])
            if not (ch.position[0] in (0,7) and not ch.king):
                if not self.checker_vulnerable(ch, move[1]):
                    logger.debug(u'select_move(): Moving checker not on home row {}'.format(move))
                    return (u'move', move)

        # Take any valid move that does not lead to being jumped
        for move in moves_list:
            ch = self.checkerboard.get_checker(move[0])
            if not self.checker_vulnerable(ch, move[1]):
                logger.debug(u'select_move(): Taking any move not vulnerable {}'.format(move))
                return (u'move', move)

        # Move any checker that is not a king
        for move in moves_list:
            ch = self.checkerboard.get_checker(move[0])
            if not ch.king:
                logger.debug(u'select_move(): Moving any checker not a king {}'.format(move))
                return (u'move', move)

        # Take any move
        logger.debug(u'select_move(): Random move of any checker {}'.format(move))
        return (u'move', random.choice(moves_list))


    def evaluate_board(self):
        u""" Evaluate the checkerboard, to determine next move """

        logger.debug(u'evaluate_board()')

        jumps_list = self.list_jumps()
        if jumps_list:
            return self.select_jumps(jumps_list)

        moves_list = self.list_moves()
        if moves_list:
            return self.select_move(moves_list)

        return (u'surrender',)




