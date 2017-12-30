#!/usr/bin/python3

import math
import random
from collections import deque
import gc
import timeit
import random
import copy
import time


def isSafe(node, r2, c2):
    for i in range(len(node[0])):
        r1 = node[0][i]
        c1 = node[1][i]
        if (rslots[r1][c1]==rslots[r2][c2] or cslots[r1][c1]==cslots[r2][c2] or d1slots[r1][c1]==d1slots[r2][c2] or d2slots[r1][c1]==d2slots[r2][c2]):
            return False
    return True


def isSafe2(node, r2, c2):
    global rslots, cslots, d1slots, d2slots,rslotsUsed,cslotsUsed,d1slotsUsed,d2slotsUsed
    if (rslotsUsed[rslots[r2][c2]] or cslotsUsed[cslots[r2][c2]] or d1slotsUsed[d1slots[r2][c2]] or d2slotsUsed[d2slots[r2][c2]]):
        return False
    return True


def createNode(row, col, slot_index):
    node = []
    node.append(row)
    node.append(col)
    node.append(slot_index)
    return node

def copy_node(node):
    child = [[],[],-1]
    child[0] = node[0][:]
    child[1] = node[1][:]
    child[2] = node[2]
    return child

##DFS
def dfs(nursery,n,p,count,count1,cur,node):
    global start, rslots, cslots, d1slots, d2slots, rslotsUsed, cslotsUsed, d1slotsUsed, d2slotsUsed, slots
    res = False
    
    currentTime = time.time()
    if currentTime-start > 290.0:
        return False

    if count==p:
        return nursery
    elif cur>=len(slots):
        return False
    elif (count+(count1-cur))<p:
        return False
    else:
        child = None
        for col in range(slots[cur][1],slots[cur][2]+1):
            row=slots[cur][0]
            rett=isSafe2(node,row,col)
            if rett!= False:
                nursery[row][col]=1
                child = copy_node(node)
                child[0].append(row)
                child[1].append(col)
                child[2] = cur
                slots[cur][3] = True
                rslotsUsed[rslots[row][col]] = True
                cslotsUsed[cslots[row][col]] = True
                d1slotsUsed[d1slots[row][col]] = True
                d2slotsUsed[d2slots[row][col]] = True
                count+=1
                cur+=1
                
                res=dfs(nursery,n,p,count,count1,cur,child)
                if res!=False:
                    return res
                else:
                    nursery[row][col]=0
                    slots[cur-1][3] = False
                    rslotsUsed[rslots[row][col]] = False
                    cslotsUsed[cslots[row][col]] = False
                    d1slotsUsed[d1slots[row][col]] = False
                    d2slotsUsed[d2slots[row][col]] = False
                    count-=1
                    cur-=1
                    
        cur=cur+1
        if child == None:
            child = copy_node(node)
        
        res=dfs(nursery,n,p,count,count1,cur,child)
        return res


##BFS
def bfs(n, p, nursery, slots):
    global start
    frontier = set()
    row = []
    col = []
    s_index = -1
    node = []
    global algo

    if(p>len(slots)):
        return False

    initialState = createNode(row, col, s_index)
    frontier = deque()
    frontier.append(initialState)
    while frontier:
        #del node
        node = frontier.popleft()
        
        s_index = node[2]
        if(s_index>len(slots)-2):
            continue
        #add an empty node so that if there is no possible square for queen on this slot, we can go ahead
        child_s_index = s_index + 1
        foundChild = False

        while (not foundChild) and child_s_index<len(slots):
            for i in range(slots[child_s_index][1],slots[child_s_index][2]+1):
                row = node[0][:]
                col = node[1][:]

                if len(row) < p:
                    if isSafe(node, slots[child_s_index][0], i):
                        foundChild = True
                        row.append(slots[child_s_index][0])
                        col.append(i)
                        child = createNode(row, col, child_s_index)
                        if (len(row)==p):
                            for j in range(p):
                                nursery[child[0][j]][child[1][j]] = 1
                            return True
                        frontier.append(child)

            if (not foundChild):
                child_s_index += 1
        
        currentTime = time.time()
        if(currentTime-start > 290.0):
            return False
    return False


##SA
def getConflicts(p, node):
    global conflictQeens, slots, rslots, cslots, d1slots, d2slots
    conflicts = [0 for i in range(p)]
    conflictQeens = [[] for i in range(2)]
    for i in range(p):
        for j in range(i+1,p):
            r1 = node[0][i]
            c1 = node[1][i]
            r2 = node[0][j]
            c2 = node[1][j]
            
            if (rslots[r1][c1]==rslots[r2][c2] or cslots[r1][c1]==cslots[r2][c2] or d1slots[r1][c1]==d1slots[r2][c2] or d2slots[r1][c1]==d2slots[r2][c2]):
                conflicts[i] += 1
                conflictQeens[0].append(i)
                conflictQeens[1].append(j)
                            
    totalConflicts = sum(conflicts)
    return totalConflicts

