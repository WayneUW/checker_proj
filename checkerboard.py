
from __future__ import absolute_import
import logging
import checker as ch
import sys

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Checkerboard(object):
    u""" A checkerboard for playing checkers """

    def __init__(self):
        u""" Create a 2 dimensional array representing checkerboard 
            squares """
        self.squares = [[None for j in xrange(8)] for i in xrange(8)]

        self.black_checkers = []
        self.white_checkers = []

        logger.info(u'Initialized checkerboard {}'.format(self))


    def dark_square(self, square):
        u""" True if this is a dark square, a valid location 
            for a checker """

        logger.debug(u'dark_square({})'.format(square))

        row, column = square
        return (row + column) % 2 != 0


    def print_board(self):
        u""" Print the contents of the checkerboard """

        print

        for row in xrange(8):
            for column in xrange(8):
                if self.squares[row][column]:
                    print self.squares[row][column],; sys.stdout.write(u'')
                else:
                    if self.dark_square((row, column)):
                        print u' __ ',; sys.stdout.write(u'')
                    else:
                        print u' .  ',; sys.stdout.write(u'')
            print
        print


    def place_checker(self, square, checker):
        u""" Place checker on square """

        logger.debug(u'place_checker({}, {})'.format(square, checker))

        row, column = square
        self.squares[row][column] = checker
        checker.position = (row, column)


    def get_checker(self, square):
        u""" Return reference to the checker at square """

        logger.debug(u'get_checker({})'.format(square))

        row, column = square
        return self.squares[row][column]


    def remove_checker(self, square):
        u""" Remove checker from the board """

        logger.debug(u'remove_checker({})'.format(square))

        checker = self.get_checker(square)
        logger.debug(u'remove_checker(): checker={}'.format(checker))

        row, column = square
        self.squares[row][column] = None

        if checker.color == u'black':
            self.black_checkers.remove(checker)
        else:
            self.white_checkers.remove(checker)


    def setup_new_board(self):
        u""" Setup a new board with 12 checkers on each side 
            in starting positions """

        logger.info(u'setup_new_board()')

        self.squares = [[None for j in xrange(8)] for i in xrange(8)]
        
        self.black_checkers = [ch.Checker(u'black', self) for i in xrange(12)]
        self.white_checkers = [ch.Checker(u'white', self) for i in xrange(12)]

        u""" Place checkers in starting squares """
        i = 0
        for row in xrange(3):
            for column in xrange(8):
                if self.dark_square((row, column)):
                    self.place_checker((row, column), self.white_checkers[i])
                    i += 1

        i = 0
        for row in xrange(5, 8):
            for column in xrange(8):
                if self.dark_square((row, column)):
                    self.place_checker((row, column), self.black_checkers[i])
                    i += 1


