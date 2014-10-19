#-- In go.py
[dictSenses, dictAvailableActions, dictNext] = makeMaze(N_mazeSize, b_useNewDG, prefixFolder=fullImageFolder)     #make maze, including ideal percepts at each place
    #-- In makeMaze.py
    #- makeMaze.makeMaze:
    surfDict = makeSURFRepresentation(prefixFolder) # prefixFolder=./DCSCourtyard
        #-- In SURFExtractor.py
        #- SURFExtractor.makeSURFRepresentation(prefixFolder)
        se = SURFExtractor(prefixFolder) # Instantiate Class
        [...] # Initialise fields
        # Generate features from images. 0 refers to "byFolder", just to know where to find the pics.
        se.generateFeatureRepresentations(0)
        #- generateFeatureRepresentations
            # fills in se.files according to the rootFolder, ie loads all filenames.
            [...] 
            # For every image, we extract SURF features and merge them according to a dictionary. Then, we represent
            # each image w.r.t to the dictionary.
            self.extractDescriptors(self.files, self.maxFeaturesForMerging)
            [...]
                # self.featuresDescDict will hold the dictionary learned
                # It has a feature vector per location loc per direction:
                  # ie self.featuresDescDict[(loc,dir)].append(featureVec)
                  # from: (loc, dir) in self.descriptors.keys()
                self.generateFeatureVectors(..)
    # This function returns: dictSenses, dictAvailableActions, dictNExt, where:
    senses = Senses(n,x,y,ith,surfDict)
    dictSenses[stateCenter] = senses
    # All actions are STAY, FWD, LEFT, RIGHT, U-TURN. For some reason we exclude UTURN initially...
    dictAvailableActions[stateCenter] = [STAY,FWD,LEFT,RIGHT]
    # ... but for the possible next, we use a 5-dim vector, for the 5 possible states.
    dictNext[stateCenter] = [(x,y,ith), (x+step_xs[ith],y+step_ys[ith],ith), (x,y,ith_l), (x,y,ith_r)] 
    # There's a 1-1 correspondance between dictNext and dictAvailableActions.
    # the key_i, item_j - th entry in dictAvailableActions says if I take action item_j from location key_i, I'll find myself
    # in location dictNext[key_i,loc_j]
    # dictAvailableActions has (for every location/key loc) an vector entry, where each element of the vector
    # belongs to {0,1,2,3,4}, corresponding to STAY, FWD, LEFT, RIGHT, UTURN
    # STATE: the location loc (key in the dictionaries above) is a state, a 3-element tuple: (x,y,D).
    # x \in {0,1,2,3,4,5,6}: the x-th coordinate on the cross-maze
    # y Similarly for the y-th coordinate. E.g. 3 means center square.
    # D : Direction facing \in {0,1,2,3} ie {0: 'E', 1: 'N', 2: 'W', 3: 'S'} 

# DictGrids is from location.py. Sets up a dictionary of grid cell locations from XY locations (I think!).
# A bit confusing how the mapping from the one representation to the other is done
dictGrids = DictGrids()

#This next cell uses paths.py to generate a path object (where in the world am I at each point) and then initialises the model percepts at each point
#A path is a log of random walk locations and sensations.
path = Paths(dictNext,N_mazeSize, T)          #a random walk through the maze -- a list of world states (not percepts)
# The above code (Paths.paths) is running a random walk, where at each step we have a "current direction" of light and a state.
# If we reach the end NORTH side of the maze and the light is in 'N', then we change the position of the light.
# Elaborating on the 
    if s[2]==lightstate
    #part:
    # Check if there is a visible light ahead. If yes, then depending on the next random step,
    # and if we're in the boundary, we might actually reach the direction of the light, e.g. if
    # we're one cell before the top north location and we're facing north, then if we also make
    # a move towards north we reach the goal (? .. I think!)

# !!!! TODO: Can we use a large T for training (finding weights W) and then a smaller T for inference?
# i.e. train by simulation and then test on a few instances only.