def getNextState(n, p, current):
    global slots, nursery, conflictQeens,availSlots
    nextState = [row[:] for row in current]
    nextSlots = [row[:] for row in slots]
    nextNursery = [row[:] for row in nursery]
    nextAvail = availSlots[:]

    itr = 0
    opp = 10 * len(nextSlots)
    lenOfSlots = len(nextSlots)
    cq = [-1,-1]
    cr = [-1,-1]
    cc = [-1,-1]
    cs = [-1,-1]
    for i in range(1):
        conflictIndex = random.randint(0,len(conflictQeens[0])-1)
        cq[0] = conflictQeens[0][conflictIndex]
        cr[0] = nextState[0][cq[0]]
        cc[0] = nextState[1][cq[0]]
        cs[0] = nextState[2][cq[0]]
        
        cq[1] = conflictQeens[1][conflictIndex]
        cr[1] = nextState[0][cq[1]]
        cc[1] = nextState[1][cq[1]]
        cs[1] = nextState[2][cq[1]]

        nextSlots[cs[0]][3] = False
        nextSlots[cs[1]][3] = False
        if p!=lenOfSlots:
            nextAvail.append(cs[0])
            nextAvail.append(cs[1])

        nextNursery[cr[0]][cc[0]] = 0
        nextNursery[cr[1]][cc[1]] = 0

        for k in range(2):
            foundSlot = False
            while not foundSlot:
                if p == lenOfSlots:
                    s_index = cs[k]
                else:
                    s_index = random.randint(0,len(nextAvail)-1)
                    s_index  = nextAvail[s_index]
                    
                if(nextSlots[s_index][3]==False):
                    r = nextSlots[s_index][0]
                    c = random.randint(nextSlots[s_index][1],nextSlots[s_index][2])
                    if nextNursery[r][c]==0:
                        nextNursery[r][c] = 1                        
                        foundSlot = True
                        nextSlots[s_index][3] = True
                        if p != lenOfSlots:
                            nextAvail.remove(s_index)
                        nextState[0][cq[k]] = r
                        nextState[1][cq[k]] = c
                        nextState[2][cq[k]] = s_index
            if not foundSlot:
                nextSlots[cs[k]][3] = True
                nextNursery[cr[k]][cc[k]] = 1
    return nextState, nextSlots, nextNursery, nextAvail 


def simulated_annealing(n, p):
    global conflictQeens, start, nursery, slots, availSlots
    placedQueens = 0
    emptySlots = len(slots)
    row = []
    col = []
    sc= []
    while placedQueens!=p and emptySlots > 0:
        s_index = random.randint(0,len(slots)-1)
        
        if(slots[s_index][3]==False):
            r = slots[s_index][0]
            c = random.randint(slots[s_index][1],slots[s_index][2])
            if nursery[r][c]==0:
                row.append(r)
                col.append(c)
                sc.append(s_index)
                slots[s_index][3]=True

                emptySlots -= 1
                placedQueens += 1
                nursery[r][c] = 1


    if placedQueens!=p:
        return False

    if len(slots) < p:
        return False

    current = [[] for i in range(3)]
    current[0] = row
    current[1] = col
    current[2] = sc

    totalSlots = len(slots)
    availSlots= []
    for i in range(totalSlots):
        if slots[i][3]==False:
            availSlots.append(i)
    
    Ec = getConflicts(p, current)
    ############### Initialize
    Tmax = 24   
    Tmin = 0.13
    Tsteps = 2200000.0 
    updates = 100
    best_state = None
    bestE = None
    
    Emin = -(p-1)

    Tf = -math.log(Tmax/Tmin)
    T = Tmax
    best_state = current
    bestE = Ec
    Ec = bestE
    step = 1
    trails = 0
    accepts = 0
    improves = 0
    currentTime = start+1
    Ec = getConflicts(p, current)
    ################### main loop
    while step < Tsteps and T>=0:
        step += 1
        trails += 1
        T = 1/math.log(p+step)

        if Ec == 0:
            return True
        nextState, nextSlots, nextNursery, nextAvail = getNextState(n, p, current)
        En = getConflicts(p, nextState)
        dE = En - Ec
        if dE <= 0:
            improves += 1
            accepts += 1
            current = nextState
            nursery = nextNursery
            slots = nextSlots
            availSlots = nextAvail
            Ec = En
        else:
            probability = math.exp(-dE/T)
            #probability = (end - time.time())/(end-start)
            num = random.uniform(0,1)
            if num < probability:
                accepts += 1
                current = nextState
                nursery = nextNursery
                slots = nextSlots
                availSlots = nextAvail
                Ec = En
        currentTime = time.time()
        if currentTime - start > 290.0:
            return False
    return False




