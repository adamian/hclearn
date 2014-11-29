#import matplotlib
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt
import numpy as np
# Test load each item to make sure it exists.....
from hcq import *
from gui import *
from locationLuke import * # using luke version....
from paths import * #CHANGED AS IPYTHON DOESN'T LIKE FILES/DIRS CALLED PATH
from makeMazeResizeable import * # Luke Altered to add new functions for displaying mze
import plotPlaceCells
#from makeMazeResizeable import displayMaze
#from os import sys
import learnWeights
import sys # repeat of above sys import
import cPickle as pickle
import os.path
from collections import OrderedDict
from explore_maze import ExploreMaze
#if len(sys.argv) == 3:
#    b_useNewDG = (sys.argv[1] == "True")
#    learningRate = float(sys.argv[2])
#else:
#    b_useNewDG = True
#    learningRate = 0.01

##################################################
################## Options #######################
##################################################
# LB: I have reorganised this to bring all to top of code to make it easier to understand and adjust....
#------------- Data input -> Maze -------------
imFolder ="division_street_1"  # Original: "DCSCourtyard" #"division_street_1" #"DivisionCarver"

#------------- Loading & Saving -------------
pickle_maze = True  # Original: True
# Andreas: If true then it'll attempt to load the maze (corresponding to the same set of configurations) 
# from a file. If the file doesn't exist, the algorithm will save the maze for future use.
# Andreas: Notice that makeMaze must have some radomness, because multiple runs of go.py return different results. 
## Load in previous ground truth data ??????????
b_usePrevGroundTruthCA3 = False  # Original: False
## ?????????????
b_useGroundTruthGrids = False  # Original: False


#------------- Plotting Options -------------
## Plot final outpts
b_plot = True # Original: True
## luke -> Plot mazes after load and enter interactive mode...
plot_maze = False  # Original: False
## luke -> Plot mazes and wonder round using learning paths...
plot_paths = True  # Original: False

#------------- Model Configuration -------------
#@@@@@@@@@@@@@ Learning @@@@@@@@@@@
## Number of learning steps around the maze...
T=40   #trained on 30000   #better to have one long path than mult epochs on overfit little path
## Run new dentate gyrus code
b_useNewDG = True  # Original: True
## Set overall learning rate
learningRate = 0.01  # Original: 0.01
## Learn main model weights ( Go around the steps (T) built in paths)
b_learnWeights = True  # Original: True
## Use the learned model to infer locations using original path....    
b_inference_learn = True  # Original: True

#@@@@@@@@@@@@@ Controls @@@@@@@@@@@
# 1. Randomise (original) ~ Equivalent to ~Zero Mean
ctrl_randomised_zero = True  # Original: True 
# 2. Hand-set / ideal weights -> should give best value as uses ~GPS
ctrl_handset_ideal = True  # Original: True 
# 3. Randomise (using real random value's) ~ Equivalent to ~Mean (see Andreas)
ctrl_randomised_random = True  # Original: True 

#@@@@@@@@@@@@@ Testing @@@@@@@@@@@
## Number of training epochs -> NOT SURE WHAT THIS IS?
tr_epochs = 10  # Original: 10
## Number of steps for testing the model ability to predict locations
T_test = 100  # Original: 100
## Do more learning while performing inference (e.g. roaming around paths)...
b_learn = False  # Original: False  
## Only use observations ????????????
b_obsOnly = False  # Original: False
## ??????????????????????
b_useSub = True  # Original: True
## Use the model to infer locations using a new path (test phase)....    
b_inference_test = True  # Original: True
## N_mazeSize=3 -> THIS NOW AUTOMATICALLY GENERATED from loaded image files!

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
fullImageFolder = rootFolder + imFolder + "/"
#-------------------------------------------

# Luke added exception catch
#try:

# LB: N_mazeSize as Nmax in dictGrids    

pickled_maze_name = "maze_SEED" + str(SEED) + "_DG" + str(int(b_useNewDG)) +  "_imdir" + imFolder + ".pickle"
if pickle_maze and os.path.isfile(pickled_maze_name):
    saved_maze = pickle.load( open( pickled_maze_name, "rb" ) )
    dictSenses = saved_maze[0]
    dictAvailableActions = saved_maze[1]
    dictNext = saved_maze[2]
    #N_mazeSize = saved_maze[3] 
    dictGrids = saved_maze[3]
    
    print "# Found and loaded pickled maze!"
else:
#    [dictSenses, dictAvailableActions, dictNext, N_mazeSize] = makeMaze(b_useNewDG, prefixFolder=fullImageFolder)  #make maze, including ideal percepts at each place
    [dictSenses, dictAvailableActions, dictNext, dictGrids] = makeMaze(b_useNewDG, prefixFolder=fullImageFolder)  #make maze, including ideal percepts at each place

    if pickle_maze:
        saved_maze = [dictSenses, dictAvailableActions, dictNext, dictGrids]
        pickle.dump( saved_maze, open( pickled_maze_name, "wb" ) )

# DictGrids is from location.py. Sets up a dictionary of grid cell locations from XY locations (I think!)

##### Next problem....

#dictGrids = DictGrids(dictPlaceCells,N_mazeSize)
# Luke added to graphically display maze....
#if plot_maze:
#    displayMaze(fullImageFolder, dictSenses, dictGrids, dictNext, dictAvailableActions)

# Luke Modified -> use start from first location in DictSenses
#start_location=[3,3,0] # Original setting in paths.py
start_location=np.asarray(dictSenses.keys()[0])

e = ExploreMaze(dictNext, T, start_location,debug_log='deleteme.log')
e.walk()

path_config = Paths(dictNext,dictGrids.Nmax, T, start_location)          #a random walk through the maze -- a list of world states (not percepts)
displayPaths(fullImageFolder, path_config.posLog, dictSenses, dictGrids, dictNext, dictAvailableActions)

path_config.posLog = e.posLog.copy()
displayPaths(fullImageFolder, path_config.posLog, dictSenses, dictGrids, dictNext, dictAvailableActions)
