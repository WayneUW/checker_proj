READ ME NOTES
6/9/15

“A Simple Game of Checkers”
Final Project
Wayne Fukuhara & Brent Nunn
UW Spring 2015


Applications Used for Development:
-Python 2.7.8
-Pygame 1.9.2pre-py2.7-macosx10.7
-Xcode v2333
-X11 v1.0
-Homebrew v0.95
    -Used to install SDL dependencies. Run this command, “brew install sdl sdl_image sdl_mixer sdl_ttf portmidi”
-Adobe Illustrator 18.1.1



System and Hardware Used During Development:
-MacBook Pro 2.6 Ghz, Intel Core i7 with Mavericks OS 10.9.5
-HP Notebook with Fedora 22



Modules Developed for the Game:
-init.py (empty script for the package)
-checker1.py (Main module)
-game.py (Initialize Game() class. Controlling class for game.)
-checker.py (Initialize Checker() class.)
-checkerboard.py (Initialize Checkerboard() class.)
-player.py (contains Player() superclass. Determines what move to make based on list of available moves.)
-computerplayer.py (Contains ComputerPlayer() a sub-class of Player(). Automates valid moves.)
-simpleplayer.py (Contains SimplePlayer() a sub-class of ComputerPlayer(). Makes smarter moves than RandomPlayer().)
-images directory (images for the checkerboard pieces, checker pieces and king pieces)
	
-humanplayer.py (Contains HumanPlayer(), a sub-class of Player(). Not currently in use.)
-randomplayer.py (Contains RandomPlayer(), a sub-class of ComputerPlayer(). Not currently in use.)



GitHub Account: https://github.com/WayneUW/checker_proj.git
-Pull from the GitHub account above. Keep all the modules and the images folder in the same directory.
-Type” “python checker1.py” from the command line to run the game.
-The checker1.py module will import the other modules needed to run the program.
-The image files for the game are called from the images folder.







