from VTK_Code import *

def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end:
        return [path]
    if not graph.has_key(start):
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths

def getAllPaths(sm,startNode):                          # gets all the possible paths through the state machine (for testing)
    dbg = True
    guidoGraph = {}                                         # simple directed graph representation a la guido von russom
    for val in sm.objects.values():                         # for each of the non-legend states
        if hasattr(val,'nextStates'):
            nextStateList = list(itertools.chain(*val.nextStates.values()))
            guidoGraph[val.id] = nextStateList
        if val.ObjectType == 'StartState':
            sm.startStateList.append(val.id)
        if val.ObjectType == 'StopState':
            sm.stopStateList.append(val.id)
    for startState in sm.startStateList:                  # for each start state, get its sub graph
        nodesToSearch = [startState]
        currGraph = {}
        while len(nodesToSearch) > 0:
            node = nodesToSearch.pop()
            currGraph[node] = guidoGraph[node]
            nodesToSearch = nodesToSearch + guidoGraph[node]
        sm.forest[startState] = currGraph
    pathLists = {}    
    for startState in sm.startStateList:                # for each start state
        pathLists[startState] = []
        for stopState in sm.stopStateList:                  # for each stop
            paths = find_all_paths(sm.forest[startState],startState,stopState)
            if dbg: print "paths=",paths
            pathLists[startState] = paths + pathLists[startState]
    return pathLists

def testGuido():
    graph = {'A': ['B', 'C'], 
             'B': ['C', 'D'],
             'C': ['D'],
             'D': ['C'],
             'E': ['F'],
             'F': ['C']}
    print find_all_paths(graph,'A','C')    

if __name__ == "__main__":

    #testGuido()
    sm = StateMachine()
    sm.readDrawIOXMLFile("VTK 2.15.xml")
    sm.makeGraph()
    pathLists = getAllPaths(sm,'Module2Start')
    print pathLists