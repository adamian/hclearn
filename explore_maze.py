#import GPy
#from GPy.util.linalg import jitchol, tdot, dtrtrs, dpotri, pdinv
from GPy.util.linalg import jitchol, pdinv
import numpy as np
from cffun import *
import sys

class ExploreMaze:
    def __init__(self, dictNext, T_max, start_location, debug_log=None, momentum=0.9):
        self.T_max = T_max
        self.start_location = start_location
        self.dictNext = dictNext
        self.debug_log = debug_log
        self.momentum = momentum

        self.posLog = np.zeros((T_max, 3),dtype='int16')  #for training, ground truth states. Includes lightState
        # All possible positions on the maze
        self.allPos = np.array(dictNext.keys())#, dtype='float64')
        # Match all possible positions with their row index in allPos
        self.dictIndex = {}
        for j in range(self.allPos.shape[0]):
            self.dictIndex[tuple(self.allPos[j])] = j

    def walk(self):
        dictNext = self.dictNext
        T_max = self.T_max
        start_location = self.start_location
        allPos = self.allPos.copy()
        dictIndex = self.dictIndex
        
        #### TODO: Give more "priority" to the location, rather than the heading.
        allPosCov = allPos.copy()

        log_file = None
        if self.debug_log == 'stdout':
            log_file = sys.stdout
        elif self.debug_log is not None:
            log_file = open(self.debug_log,'w+')

        # Linear kernel for building cov. functions
        #kernel = GPy.kern.Linear(allPos.shape[1]) + GPy.kern.White(allPos.shape[1])
        # Y doesn't matter! Can be anything...
        #m = GPy.models.GPRegression(X=allPos, Y=allPos, kernel=kernel)

        # The full covariance matrix on all possible positions
        #SigmaC = m.kern.K(allPos,allPos)
        
        #import pdb; pdb.set_trace()
        SigmaC = np.dot(allPosCov, allPosCov.T) + 0.0000000001*np.eye(allPosCov.shape[0])

        # All indices (indexing allPos or, equivalently, sigmaC)
        V = range(allPos.shape[0])
        # Set of chosen indices, initially just the start location
        Ci = []
        Ci.append(dictIndex[tuple(start_location)])
        notCi = list(set(V) - set(Ci))
        random_selections = 0
        cur_loc = start_location
        self.posLog[0,0:3]=cur_loc
        # For every position we want to add, evaluate and add a position according to Uncertainty
        t = 0
        while t<T_max-1:
            t += 1
            #for t in range(1,T_max):
            if log_file is not None:
                print >> log_file, "\n\n# # # # t: " + str(t) + "\n"            
            s_nexts = dictNext[tuple(cur_loc)]          #possible next locations
            if log_file is not None:
                print >> log_file,  "\t # s_nexts: ",
                print >> log_file,  s_nexts
                print >> log_file,  ""
            Delta = np.zeros((len(notCi),1)) * np.nan
            for j in range(len(notCi)):
                # j indexes notCi. The elements INSIDE notCi index allPos, that's what we want. p is current notCi
                p = notCi[j]
                if tuple(allPos[p]) not in set(s_nexts):
                    Delta[j] = -np.inf
                    continue
                else:
                    not_CiUp = list(set(notCi) - set([p])) # Does not contain p
                    Sigma_a = approxConditionals(SigmaC, p, Ci);
                    Delta[j] = Sigma_a
                    if log_file is not None:
                        print >> log_file,  "\t # Examined: " + str(p) + " : ", 
                        print >> log_file,  str(allPos[p]),
                        print >> log_file, " Delta: " + str(Sigma_a)
                        print >> log_file,  ""
            # None of the unexplored locations is valid in s_nexts. Choose randomly.
            # TODO: Bias towards same direction.
            if np.isinf(Delta).all():
                # If choose randomly, at least preserve heading
                tmpList = []
                #for jn in range(len(s_nexts)):
                #    if s_nexts[jn][2] == cur_loc[2]:
                #        tmpList.append(s_nexts[jn])
                # If no available choices can preserve heading (ie we're seeing a wall), just 
                # choose whatever available at random (same if it's just the trivial stay state)
                if tmpList == []:
                    tmpList = s_nexts
                elif len(tmpList)==1 and np.all(tmpList[0] == cur_loc):
                    tmpList = s_nexts
                pMaxPos = random.randrange(0,len(tmpList))  #choose a random next location
                cur_loc = tmpList[pMaxPos]
                random_selections += 1
                if log_file is not None:
                    print >> log_file,  "\t # Selected randomly: ",
                    print >> log_file,  cur_loc
                    print >> log_file,  ""
            else:
                tmpMax = np.max(Delta)
                pMaxPos = np.argmax(Delta)
                lhat = notCi[pMaxPos]
                if log_file is not None:
                    print >> log_file,  "\t # lhat: " + str(lhat) + " : ",
                    print >> log_file,  str(allPos[lhat])
                    print >> log_file,  ""

                # Add this point to Ci and remove it from notCi
                Ci.append(lhat)
                Ci.sort()
                notCi = list(set(notCi)-set([lhat]))
                notCi.sort()
                cur_loc = self.allPos[lhat]
            self.posLog[t,0:3]=cur_loc
            #i = random.randrange(0,len(s_nexts))  #choose a random next location
            #start_location = s_nexts[i]
            if log_file is not None:
                #print >> log_file,  "\t # notCi: "
                #print >> log_file,  allPos[notCi].T
                print >> log_file,  "\t # Ci: "
                for item in Ci:
                    print >> log_file, allPos[item],
                print >> log_file, ""
        if log_file is not None:
            print >> log_file,  "#### Random selections: ",
            print >> log_file,  "{0:.0f}%".format(float(random_selections)/T_max * 100)
            log_file.close()

    def walk_bidirect(self):
        dictNext = self.dictNext
        T_max = self.T_max
        start_location = self.start_location
        allPos = self.allPos.copy()
        dictIndex = self.dictIndex
        
        #### TODO: Give more "priority" to the location, rather than the heading.
        allPosCov = allPos.copy()

        log_file = None
        if self.debug_log == 'stdout':
            log_file = sys.stdout
        elif self.debug_log is not None:
            log_file = open(self.debug_log,'w+')

        # Linear kernel for building cov. functions
        #kernel = GPy.kern.Linear(allPos.shape[1]) + GPy.kern.White(allPos.shape[1])
        # Y doesn't matter! Can be anything...
        #m = GPy.models.GPRegression(X=allPos, Y=allPos, kernel=kernel)

        # The full covariance matrix on all possible positions
        #SigmaC = m.kern.K(allPos,allPos)
        
        #import pdb; pdb.set_trace()
        SigmaC = np.dot(allPosCov, allPosCov.T) + 0.0000000001*np.eye(allPosCov.shape[0])

        # All indices (indexing allPos or, equivalently, sigmaC)
        V = range(allPos.shape[0])
        # Set of chosen indices, initially just the start location
        Ci = []
        Ci.append(dictIndex[tuple(start_location)])
        notCi = list(set(V) - set(Ci))
        random_selections = 0
        cur_loc = start_location
        self.posLog[0,0:3]=cur_loc
        # For every position we want to add, evaluate and add a position according to Uncertainty
        t = 0
        while t<T_max-1:
            t += 1
            #for t in range(1,T_max):
            if log_file is not None:
                print >> log_file, "\n\n# # # # t: " + str(t) + "\n"            
            s_nexts = dictNext[tuple(cur_loc)]          #possible next locations
            if log_file is not None:
                print >> log_file,  "\t # s_nexts: ",
                print >> log_file,  s_nexts
                print >> log_file,  ""
            
            # New part: If we're in position cur_pos, we assume that we can turn the head around
            # and look at all positions of the same x,y but all possible headings.
            # We add these positions in the posLog vector as well as in Ci. Further, we add the s_next
            # of these new positions to the current s_next, but we remove these new positions from the
            # old s_next.
            tmp_s_nexts = []
            for j in range(len(s_nexts)):
                if s_nexts[j][0] == cur_loc[0] and s_nexts[j][1] == cur_loc[1]:
                    if s_nexts[j][2] == cur_loc[2]:
                        tmp_s_nexts.append(s_nexts[j])
                        # continue # This is the exact same loc
                    else: # This is the other side in the same loc
                        lhat = dictIndex[s_nexts[j]]
                        Ci.append(lhat)
                        Ci.sort()
                        notCi = list(set(notCi)-set([lhat]))
                        notCi.sort()
                        tmp_loc = self.allPos[lhat]
                        if t < T_max:
                            self.posLog[t,0:3]=tmp_loc
                        t+=1
                        lhat_s_nexts = dictNext[tuple(tmp_loc)]
                        for jj in range(len(lhat_s_nexts)):
                            tmp_s_nexts.append(lhat_s_nexts[jj])
                else:
                    tmp_s_nexts.append(s_nexts[j])
            s_nexts = tmp_s_nexts
            if log_file is not None:
                print >> log_file,  "\t # tmp_s_nexts: ",
                print >> log_file,  s_nexts
                print >> log_file,  ""
                print >> log_file,  "\t # Ci_new: "
                for item in Ci:
                    print >> log_file, allPos[item],
                print >> log_file, ""

            Delta = np.zeros((len(notCi),1)) * np.nan
            for j in range(len(notCi)):
                # j indexes notCi. The elements INSIDE notCi index allPos, that's what we want. p is current notCi
                p = notCi[j]
                if tuple(allPos[p]) not in set(s_nexts):
                    Delta[j] = -np.inf
                    continue
                else:
                    not_CiUp = list(set(notCi) - set([p])) # Does not contain p
                    Sigma_a = approxConditionals(SigmaC, p, Ci);
                    Delta[j] = Sigma_a
                    if log_file is not None:
                        print >> log_file,  "\t # Examined: " + str(p) + " : ", 
                        print >> log_file,  str(allPos[p]),
                        print >> log_file, " Delta: " + str(Sigma_a)
                        print >> log_file,  ""
            # None of the unexplored locations is valid in s_nexts. Choose randomly.
            # TODO: Bias towards same direction.
            # TODO: Make the robot move towards regions of greater uncertainty. e.g. if all neighbours
            # are already visited, move towards regions that are uncertain (e.g. by checking the uncertainty
            # in subsequent simulated steps with constant heading until a non-visited region is found, simulating memory in the sense
            # of backtracking by simulating steps of previously observed regions.)
            if np.isinf(Delta).all():
                # If choose randomly, at least preserve heading and not stay still
                tmpList = []
                for jn in range(len(s_nexts)):
                    if s_nexts[jn][2] == cur_loc[2] and not np.all(s_nexts[jn] == cur_loc):
                        tmpList.append(s_nexts[jn])
                # Actually use some momentum, ie preserve heading with high probability but not necessarily.
                if np.random.rand() > self.momentum:
                    tmpList = s_nexts

                # If no available choices can preserve heading (ie we're seeing a wall), just 
                # choose whatever available at random (same if it's just the trivial stay state)
                if tmpList == []:
                    tmpList = s_nexts
                elif len(tmpList)==1 and np.all(tmpList[0] == cur_loc):
                    tmpList = s_nexts
                pMaxPos = random.randrange(0,len(tmpList))  #choose a random next location
                cur_loc = tmpList[pMaxPos]
                random_selections += 1
                if log_file is not None:
                    print >> log_file,  "\t # Selected randomly: ",
                    print >> log_file,  cur_loc
                    print >> log_file,  ""
            else:
                tmpMax = np.max(Delta)
                pMaxPos = np.argmax(Delta)
                lhat = notCi[pMaxPos]
                if log_file is not None:
                    print >> log_file,  "\t # lhat: " + str(lhat) + " : ",
                    print >> log_file,  str(allPos[lhat])
                    print >> log_file,  ""

                # Add this point to Ci and remove it from notCi
                Ci.append(lhat)
                Ci.sort()
                notCi = list(set(notCi)-set([lhat]))
                notCi.sort()
                cur_loc = self.allPos[lhat]
            if t < T_max:
                self.posLog[t,0:3]=cur_loc
            #i = random.randrange(0,len(s_nexts))  #choose a random next location
            #start_location = s_nexts[i]
            if log_file is not None:
                #print >> log_file,  "\t # notCi: "
                #print >> log_file,  allPos[notCi].T
                print >> log_file,  "\t # Ci: "
                for item in Ci:
                    print >> log_file, allPos[item],
                print >> log_file, ""
        if log_file is not None:
            print >> log_file,  "#### Random selections: ",
            print >> log_file,  "{0:.0f}%".format(float(random_selections)/T_max * 100)
            log_file.close()

