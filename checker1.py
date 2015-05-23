"""UW Spring 2015 - Class Project
Final Project - A simple checkers game
Authors: Wayne Fukuhara & Brent Nunn
Code versions used to support this game:
Python 2.7.8
Pygame 1.9.2pre-py2.7-macosx10.7
"""

import pygame, sys, os
"""pygame.locals has several constants which are easily recognized so we break
the recommended practice of not using the import * syntax
"""
from pygame.locals import *


class CheckerPieces(pygame.sprite.Sprite):  # Subclass of the main Sprite class.
    """This class defines the player piece type, its associated image, center coordinate and update.
    The self.image variable is a Surface object which is the current image displayed.
    The self.rect variable is the location when that image is drawn to the screen.
    """
    
    def __init__(self, player, (centerx,centery)): # Wayne Note: self.center is for controlling position on the screen
        """Constructor. Creates instance of the Sprite class to initialize the sprites, assigns player images, defines position"""
        pygame.sprite.Sprite.__init__(self)
        screen = pygame.display.get_surface() # Reference to the current display surface, the screen.
        self.area = screen.get_rect()  # Assigns variable for the screen.
        self.player = player  # self.player object is assigned to the argument.

        """Load the image onto the Surface object"""
        if player == "red":
            self.image, self.rect = self.load_png('red-piece.png')  # Specfic image object and rect Surface object are assigned.
        elif player == "black":
            self.image, self.rect = self.load_png('black-piece.png')  # Assignment for player black
        else:
            print "I don't recognize this player: ", player
            raise SystemExit, message

        self.rect.centerx = centerx # Center x-value of rectangle object from line 36
        self.rect.centery = centery # Center y-value of rectangle object from line 37
        self.type = "notking"  # Non-king type


    def load_png(self, name):
        """Defines image path, loads image, converts transparency and returns image object and surface"""
        imagepath = os.path.join('images', name) # Path and name of image. You can also put the images in the same folder as the .py module
        try:
            image = pygame.image.load(imagepath)  # Returns image Surface object. Assignment locates and loads from the image folder.           
        except pygame.error, message:
                print "I can't find this checker piece image!: ", imagepath
                raise SystemExit, message
        image = image.convert_alpha() # Convert the image to make blitting faster
        return image, image.get_rect() # Returns blitted Surface image object and a rectangle Surface object with the width and height.

    # """The king type would be part of this class. However it's not used in the module now."""
    # def king(self):
    #     self.type = "king"
    #     if self.player == "red":
    #         self.image, self.rect = self.load_png('red-piece-king.png')
    #     elif self.player == "black":
    #         self.image, self.rect = self.load_png('black-piece-king.png')


    def update(self, position):
        """Update the center position"""
        self.rect.centerx = position[0]
        self.rect.centery = position[1]



class CheckerBoard(pygame.sprite.Sprite):  # Subclass of the main Sprite class.
    """This class defines the board color types, its associated image and loads them"""

    def __init__(self, initial_position, color, row, col):
        pygame.sprite.Sprite.__init__(self)
        screen = pygame.display.get_surface()

        self.area = screen.get_rect() # Assigns a rectangle for the screen.
        self.color = color
        self.row = row
        self.col = col

        if color == "black":  # Dark square image
            self.image, self.rect = self.load_png('black-space.png')  # Specfic image object and rect surface object are assigned.
        elif color == "red":  # light square image
            self.image, self.rect = self.load_png('red-space.png')
        else:
            print 'This is not a space color: ', color
            raise SystemExit, message
        
        self.rect.topleft = initial_position  # This tuple will set the position


    def load_png(self, name):
        """Defines image path, loads image, converts transparency and returns image object"""
        boardimage_path = os.path.join('images', name)  # image path.
        try:
            image = pygame.image.load(boardimage_path)
        except pygame.error, message:
                print "I can't find this checkerboard image!: ", boardimage_path
                raise SystemExit, message
        image = image.convert()  # convert() is for faster blitting.
        return image, image.get_rect() # These objects are not visisble until drawn to the main display.



