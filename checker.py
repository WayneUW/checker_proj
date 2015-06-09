
from __future__ import absolute_import
import functools
import logging
import checkerboard as cb
from copy import deepcopy

logger = logging.getLogger(__name__)

class Checker(object):
    u""" Checkers for a checkergame """
    def __init__(self, color, checkerboard):
        self.color = color
        self.king = False
        self.checkerboard = checkerboard
        self.position = ()
        self._jumped_checkers = []
        self._jump_chain = []
        self._list_of_jump_chains = []

        logger.info(u'Initialized {} checker {}'.format(self.color, self.__repr__()))


    def __str__(self):
        if self.king:
            return u' ' + self.color[0] + u'k '
        else:
            return u' ' + self.color[0] + u'  '


    @staticmethod
    #@functools.lru_cache(maxsize=32)
    def get_black_move_squares(square):
        u""" Get neighboring squares that a black checker at square could
            move or jump to.  Neighboring squares are returned as a tuple 
            with 2 values: position 0 is the move square, position 1
            is the jump square. """

        logger.debug(u'get_black_move_squares({})'.format(square))

        row, column = square
        if row == 0:
            # No moves or jumps to calculate
            return (None, None)
            #return

        nw = [None, None]
        ne = [None, None]

        # Calculate black move squares
        if column > 0:
            nw[0] = (row - 1, column - 1)
        if column < 7:
            ne[0] = (row - 1, column + 1)

        if row == 1:
            # No jumps to calculate
            return (nw, ne)

        # Calculate black jump squares
        if column > 1:
            nw[1] = (row - 2, column - 2)
        if column < 6:
            ne[1] = (row - 2, column + 2)

        return (nw, ne)


    @staticmethod
    #@functools.lru_cache(maxsize=32)
    def get_white_move_squares(square):
        u""" Get neighboring squares that a white checker at square could
            move or jump to.  Neighboring squares are returned as a tuple 
            with 2 values: position 0 is the move square, position 1
            is the jump square. """
        
        logger.debug(u'get_white_move_squares({})'.format(square))

        row, column = square
        if row == 7:
            # No moves or jumps to calculate
            return (None, None)
            #return

        sw = [None, None]
        se = [None, None]


        # Calculate white move squares
        if column > 0:
            sw[0] = (row + 1, column - 1)
        if column < 7:
            se[0] = (row + 1, column + 1)

        if row == 6:
            # No jumps to calculate
            return (sw, se)

        # Calculate white jump squares
        if column > 1:
            sw[1] = (row + 2, column - 2)
        if column < 6:
            se[1] = (row + 2, column + 2)

        return (sw, se)
           

    def get_checker(self, square):
        u""" Return reference to the checker at square """

        return self.checkerboard.get_checker(square)


    def get_move_squares(self, square=None):
        u""" Return the neighboring squares to which a checker might move
            or jump to. """

        logger.debug(u'get_move_squares({})'.format(square))

        if square == None:
            square = self.position
            logger.debug(u'get_move_squares(): square='.format(square))

        if self.king:
            return (self.get_black_move_squares(square) + 
                    self.get_white_move_squares(square))
        else:
            if self.color == u'black':
                return self.get_black_move_squares(square)
            else:
                return self.get_white_move_squares(square)


    def list_moves(self):
        u""" List non-jump moves from the current square.
            Each move is a list encoded as the starting square followed
            by the ending square. """

        moves = []

        # Neighboring squares without a checker are possible moves
        #for move_square, jump_square in self.get_move_squares():
        for move_squares in self.get_move_squares():
            if move_squares:
                move_square, jump_square = move_squares
                if move_square and self.get_checker(move_square) == None:
                    moves.append((self.position, move_square))

        logger.debug(u'list_moves(): moves[]={}'.format(moves))
        return moves


    def _change_square(self, square):
        u""" Change checker's square """
        
        logger.debug(u'_change_square({})'.format(square))

        # Remove reference to this checker from old position
        self.checkerboard.squares[self.position[0]][self.position[1]] = None

        # Place checker in new position
        self.checkerboard.place_checker(square, self)

        # See if checker should be promoted to a king
        row, column = square
        if not self.king:
            if (self.color == u'black' and row == 0 or
                self.color == u'white' and row == 7):
                self.king = True


    def move(self, square):
        u""" Move checker to square """
        
        logger.debug(u'move({})'.format(square))

        # Verify we are moving to an empty neighboring square
        u"""
        if (square in [sq[0] for sq in self.get_move_squares()] and
            self.get_checker(square) == None):
            
            logger.info('move(): Moving from {} to {}'.format(self.position, square))

            self._change_square(square)

        else:
            # Illegal Move error
            logger.warning('move(): Illegal move from {} to {}'.format(self.position, square))
            print("Invalid move from", self.position, "to", square)
        """
        logger.info(u'move(): Moving from {} to {}'.format(self.position, square))
        self._change_square(square)


    def check_for_jump(self):
        u""" Return true if checker has a jump move available """

        logger.debug(u'check_for_jump()')

        for move_square, jump_square in self.get_move_squares():
            if jump_square:
                move_square_checker = self.get_checker(move_square)
                jump_square_checker = self.get_checker(jump_square)

                if (isinstance(move_square_checker, Checker) and
                    move_square_checker.color != self.color and
                    jump_square_checker == None):

                    return True

        return False


    def valid_jump(self, neighbors):
        u""" Check for valid jump """
        
        if (neighbors and neighbors[1] and
            # Verify jump landing square is empty
            (  self.get_checker(neighbors[1]) == None or
               # Allow for king possibly jumping in a circle back to start
               self.get_checker(neighbors[1]) == self
            ) and
            # Is there an opponent's checker to jump over?
            self.get_checker(neighbors[0]) and
            self.get_checker(neighbors[0]).color != self.color and
            # Prevent trying to jump the same checker twice
            self.get_checker(neighbors[0]) not in self._jumped_checkers):

            logger.debug(u'valid_jump({}): True'.format(neighbors))
            return True

        else:
            logger.debug(u'valid_jump({}): False'.format(neighbors))
            return False


    def _add_jump_square(self, square):
        u""" Add a jump square to a chain of jumps """

        logger.debug(u'_add_jump_square({})'.format(square))

        self._jump_chain.append(square)
        logger.debug(u'_add_jump_square(): self._jump_chain={}'.format(self._jump_chain))

        end_of_jump_chain = True

        # Check for more jumps from new position
        for neighbors in self.get_move_squares(square):
            if self.valid_jump(neighbors):
                end_of_jump_chain = False

                # Keep track of jumped checkers
                self._jumped_checkers.append(self.get_checker(neighbors[0]))

                # Add target squares to the jump chain
                self._add_jump_square(neighbors[1])

                logger.debug(u'_add_jump_square(): Jump checker={}'.format(neighbors[0]))
                logger.debug(u'_add_jump_square(): Jump to square={}'.format(neighbors[1]))

        # If end of a jump chain
        if end_of_jump_chain:
            logger.debug(u'_add_jump_square(): end of jump chain')

            self._list_of_jump_chains.append(deepcopy(self._jump_chain))
            logger.debug(u'_add_jump_square(): self._list_of_jump_chains={}'.format(self._list_of_jump_chains))

        self._jump_chain.pop()
        logger.debug(u'_add_jump_square(): self._jump_chain={}'.format(self._jump_chain))

        self._jumped_checkers.pop()
        logger.debug(u'_add_jump_square(): self._jumped_checkers={}'.format(self._jumped_checkers))

        return


    def list_jumps(self):
        u""" List all possible jumps from checker's position """

        logger.debug(u'list_jumps(): position={}'.format(self.position))

        # Each jump chain begins with checker's starting position
        self._jump_chain = [self.position]
        logger.debug(u'list_jumps(): _jump_chain={}'.format(self._jump_chain))

        self._list_of_jump_chains = []

        for neighbors in self.get_move_squares():
            if self.valid_jump(neighbors):
                # Keep track of jumped checkers
                self._jumped_checkers = [self.get_checker(neighbors[0])]
                logger.debug(u'list_jumps(): _jumped_checkers={}'.format(self._jumped_checkers))
                #self._jumped_checkers.append(self.get_checker(neighbors[0]))

                # Add target squares to the jump chain
                self._add_jump_square(neighbors[1])

                logger.debug(u'list_jumps(): Jumped square={}'.format(neighbors[0]))
                logger.debug(u'list_jumps(): Jump to square={}'.format(neighbors[1]))

        logger.debug(u'list_jumps(): _list_of_jump_chains={}'.format(self._list_of_jump_chains))
        return self._list_of_jump_chains


    def jump(self, square):
        u""" Checker jumps to square """

        logger.debug(u'jump({})'.format(square))

        # Verify valid jump
        #for jumped_square, jump_to_square in self.get_move_squares():
        for move_squares in self.get_move_squares():
            if move_squares:
                jumped_square, jump_to_square = move_squares
                if jump_to_square == square:
                    jumped_square_checker = self.get_checker(jumped_square)
                    jump_to_square_checker = self.get_checker(jump_to_square)

                    if (isinstance(jumped_square_checker, Checker) and
                        jumped_square_checker.color != self.color and
                        jump_to_square_checker == None):

                        # Valid jump, remove jumped checker
                        logger.info(u'jump(): Jumping from {} to {}'.format(self.position, square))
                        self.checkerboard.remove_checker(jumped_square)

                        self._change_square(jump_to_square)

                        return

        # Invalid jump request
        logger.warning(u'jump(): Invalid jump from {} to {}'.format(self.position, jumped_square))


    def jump_chain(self, chain):
        u""" Walk a jump chain (list of squares), jumping checkers between squares """

        logger.debug(u'jump_chain({})'.format(chain))

        # Jump chains always start with current position
        if len(chain) > 1 and chain[0] == self.position:
            for square in chain[1:]:
                self.jump(square)

        else:
            logger.warning(u'jump_chain({}): Invalid jump chain'.format(chain))


