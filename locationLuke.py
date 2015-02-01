# This is the same as location.py, but has Nmax to be given, so it can create arbitrarily large mazes.
# Has to be changed more (e.g. see which functions use Nmax). For the moment, DictGrids is working with larger mazes and all functions 
# are using customizable Nmax. But have to change the grid creation to actually take into account this Nmax

#place cell code:          th headings:
#                           
#       6                            y
#       5                            ^ th<
#       4                     1      |    \
# 9 8 7 0 1 2 3             2 * 0    * -->x
#       10                    3
#       11
#       12

#conversion between x,y locations and place cell Ids.

# Luke:
# This needs to be reworked
# @You have an x by y grid e.g. 8*8=64
# @But a more limited grid of only useable cell locations!!!!! e.g 13 cells
# @Therefore we used this code to convert between them
# Therefore: we need to convert between each x/y and the useable placeId locations
# 1. dictGrids.d (self.d) Is a mapping for all x,y values and their matching grid cell id 
# 2. placeDict is the dictionary of place cell ids to their matching x,y
# 3. need a way to index between these two.......
# 4. Make a fn
import sys
import numpy as np

# If the maze is has x in [0, ..., xMax] and y in [0, ..., yMax], then xyMax = max(xMax, yMax)
# Then, we find the nearest to xyMax (rounding upwards) number K, so that 2^Nmax = K.
default_Nmax=3

# Luke code for debugging!!!!!!
fixed_place_cell_id=False

print_messages=True
# Returns mod 2^{n+1} < 2^n
# (see Fox paper before eq. 19)
def gComponent(x, i):
    return (  np.mod(x,2**(i+1)) < 2**i )

class DictGrids:
    def __init__(self, dictPlace, Nmax=default_Nmax): # Luke removed place cell dict
    #def __init__(self, place_cell_count=13, Nmax=default_Nmax):
        self.Nmax=int(Nmax)
        #self.basis = np.array([[1,2,4],[8,16,32]])
        # We want to put a unique int id per cell. E.g. 
        # (0,0) -> 0
        # (0,1) -> 8 etc. 
        # It doesn't matter if cell (x,y) is a valid maze location, we need to do this assignment for all x times y cells,
        # x in [0, ...., xMax] and y in [0, .. yMax]
        # The following function is taking two inputs and returns a unique reversible id.
        self.basis = np.vstack((2**np.arange(self.Nmax,dtype='i2'),2**(np.arange(self.Nmax,dtype='i2')+self.Nmax)))
        self.d=dict()
        self.placeCellCount=len(dictPlace)
        #### Update - Luke save dictPlace fpor mapping 
        self.dictPlace=dictPlace # Luke removed here again
        ## Luke switched off
        #self.dictPlace2grid=dict()
                
        for x in range(int(np.sqrt(np.amax(self.basis)*2))):#(0,2*self.Nmax): # LB modified as not using full range!
            for y in range(int(np.sqrt(np.amax(self.basis)*2))):#0,2*self.Nmax):
                grids=getGrids(x,y,self.Nmax)
                id = sum(sum(grids*self.basis))
                #print id
                self.d[id]=(x,y)
        # Luke go from minimum place to max and find matching grid cell iD
        # Temp: flip keys in self.d to make life easier....
        # new_dict = dict (zip(my_dict.values(),my_dict.keys()))
             
        # Temp: flip keys in self.d to make life easier....
        self.d_flipped = dict (zip(self.d.values(),self.d.keys()))
        self.d_keys=self.d_flipped.keys()
#==============================================================================
#         Luke removed place cell dict
        dictGrid_temp = dict(zip(self.d.values(),self.d.keys()))  
        place_count=0
        #file_database=np.empty([5,no_files],dtype=int)
        self.grid2place_index=np.empty(len(self.dictPlace),dtype=[('x','i2'),('y','i2'),('grid','i2'),('place','i2')])
        for current_place_key in self.dictPlace.keys():  
            # First find matching location key in
            self.grid2place_index['x'][place_count]=current_place_key[0]
            self.grid2place_index['y'][place_count]=current_place_key[1]
#            self.grid2place_index['xy'][place_count]=current_place_key
            self.grid2place_index['grid'][place_count]=int(dictGrid_temp[current_place_key])
            self.grid2place_index['place'][place_count]=int(self.dictPlace[current_place_key])
            place_count+=1
#==============================================================================
        
        
#        range(self.dictPlace[min(self.dictPlace, key=self.dictPlace.get)],self.dictPlace[max(self.dictPlace, key=self.dictPlace.get)])
                
        print'END'
    def lookup(self, grids):
        id = sum(sum(grids*self.basis))
        #print(str(id))
        return self.d[id]