def sliceArr(s,A,B):
    return np.array(s[A])[:,B]

def approxConditionals(s, lhat, rest=None):
    """
    y: Full mean (all dimensions)
    s: Full cov. matrix (all dimensions)
    lhat: The dimensions for which to compute
          p(lhat | rest).
    
    a = lhat (unobserved indices) |a| - dimensional
    b = rest (observed indices)   |b| - dimensional
    
    (a,b) ~ N(M, S)
    Then:
    S_{a|b} = Saa - Sab Sbb^-1 Sba
    M_{a|b} = Sab Sbb^-1 Mb        
    """
    #  y is L x 1
    #  s is L x L
    L = s.shape[1]
    if rest is None:
        A = list(set(range(L)) - set([lhat]))
    else:
        A = rest
    # Slice s, to get the indices denoted by A,A (ie all rows in A and columns in A)
    sAA = sliceArr(s,A,A)
    try:
        inv_sAA = pdinv(sAA)[0]
    except:
        inv_sAA = pdinv(sAA + 0.00000001*np.eye(sAA.shape[0],sAA.shape[1]))[0]
        print "Warning: Added more jitter!"
    sc = sliceArr(s,[lhat],A)
    sInvs = np.dot(np.dot(sc,inv_sAA),sc.T)

    s_U = sliceArr(s,[lhat],[lhat]) - sInvs
    return s_U