class CheckersMain(object):
    """This class handles the main initialization and creation of the game.
    A Pygame window, or screen, is described by pixel width and pixel height.
    It is a Pygame Surface object. Surfaces are images on the screen.
    """
    def __init__(self):
        """Initialize Pygame"""
        pygame.init() # This initializes pygame and makes the submodules available.

        """Window Caption"""
        pygame.display.set_caption('Simple Game of Checkers')


    def mainloop(self):
        """Create the screen using the disply module and the width-height arguments"""
        screen = pygame.display.set_mode((600, 600), RESIZABLE) # The main display, or surface, of the terminal window size.
        tile_width = 75 # The size if the checkboard square.

        """Fill the background."""
        background = pygame.Surface(screen.get_size()) # Size of screen surface
        background.fill((255,255,255)) # Fill background surface. This RGB is white.
        background = background.convert() # Convert surface to make blitting faster

        """All checkerboard squares and 24 pieces are initially added to this container when the board is drawn.
        Track and update all black, red checkboard spaces and checker pieces that have changed.
        """
        black_spaces = pygame.sprite.RenderUpdates()
        red_spaces = pygame.sprite.RenderUpdates()
        pieces = pygame.sprite.RenderUpdates() # Both red and black pieces.

        """Set up the checkerboard."""
        for row in range(8): # 0 thru 7
            for col in range(8):
                top = tile_width*row # Pixel position. Row/top is the y coordinate. Start is 0,0
                left = tile_width*col # Pixel position. Column/left is the x coordinate. Start is 0,0
                if not(row % 2) and (col % 2):  # Initial combo is (0,1). The nested loop will layout by row.
                    black_spaces.add(CheckerBoard((left,top),"black", row, col)) # Track all black spaces by adding instances to the RenderUpdates() class.
                elif not(row % 2) and not(col % 2): # Initial combo is (1, 1)
                    red_spaces.add(CheckerBoard((left,top),"red", row, col))
                elif (row % 2) and not(col % 2): # Initial combo is (1, 0)
                    black_spaces.add(CheckerBoard((left,top),"black", row, col))
                elif (row % 2) and (col % 2): # Initial combo is (0, 0)
                    red_spaces.add(CheckerBoard((left,top),"red", row, col))

        """Set up the checker pieces."""
        for row in range(8): # 0 thru 7
            for col in range(8): # This inner loop will go through it's iterations first. (0,0),(0,1,(0,2) etc.
                if row < 3:  # If y is 0, 1 or 2
                    player = "black"
                elif row > 4: # If y is 5, 6, or 7
                    player = "red"
                if row < 3 or row > 4:
                    top = tile_width*row
                    left = tile_width*col
                    if not(row % 2) and (col % 2): # (0, 1) 
                        pieces.add(CheckerPieces(player,(left+(tile_width/2), top+(tile_width/2)))) # Track all checker pieces by adding instances to the RenderUpdates() class. This determines onto which squares the pieces are drawn and tracked and the center x and y.
                    elif (row % 2) and not(col % 2): # (1, 0)
                        pieces.add(CheckerPieces(player,(left+(tile_width/2), top+(tile_width/2)))) # At this point 24 checker pieces are in RenderUpdates()

        """Blit the checkerboard and pieces to Surface object, i.e. the screen, so they appear."""
        screen.blit(background, (0,0))
        # pygame.display.flip() # update drawing

        """Manage the sprite you are controlling by putting into GroupSingle()
        This allows the ability to manage a single sprite.
        """
        piece_selected = pygame.sprite.GroupSingle() # GroupSingle() holds a single sprite at a time. It can be None.
        space_selected = pygame.sprite.GroupSingle() # The black space where the piece has moved to.
        currentpiece_position = (0,0) # Initial piece position.



        """Begins the event handler loop which is queue for all events"""
        while True:
            for event in pygame.event.get(): # return events in the queue. Executes event handling code since the last time the function was called.
                if event.type == QUIT: # Quit if the close button is clicked. pygame.QUIT worked. QUIT is a contstant in .locals
                    pygame.quit() # This is a opposite of the init() function. This is here to accomodate a bug which hands IDLE
                    sys.exit()


                """Board with all the pieces load correctly."""



                """The main logic for the game goes here. The idea is to:
                Select a checker piece.
                Make a determination of where to move it (the rules).
                Move the piece.
                Redraw the screen. Easy right?
                
                Something like this:
                # boy = CheckerPieces("red", (337.5, 412.5))
                # boyrect = boy.get_rect()
                # boyrect.move = (337.5, 337)
                # boyrect.draw(screen)


                What I've been trying to do is grab a specific piece on the board.
                I've tried to:
                Select a specific sprite out of the container of sprites from RenderUpdate().
                I am able to index a spite out of the container, but it doesn't seem know it's an object of the larger class.
                It only knows it as an element of a list.

                For example, If I change the container type to LayeredUpdates() which has the get_sprites-at function I can get the list.

                # boy = pieces.get_sprites_at((75, 0))    OR   boy = pieces.get_sprite(1)
                # boyrect = boy.get_rect()

                If I print "boyrect" it shows me a list of one sprite. I need the object in order to manipulate it.



                Meanwhile...
                I have had some succes by calling the CheckerPieces class and passing the center coordinates.
                I am able manipulate it using a rectangle attributes.

                For example:
                # boy = CheckerPieces("red", (337.5, 412.5)) # Return a specific red checkerpiece.
                # boycenter = boy.rect.centerx # Return the center x coordinate of the rectangle.
                # print boycenter

                This returns centerx as 337 and continues to loop until I stop it. The center x coorindate is actually 337.5, so I'm
                not sure why it returns 337.
                However the fact that I can access the attribute centerx is good because it means it understands the statement.

                At this point 5/23/15 almost noon, I decided to baseline the code and send to you in case you have installed
                Pygame since you've had more sucess then me this week.
                """



            """Remove all events from the queue. Clear screen"""
            pieces.clear(screen, background)
            black_spaces.clear(screen, background)
            red_spaces.clear(screen, background)

            """Draw images using RenderUpdates() draw method"""
            black_spaces.draw(screen) # Draws changed sprites to the screen.
            red_spaces.draw(screen)
            pieces.draw(screen)

            """Refresh the screen"""
            # pygame.display.flip()
            pygame.display.update()


    """Finish game"""
    pygame.quit()


if __name__ == '__main__':
    main_window = CheckersMain()
    main_window.mainloop()