#    def place2grid(self,placeId): # Luke: New fn to convert placeId to gridId
#        gridId=None
#        return gridId        
#    def grid2place(self,gridId): # New fn to turn gridId to placeId
#        placeId=None
#        return placeId

## This should still work as this uses the original placeId
def getGrids(x,y, Nmax=default_Nmax):
    assert(x <= (2**Nmax)-1) # incorrect LB, Nmax**2
    assert(y <= (2**Nmax)-1) # incorrect LB
    #print('STOP HERE')    
        
    #Nmax = 3
    grids = np.zeros((2,Nmax))
    for i in range(0,Nmax):   #TODO should test this more, maybe a source of bugs?

        bx0=gComponent(x,i)
        by0=gComponent(y,i+1)
        grids[0,i] = bx0^by0     #xor

        bx1=gComponent(x,i+1)
        by1=gComponent(y,i)
        grids[1,i] = bx1^by1     #xor
    return grids


# Continue edits from here and below...

class Location:
    # Luke Commented def __init__(self, Nmax=default_Nmax):
    def __init__(self,dictGrids):
        foo=0
        self.Nmax=dictGrids.Nmax
        #self.grid2place_index=dictGrids.grid2place_index # Luke mapping of grid cells to places -> unfixed like original code..
        self.dictGrids=dictGrids
    # TODO for resizable
    def setPlaceId(self, placeId):
        self.placeId = placeId
        if placeId<0 or placeId>12:
            print "ERROR, tried to set placeId outside maze!"
    
    # TODO for resizable
# Luke commented    def setXY(self, x, y):
    def setXY(self, x, y):
            ### Luke new version
#==============================================================================
        self.placeId=None        
        for current_place in range(0,len(self.dictGrids.grid2place_index)):
            if self.dictGrids.grid2place_index['x'][current_place]==x and self.dictGrids.grid2place_index['y'][current_place]==y: 
                self.placeId=self.dictGrids.grid2place_index['place'][current_place]
                break
        if self.placeId==None:
            print('ERROR could not find placeId for x:',str(x), ' y:', str(y))
#==============================================================================        
#
#        if x==3 and y==3:
#            self.placeId=0
#        elif y==3 and x>3:
#            self.placeId = 0 + (x-3)
#        elif x==3 and y>3:
#            self.placeId = 3 + (y-3)
#        elif y==3 and x<3:
#            self.placeId = 6 + (3-x)
#        elif x==3 and y<3:
#            self.placeId = 9 + (3-y)
#        else:
#            print "ERROR, tried to set XY outside maze!"
    def setGrids(self, grids):
        (x,y) = self.dictGrids.lookup(grids)
        # Luke commnted        
        #self.setXY(x,y)
        # Luke modified
        self.setXY(x,y)
# LUKE COMMENTED OUT HERE AS REPEATED
#    def getGrids(self):
#        (x,y)=self.getXY()
#        return getGrids(x,y)

    # TODO for resizable # LUKE -> will send in direct place cell rather than assigning by location 
    def getXY(self):
        
#==============================================================================
        xy = np.array([0,0])
        xy[0]=self.dictGrids.grid2place_index['x'][np.where(self.dictGrids.grid2place_index['place']==self.placeId)]
        xy[1]=self.dictGrids.grid2place_index['y'][np.where(self.dictGrids.grid2place_index['place']==self.placeId)]
#===============        
        
# Luke comented        
#        if self.placeId > 9:
#            d = (self.placeId-9)* np.array([0, -1])
#        elif self.placeId > 6:
#            d = (self.placeId-6)* np.array([-1,  0])
#        elif self.placeId > 3:
#            d = (self.placeId-3)* np.array([0, 1])
#        elif self.placeId > 0:
#            d = (self.placeId-0)* np.array([1, 0])
#        else:
#            d = np.array([0,0])
#        center = np.array([3,3])
#        return center+d
        return xy
# Luke COMMENTED OUT!!!!
    # TODO for resizable
    def getGrids(self):

        Nmax = self.Nmax
        grids = np.zeros((2,Nmax))

        (x,y) = self.getXY()

        for i in range(0,Nmax):   #TODO should test this more, maybe a source of bugs?

            bx0=gComponent(x,i)
            by0=gComponent(y,i+1)
            grids[0,i] = bx0^by0     #xor

            bx1=gComponent(x,i+1)
            by1=gComponent(y,i)
            grids[1,i] = bx1^by1     #xor

        return grids


#dictGrids = DictGrids() # Luke dont want autogeneration dangerous!!!!!!
