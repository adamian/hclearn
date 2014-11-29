import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from hcq import *
from gui import *
from locationLuke import * # using luke version....
from paths import * #CHANGED AS IPYTHON DOESN'T LIKE FILES/DIRS CALLED PATH
from makeMazeResizeable import * # Luke Altered to add new functions for displaying mze
#from makeMazeResizeable import displayMaze
from os import sys
import learnWeights
import sys
import cPickle as pickle
import os.path
from explore_maze import ExploreMaze


#if len(sys.argv) == 3:
#    b_useNewDG = (sys.argv[1] == "True")
#    learningRate = float(sys.argv[2])
#else:
#    b_useNewDG = True
#    learningRate = 0.01

b_useNewDG = True
learningRate = 0.01
    
print("Sys:%d" % len(sys.argv))
print("DG:%s" % b_useNewDG)
print("LR:%f" % learningRate)

np.set_printoptions(threshold=sys.maxint)         #=format short in matlab

# Set the root folder. You have two options:
# a) Put a file with name rootFolder.txt inside your visible path. 
#    It has to contain the full path of your root folder.
#    Do not sync with git this file (as it's different for every user)
# b) Do nothing, the code will find the current directory and use it as the default root folder.
rootFolderName = 'rootFolder.txt'
if os.path.isfile(rootFolderName):
    with open(rootFolderName,'r') as f:
        rootFolder = f.read().rstrip('\n')
    assert(f.closed)
else:
    rootFolder = os.path.dirname(os.path.abspath(__file__)) + '/'

# Run generate_map_from_streetview.py if you want to get the streetview pics

#----- Configuration -------------
## N_mazeSize=3 -> THIS NOW AUTOMATICALLY GENERATED!!!!!!!!!!!!!!!!!!!!!!!!!!

T=40   #trained on 30000   #better to have one long path than mult epochs on overfit little path
b_learnWeights=True
b_plot=True
b_inference=True
tr_epochs=10
# If true then it'll attempt to load the maze (corresponding to the same set of configurations) 
# from a file. If the file doesn't exist, the algorithm will save the maze for future use.
# Notice that makeMaze must have some radomness, because multiple runs of go.py return different results.

## luke -> Plot mazes after load and enter interactive mode...
plot_maze=False
plot_paths=False

pickle_maze = True # True # True
imFolder ="division_street_1" #"division_street_1" # "DCSCourtyard" #"division_street_1" #"DivisionCarver" #DCSCourtyard"
fullImageFolder = rootFolder + imFolder + "/"
#-------------------------------------------

# Luke added to graphically display maze....
if plot_maze:
    displayMaze(prefixFolder=fullImageFolder)
    

pickled_maze_name = "maze_SEED" + str(SEED) + "_DG" + str(int(b_useNewDG)) +  "_imdir" + imFolder + ".pickle"
if pickle_maze and os.path.isfile(pickled_maze_name):
    saved_maze = pickle.load( open( pickled_maze_name, "rb" ) )
    dictSenses = saved_maze[0]
    dictAvailableActions = saved_maze[1]
    dictNext = saved_maze[2]
    N_mazeSize = saved_maze[3] 
    dictPlaceCells = saved_maze[4]
    
    print "# Found and loaded pickled maze!"
else:
#    [dictSenses, dictAvailableActions, dictNext, N_mazeSize] = makeMaze(b_useNewDG, prefixFolder=fullImageFolder)  #make maze, including ideal percepts at each place
    [dictSenses, dictAvailableActions, dictNext, N_mazeSize, dictPlaceCells] = makeMaze(b_useNewDG, prefixFolder=fullImageFolder)  #make maze, including ideal percepts at each place

    if pickle_maze:
        saved_maze = [dictSenses, dictAvailableActions, dictNext, N_mazeSize, dictPlaceCells]
        pickle.dump( saved_maze, open( pickled_maze_name, "wb" ) )

# DictGrids is from location.py. Sets up a dictionary of grid cell locations from XY locations (I think!)

##### Next problem....
dictGrids = DictGrids()

# Luke Modified -> use start from first location in DictSenses
#start_location=[3,3,0] # Original setting in paths.py
start_location=np.asarray(dictSenses.keys()[0])

e = ExploreMaze(dictNext, T, start_location,debug_log='deleteme.log')
e.walk()

###### N_mazesize generated!!!
path_config = Paths(dictNext,N_mazeSize, T, start_location)          #a random walk through the maze -- a list of world states (not percepts)
displayPaths(fullImageFolder, path_config.posLog)


path_config.posLog = e.posLog.copy()
displayPaths(fullImageFolder, path_config.posLog)