#measure start time for SA
start = time.time()
end = start + 290.0

#read input.txt
input = open("input.txt","r")

algo = (input.readline()).rstrip()
n = int((input.readline()).rstrip())
p = int((input.readline()).rstrip())

nur = [[0]*n]*n
for i in range(n):
    nur[i] = (input.readline()).rstrip()

input.close()

#store queen/lizard positions in ith row 
t_row = [[] for i in range(n)]
#store queen/lizard positions in ith column
t_col = [[] for i in range(n)]
#store queen/lizard positions in (i+j)th diagonal
t_diag1 = [[] for i in range(2*n)]
#store queen/lizard positions in (n-i+j-1)th diagonal
t_diag2 = [[] for i in range(2*n)]

conflictQeens = [[] for i in range(p)]
maxConflictQ = -1

nursery = [[0] * n for i in range(n)]

for i in range(n):
    for j in range(n):
        nursery[i][j] = int(nur[i][j])
        if nursery[i][j] == 2:
            t_row[i].append(j)
            t_col[j].append(i)
            t_diag1[i+j].append([i, j])
            t_diag2[n-i+j-1].append([i,j])

slots = []
for i in range(n):
    if (len(t_row[i])>0):
        first = 0
        last = t_row[i][0]-1
        if first <= last:
            slots.append([i, first, last, False])
        for j in range(1,len(t_row[i])):
            first = last+2
            last = t_row[i][j]-1
            if first <= last:
                slots.append([i, first, last, False])
        first = last+2
        last = n-1
        if first <= last:
            slots.append([i, first, last, False])
    else:
        slots.append([i,0,n-1,False])

rslots = [[-1 for i in range(n)] for j in range(n)]
slotid = 0
for i in range(n):
    j = 0
    while j < n:
        isThereSlot = False
        while j<n and nursery[i][j]==2:
            j+=1
        while j<n and nursery[i][j]==0:
            rslots[i][j] = slotid
            isThereSlot = True
            j+=1
        if isThereSlot == True:
            slotid += 1

rslotsUsed = [False for i in range(slotid)]

cslots = [[-1 for i in range(n)] for j in range(n)]
slotid = 0
for j in range(n):
    i = 0
    while i<n:
        isThereSlot = False
        while i<n and nursery[i][j]==2:
            i+=1
        while i<n and nursery[i][j]==0:
            cslots[i][j] = slotid
            isThereSlot = True
            i+=1
        if isThereSlot == True:
            slotid += 1

cslotsUsed = [False for i in range(slotid)]

d1slots = [[-1 for i in range(n)] for j in range(n)]
slotid = 0
for k in range(2*n):
    yMin = max(0, k - n + 1)
    yMax = min(n - 1, k)
    y = yMin
    while y<=yMax:
        x = k-y
        isThereSlot = False
        while y<=yMax and nursery[y][x]==2:
            y+=1
            x = k-y
        while y<=yMax and nursery[y][x]==0:
            isThereSlot = True
            d1slots[y][x] = slotid
            y+=1
            x = k-y
            
        if isThereSlot == True:
            slotid +=1

d1slotsUsed = [False for i in range(slotid)]

d2slots = [[-1 for i in range(n)] for j in range(n)]
slotid = 0
for k in range(2*n):
    yMin = max(0, k - n + 1)
    yMax = min(n - 1, k)
    y = yMin
    while y<=yMax:
        x = (n-1)-(k-y)
        isThereSlot = False
        while y<=yMax and nursery[x][y]==2:
            y+=1
            x = (n-1)-(k-y)
        while y<=yMax and nursery[x][y]==0:
            isThereSlot = True
            d2slots[x][y] = slotid
            y+=1
            x = (n-1)-(k-y)
            
        if isThereSlot == True:
            slotid +=1

d2slotsUsed = [False for i in range(slotid)]

boolean = False

if  algo == "DFS":
    count=0
    cur=0
    count1=len(slots)
    row = []
    col = []
    s_index = -1
    initialState = createNode(row, col, s_index)
    boolean = dfs(nursery,n,p,count,count1,cur,initialState)
elif algo == "BFS":
    boolean = bfs(n, p, nursery, slots)
elif algo == "SA":
    boolean = simulated_annealing(n, p)
else:
    print("UNKNOWN INPUT")


output = open("output.txt","w")

if boolean:
    output.write("OK\n")
    for i in range(n):
        for j in range(n):
            output.write(str(nursery[i][j]))
        output.write("\n")
else:
    output.write("FAIL\n")

output.close()

