import string
import sys
import xml.etree.ElementTree as etree
import json
from VTKTests import *
import itertools

class State:                                                        # Base class representing nodes of a graph
    def __init__(self,dic,sm):                                          # initialize
        for attrKey in dic.keys():                                          # take all the items from the GUI xml and add to python object
            setattr(self,attrKey,dic[attrKey])
        self.prompts = None                                                 # list of prompts
        self.parents = []                                                   # all objects from the GUI can have parents and children
        self.children = []
        self.nextStates = {}                                                # after the GUI is put into a graph,nextStates points to next nodes
        self.traversed = False                                              # when a simulation is run, this tracks if the nodes has been traversed
    def addPrompts(self,dic,sm):                                        # add prompts
        promptNumbers = ['1','2','3','4','5']                               # you can have up to five ordered prompts in a state.  add more here if desired.
        for aNum in promptNumbers:
            nameStr = "Prompt_" + aNum + "_Name"
            if dic.has_key(nameStr):
                aPrompt = Prompt(dic[nameStr])
                if dic.has_key('Prompt_'+aNum+'_Text'):
                    aPrompt.text = dic['Prompt_'+aNum+'_Text']
                self.prompts.append(aPrompt.name)
                sm.addPrompt(aPrompt)
    def dump(self):
        #return vars(self)
        return self.__dict__
    def getPrompts(self):
        return self.prompts
    def run(self,sm):                                                   # to run a state, make a runResult object and get the next state
        runResult = RunResult()
        try:
            runResult.nextState = self.nextStates['default']
        except KeyError:
            if len(self.nextStates) == 1:
                runResult.nextState = self.nextStates.values()[0]
        return runResult

class RunResult:                                                    # When a state is run, it returns its results using this structure
    def __init__(self):
        self.prompts = []                                               # this is the list of prompts the the state would output to user
        self.nextState = []                                             # this is the list of usually one but sometimes more than one next state to go to
    def dump(self):
        return vars(self)

class StartState(State):                                            # Start of the application or a sub dialog
    def __init__(self,dic,sm):
        State.__init__(self,dic,sm)
        self.callFromReturnToDict = {}                                  # if a start state is called by a subdialog state, this points back to the
class StopState(State):                                             # Where we stop
    def __init__(self,dic,sm):
        State.__init__(self,dic,sm)
  
class Prompt:                                                       # This is the text shown/played back to the user
    def __init__(self,name):
        self.name = name
        self.text = None
    def dump(self):
        print self.name,self.text

class PromptState(State):                                           # A Prompt state when run plays/shows text to the user
    def __init__(self,dic,sm):
        State.__init__(self,dic,sm)
        self.prompts = []
        self.objectType = 'PromptState'
        self.addPrompts(dic,sm)
    def run(self,sm):
        dbg = False
        if dbg: print "Info: Prompt.run",self.dump()
        runResult = RunResult()
        runResult.prompts = self.prompts
        try:
            runResult.nextState = self.nextStates['default']
        except KeyError:
            if len(self.nextStates) == 1:
                runResult.nextState = self.nextStates.values()[0]
        return runResult
        
class Grammar:                                                      # User's input is parsed by a grammar, returning meaning
    def __init__(self,dic,sm):
        dbg = False
        if dbg: print "Info: initializing grammar"
        for attrKey in dic.keys():
            setattr(self,attrKey,dic[attrKey])
        self.text2meanings = {}
        self.semanticMeanings = []
        props = dir(self)
        if dbg: print "props=",props
        for prop in props:
            if prop.startswith('Meaning'):
                words = getattr(self,prop).split(',')
                self.semanticMeanings.append(words[0])                              # the first word in the list is the semantic meaning
                for word in words:
                    self.text2meanings[word] = words[0]
        sm.grammarName2ObjectIndex[self.ObjectName] = self.id                           
        if sm.grammars.has_key(self.ObjectName):                                    # the name is like 'YNQ'
            print "Info: Same grammar name seen twice:",self.ObjectName
        else:
            sm.grammars[self.ObjectName] = self
        if dbg:
            print "self.vars=",vars(self)
            print "Info: done initializing grammar"
    def Parse(self,text):
        try:
            return self.text2meanings[text]
        except KeyError:
            pass
        else:
            return None
    def getPossibleInputs(self):
        return self.text2meanings
        
class GrammarState(State):                                          # a grammar state plays a prompt, collects user input and parses it
    def __init__(self,dic,sm):                                          # initialize with the data from the GUI
        State.__init__(self,dic,sm)
        self.prompts = []
        self.addPrompts(dic,sm)
        self.grammarNames = []
        if dic.has_key('Grammar_1_Name'):                                   # currently there are two grammars per grammar state, but could add more here
            self.grammarNames.append(dic['Grammar_1_Name'])
        if dic.has_key('Grammar_2_Name'):
            self.grammarNames.append(dic['Grammar_2_Name'])
        self.grammars = {}
    def run(self,sm):                                                   # this gets the prompts (if any) of the grammar state and returns them to the main run method
        dbg = False
        if dbg: print "Info: running grammar state",self.__dict__
        runResult = RunResult()                                             # to run a state make a new run result structure
        runResult.prompts = self.getPrompts()                               # put any prompts the state has into it
        return runResult
    def parseInput(self,text):                                          # after the prompts (if any) are rendered, the main state machine run method calls parseInput 
        dbg = False
        meanings = []
        for aGrammarName in self.grammarNames:
            aGrammar = self.grammars[aGrammarName]
            if dbg: print "working in runParse with aGrammar",aGrammar.__dict__
            result = aGrammar.Parse(text)
            if dbg: print "in runparse, result=",result,"type(result)=",type(result)
            if result:
                if result not in meanings:
                    meanings.append(result)
        return meanings
    def getPossibleInputs(self):                                        # this is used to run simulations - it gathers all possible inputs at a grammar state
        dbg = False
        possibleInputs = []                                                 # this is a list of text to meaning dicts
        for aGrammarName in self.grammarNames:
            aGrammar = self.grammars[aGrammarName]
            if dbg: print "working in getPossibleInputs with aGrammar",aGrammar.__dict__
            result = aGrammar.getPossibleInputs()
            if dbg: print "in getPossibleInputs, result=",result,"type(result)=",type(result)
            if result:
                if result not in possibleInputs:
                    possibleInputs.append(result)
        return possibleInputs
        

class Edge(State):                                                  # These are the arcs or arrows connecting up the graph
    def __init__(self,element,sm):
        dbg = False
        if dbg:
            print "making edge:",json.dumps(self.__dict__) 
        for attrKey in element.attrib.keys():
            setattr(self,attrKey,element.attrib[attrKey])
        props = element.getchildren()[0]
        if props.attrib.has_key('source'):
            self.source = props.attrib['source']
        else:
            print "***Warning: no source for edge",json.dumps(self.__dict__)
            self.source = ""
        if props.attrib.has_key('target'):
            self.target = props.attrib['target']
        else:
            print "***Warning: no target for edge",json.dumps(self.__dict__)
            self.target = ""           
        sm.edges[self.id] = self

class DecisionState(State):                                         # Branches flow through the graph depending on variables' values
    def __init__(self,dic,sm):
        dbg = False
        if (dbg):print "--> DecisionState init\n\t",dic
        State.__init__(self,dic,sm)
        if (dbg):print "<-- DecisionState init"
    def run(self,sm):
        dbg = False
        if dbg: print "Info: in DecisionState.run"
        runResult = RunResult()
        try:                                                                # get the variable name to branch on
            variableName = getattr(self,'VariableName')                         # e.g. 'feelings'
            if sm.db.has_key(variableName):                                        # if it has been set in the db by some other state
                varValue = sm.db[variableName]                                         # get the value (e.g. 'bad')
                if self.nextStates.has_key(varValue):                               # if that is an index in the nextStates dic of the decision object                         
                    runResult.nextState = self.nextStates[varValue]                    # get the next state number to go to
        except AttributeError:
            print "in Decisionstate.run, I decision state has no attribute 'VariableName'"
        return runResult

class ComputationalState(State):                                    # Sets variables to values
    def __init__(self,dic,sm):
        dbg = False
        State.__init__(self,dic,sm)
        if dic.has_key('label'):
            self.codeBlock = dic['label']
        self.nextState = None
        sm.objects[self.id] = self
        if dbg: print self.codeBlock
    def run(self,sm):
        dbg = False
        if dbg: print "  Info: in computationalState.run"
        runResult = RunResult()
        try:                                                                # find the next state to go to
            runResult.nextState = self.nextStates['default']
        except KeyError:
            if len(self.nextStates) == 1:
                nextStateID = self.nextStates.values()[0]
                if dbg: print "  Info: in computationalState.run nextStateID=",nextStateID
                runResult.nextState = nextStateID
        if self.codeBlock:                                                  # execute the code block (put the results in the DB)                                            
            if dbg: print "  Info: executing code block=",self.codeBlock
            attr,val = self.codeBlock.split("=")
            if dbg: print "  Info: executing attr,val=",attr,val
            sm.db[attr.strip()] = val.strip()
        return runResult

# {'cameFromGoToStates': {}, 'ObjectName': 'SayGoodbye', 'SubDialogStartName': 'SayGoodbyeStart', 'nextStates': {'default': ['327']}, 'children': ['328'],
#   'Module': 'eg2', 'label': 'Bye', 'prompts': None, 'parents': ['23', '326'],
#    'nextState': None, 'codeBlock': 'Bye', 'id': '325', 'ObjectType': 'SubDialog'}

# a subdialog state is used to refer to a section of code that can be called as a gosub or a goto.  In the state's metadata, the property that contains the go-to state's name is SubDialogStateName.
# In the example, the label on the subdialog state is Bye and the label on the start state of the subdialog is SubDialogStart in the module named subDialog. 
# If there is an arrow coming out of a subdialogstate, then there should be a return symbol terminating the referred-to subdialog.  After traversing the subdialog, when the return state is encountered,
# processing continues at the next state pointed at by arrow coming out of the subdialogstate symbol (Main Stop in the example).
# If there is not an arrow coming out of the subdialogstate symbol, then think of it as a labelled goto, meaning processing just continues on at the state named SubDialogStateName
# A given subDialog symbol can be used multiple times (and multiple objects will be created) while the start state of the subdialog being called will only be created once.
# A stack in the state machine keeps track when a subdialog.run is called by pushing the name of the subdialog state on the stack.
# When the main loop encounters a return state, the main loop will pop the stack to get the name of the last name of the calling subdialogstate, and from that get the name of the
# resumeOnReturn state (e.g., Module2Stop).
  
class SubDialogState(State):                                        # Think 'subroutine'
    def __init__(self,dic,sm):
        dbg = False
        self.SubDialogStateName = None                                      # this is the start state name of the  immediate next state to run
        State.__init__(self,dic,sm)
        self.nextState = None
        sm.objects[self.id] = self
        self.resumeOnReturn = None                                          # this is the name of the state to resume processing on 
    def run(self,sm):                                                       
        dbg = False
        if dbg: print "Info: in SubDialogState.run"
        runResult = RunResult()
        try:                                                                # find the name of the subDialog state to go to next (start of a subdialog)
            gotostate=self.SubDialogStartName
            if dbg: print "Info: in SubDialogState.run: goto state=",gotostate, "id=",sm.objectName2Index[gotostate],"\n"
            runResult.nextState.append(sm.objectName2Index[gotostate])
        except KeyError:
            runResult.nextState.append(None)
        return runResult
    def resumeRun(self,sm):                                                 # where to go after a return state is encountered in the subdialog
        dbg = False
        if dbg: print "Info: in SubDialogState.resumeRun"
        try:                                                               
            return self.nextStates['default']
        except KeyError:
            return self.nextStates.values()[0][0]

class StateMachine:                                                 # Creates the data structures from input xml, runs it
    def __init__(self):                                             # initialize
        dbg = True
        if dbg: print "initializing state machine"
        self.objects = {}                                                   # all the objects in the state machine indexed by their ID
        self.edges = {}                                                     # the edges (arcs, arrows) from the GUI
        self.prompts = {}                                                   # the prompts the system gives to the user
        self.grammars = {}                                                  # the grammars the system uses to parse user input
        self.grammarStateIDs = []                                           # the grammar states
        self.grammarName2ObjectIndex = {}                                   # a way to get the grammar object ID from the grammar name
        self.objectName2Index = {}                                          # a way to get the object ID from an object name
        self.db = {}                                                        # this stores run time data values
        self.reconcilationOK = True                                         # boolean to make sure that all grammar names referenced in the GUI have an actual grammar to use
        self.subDialogStack = []                                            # when a subdialog symbol state is run, its ID is put on this stack.  When a return state is encountered
        self.subDialogStateList = []                                        # list of subdialog state IDs
        self.startStateList = []                                            # list of all start states
        self.stopStateList = []                                             # list of all end states
        self.forest = {}                                                    # paths through all start states to terminating states      

    def addPrompt(self,newPrompt):                                      # adds a prompt
        if self.prompts.has_key(newPrompt.name):
            oldPrompt = self.prompts[newPrompt.name]
            if not oldPrompt.text == newPrompt.text:
                print "Warning: duplicate prompt names with different text",oldPrompt.dump(),newPrompt.dump(),"keeping old"
        else:
            self.prompts[newPrompt.name] = newPrompt
            
    def addGrammar(self,newGrammar):                                    # adds a grammar
        if self.grammars.has_key(newGrammar.name):
            oldGrammar = self.grammars[newGrammar.name]
            if not oldGrammar.is_same_as(newGrammar):
                print "Warning: duplicate grammar names with different text2 meanings",newPrompt.name,oldPrompt.name,"keeping old"
        else:
            self.grammars[newGrammar.name] = newGrammar
            
    def jsize(self,thing):                                              # creates JSON from an object
        return ','.join([json.dumps(obj.__dict__,sort_keys=True,indent=4,separators=(',',':')) for obj in thing.values()])

    def readDrawIOXMLFile(self,fileName):                               # parses an exported draw.io regular XML graphical VUI design into python objects
        dbg = False
        if dbg: print "--> readXMLFile"
        tree = etree.parse(fileName)                                    # parse the XML file
        mxGraphModel = tree.getroot()                                   # get the root
        root = mxGraphModel.getchildren()[0]                            # get the children
        for child in root:                                              # for each object in the file
            if child.tag == 'object':                                       # parse it and assign it to a python representation
                self.objectReadHandler(child)
        if dbg: print "<-- readXMLFile"

    def objectReadHandler(self,element):                                # parse the xml object from the GUI
        dbg = False
        if dbg: print "--> objectHandler\n\t",element.attrib
        if element.attrib.has_key('Module'):                            # if the object has a module attribute
            if element.attrib['Module'] != 'legend':                        # if the module is not 'legend' (we don't want them in the graph)
                if element.attrib.has_key('ObjectType'):                        # if we have an object type attribute
                    objectType = element.attrib['ObjectType']
                    if dbg: print "Info: objectType=",objectType
                    addObject = True
                    if objectType == 'Arrow':                                       # if we have an edge
                        Edge(element,self)                                                # make an edge    
                    else:
                        if objectType == "Grammar":                                 # else if we have a grammar
                            Grammar(element.attrib,self)                                  # make one
                        else:                                                       # else for all the other state types
                            if objectType == 'PromptState':                             # if we have a prompt state
                                newState = PromptState(element.attrib,self)                   # make a new prompt state object
                            elif objectType == 'GrammarState':                          # if we have a grammar state
                                newState = GrammarState(element.attrib,self)
                                self.grammarStateIDs.append(newState.id)
                            elif objectType == 'StartState':                            # if we have a start state
                                newState = StartState(element.attrib,self)                           
                            elif objectType == 'StopState':                             # if we have a stop state
                                newState = StopState(element.attrib,self)                            
                            elif objectType == 'DecisionState':                         # if we have a decision state
                                newState = DecisionState(element.attrib,self)                        
                            elif objectType == 'ComputationalState':                    # if we have a computational state
                                newState = ComputationalState(element.attrib,self)
                            elif objectType == 'SubDialog':
                                newState = SubDialogState(element.attrib,self)
                            else:
                                print "Warning, unknown object type",objectType
                                addObject = False
                            if addObject:
                                self.objectName2Index[newState.ObjectName] = newState.id    # translates object names to IDs
                                self.objects[newState.id] = newState                        # add the new state to the state machine
        if dbg: print "<-- objectHandler"
    def makeGraph(self):                                                # makes the graph
    # go through the edges and find their source and target objects - get rid of the edges and transfer the parent-children relationships to the node objects
    # themselves.  This piece of the code just reads through the edges from the GUI to see the source-target relationships
        dbg = False
        warningMsg1 = "Warning: multiple edges for object:"
        for edge in self.edges.values():                                              # for each edge
            if dbg:
                print "edge is",edge
            if edge.source:                                                             # if it has a source object
                if edge.target:                                                             # if it has a target object
                    try:
                        self.objects[edge.source].children.append(edge.id)                            # assign edge id to parent state's children list
                    except KeyError:
                        print "Error: makeGraph 1: no source object with id",edge.source
                        print "Hint: load the xml file into chrome and look for an object with that ID.  it is probably not linked correctly"
                    try:    
                        self.objects[edge.target].parents.append(edge.id)
                    except KeyError:
                        print "Error: makeGraph 2: no target object with id",edge.target
                        print "Hint: load the xml file into chrome and look for an object with that ID.  it is probably not linked correctly"
                else:
                    print "Warning:No target for edge",edge
            else:
                print "Warning: No source for edge",edge
        for obj in self.objects.values():                                             # for each object
            if dbg:
                print "in makegraph lookin at:",obj,obj.__dict__
            if obj.children:                                                            # if it has children
                for edgeID in obj.children:                                                 # for each of the outgoing edges in its children list
                    thisEdge = self.edges[edgeID]
                    if thisEdge.label:                                                          # if the edge is labelled (has a semantic value)
                        if obj.nextStates.has_key(thisEdge.label):                                  # if it has a duplicate key print a warning
                            print warningMsg1,obj.__class__.__name__,"with same label",thisEdge.label,"in module",obj.module
                            obj.nextStates[thisEdge.label].append(self.objects[thisEdge.target].id)
                        else:
                            obj.nextStates[thisEdge.label] = [self.objects[thisEdge.target].id]     # make the next state the goto state indexed by label
                    else:                                                                       # else the edge has no label
                        if obj.nextStates.has_key('default'):                                       # if there is already an edge with the default label, print a warning                         
                            print warningMsg1,obj.__class__.__name__,"in module",obj.module
                            obj.nextStates['default'] = obj.nextStates['default'] + self.objects[thisEdge.target].id
                           
                        else:
                            try:
                                obj.nextStates['default'] = [self.objects[thisEdge.target].id]            # else use the label 'default'
                            except KeyError:
                                print "Error: makeGraph 3: no target object with id",edge.target
                                print "Hint: load the xml file into chrome and look for an object with that ID.  it is probably not linked correctly"
        self.reconcileGrammarStateReferencesToGrammars()
                                
        # go through the grammar states and make sure that every grammar referred to by a grammar state exists
        # and check that the semantic labels on the outgoing arcs of the grammar exist in a referred-to grammar
    def reconcileGrammarStateReferencesToGrammars(self):                # ensures that grammars referred to actually exist
        dbg = False
        semanticMeanings = []
        if dbg: print "Info: Reconciling grammar references with grammars..."
        for grammarStateID in self.grammarStateIDs:                                             # for each grammar state
            grammarState = self.objects[grammarStateID]
            for grammarName in grammarState.grammarNames:                                           # for each of the grammar names referred to in the state
                if not self.grammars.has_key(grammarName):                                              # if  we can't find a grammar with that name 
                    print "Warning: grammar referred to in state",grammarState.dump(),"does not exist"      # print a warning
                    sm.reconcilationOK = False
                else:
                    semanticMeanings = self.grammars[grammarName].semanticMeanings + semanticMeanings
            if dbg: print "Info: all semanticMeanings for this state=",semanticMeanings
            for key in grammarState.nextStates:                                                     # for each of the labelled arcs coming out of the state
                if dbg:print "Info: key=",key
                if key.lower() not in semanticMeanings:                                                 # if the semantic tag does not exist in any of the referred to grammars
                    print "Warning: the labelled arc",key,"in grammar grammar state",grammarState.id,"is not in a grammar"
                    self.reconcilationOK = False                                                            # print a warning
        for grammarStateID in self.grammarStateIDs:                                             # for each grammar state
            grammarState = self.objects[grammarStateID]
            for grammarName in grammarState.grammarNames:                                           # for each of the grammar names referred to in the state
                grammarState.grammars[grammarName] = self.grammars[grammarName]                         # assign the grammar (not just the name) to the state
        if self.reconcilationOK:
            if dbg: print "Info: No issues reconciling grammars."

    def run(self,stateName=None,simulation=False,simDict=None):         # runs the state machine
        dbg = True
        notDone = True
        if dbg:
            print "\nInfo: sm.run: starting.  stateName=",stateName,"simulation=",simulation,"simDict=",simDict
        if not stateName:
            return
        try:
            stateID = self.objectName2Index[stateName]
            currentState = self.objects[self.objectName2Index[stateName]]
        except KeyError:
            if dbg: print "Error: In stateMachine.run() 1: Cannot find currentState named",stateName
            return
        promptsToPlay = []
        stateCtr = 0
        while notDone:
            # get the type of the current state
            stateType = currentState.__class__.__name__
            if dbg:
                print stateCtr,"------------------------------"
                print "  Info: In stateMachine.run() 2: stateType =",stateType, "; ObjectName=",currentState.ObjectName,"; id=",currentState.id
            # run the state to collect any prompts we need to display and set any variables that need to be set
            # this should run through all state
            stateCtr = stateCtr + 1
            if stateCtr > 1000:                                                                                    # this catches infinite loops
                exit()
            if stateType == 'GrammarState':                                                                         # if a grammar state
                runResult = currentState.run(self)
                outputText = ''
                if dbg: print "  Info: In stateMachine.run() 3: runResult=",runResult.dump(),"outputtext=",outputText,"promptsToPlay=",promptsToPlay
                for prompt in promptsToPlay:                                                                            # get prompts from previous states
                    outputText = outputText + ' ' + self.prompts[prompt].text
                for aPrompt in runResult.prompts:                                                                       # get prompts from current state
                    if dbg: print "  Info: In stateMachine.run() 3.5: aPrompt (promptName) =",aPrompt
                    outputText = outputText + ' ' + self.prompts[aPrompt].text
                if dbg: print "  Info: In stateMachine.run() 3.6: outputText =",outputText
                if not simulation:
                    userInput = raw_input(outputText)                                                                   # display prompts and get the user's input
                else:
                    print "System:",outputText
                    userInput = simDict[currentState.id]
                    print "User:",userInput
                if dbg: print "  Info: In stateMachine.run() 3.7: userInput =",userInput
                meanings = currentState.parseInput(userInput)                                                           # parse the users input
                if dbg: print "  Info: In stateMachine.run() 3.8: meanings =", meanings
                possibleNextStates = []
                for meaning in meanings:                                                                                # find the list of possible next states
                    if currentState.nextStates.has_key(meaning):
                        possibleNextStates = possibleNextStates + currentState.nextStates[meaning]
                if dbg: print "  Info: In stateMachine.run() 3.9: possibleNextStates=", possibleNextStates
                if len(possibleNextStates) > 0:                                                                        # if we got a meaning                                                                     
                    nextStateID = possibleNextStates[0]
                    if dbg: print "  Info: In stateMachine.run() 3.10: nextStateID=", nextStateID
                    try:
                        currentState = self.objects[nextStateID]                                                            # get the next state to go to
                    except KeyError:
                        if dbg: print "Error: In stateMachine.run() 3.11: Cannot find nextStateID:",nextStateID
                        return
                else:
                    if len(possibleNextStates) == 0:                                                                    # else if there was no meaning
                        if dbg: print "  Info: In stateMachine.run() 3.12: No match"
            else:
                if stateType == 'SubDialogState':                                                                   # if its a sub dialog state
                    runResult = currentState.run(self)                                                                  # run the sub dialog to get the name of the next start state
                    if dbg: print "  Info: In stateMachine.run() 4: runResmsult=",runResult.dump()
                    try:                                        # push the id of the subdialog state on a stack
                        self.subDialogStack.append(currentState.id)
                        if dbg: print "  Info: In stateMachine.run() 4.01: pushing id on stack",currentState.id
                    except KeyError:
                        print "  Error: In stateMachine.run() 4.1: currentState.id=",currentState.id
                    try:
                        nextStateID = runResult.nextState[0]
                        currentState = self.objects[nextStateID]                                                        # get the next state to go to
                    except KeyError:
                        if dbg: print "Error: In stateMachine.run() 4.2: Cannot find nextStateID:",nextStateID
                        return
                    if dbg: print "  Info: In stateMachine.run() 4.3: nextStateID=",nextStateID,"; name=",currentState.ObjectName
                else:
                    if stateType == 'StopState':                                                                    # if we have a stop state
                        if currentState.label == 'Return':                                                              # if it is a return state
                            lastSubDialogStateID = self.subDialogStack.pop()                                                # pop the last subDialog State ID from stack
                            if dbg: print "  Info: In stateMachine.run() 5.1: lastSubDialogStateID=",lastSubDialogStateID
                            lastSubDialogState = self.objects[lastSubDialogStateID]                                         # get the state object
                            nextStateID = lastSubDialogState.resumeRun(self)                                                  # find out where the next state is to resume
                            if dbg: print "  Info: In stateMachine.run() 5.2: nextStateID=",nextStateID
                            currentState = self.objects[nextStateID]                                                       # make that the current state
                        else:
                            notDone = False                                                                             # else we are done
                            outputText = ''
                            for aPrompt in promptsToPlay:                                                               # get prompts
                                outputText = outputText + ' ' + self.prompts[aPrompt].text
                            if not simulation:
                                inputText = raw_input(outputText)
                            else:
                                print "System:",outputText                                                              # flush the buffer
                    else:
                        # for all other states
                        runResult = currentState.run(self)                                   
                        if dbg: print "  Info: In stateMachine.run() 6: runResult=",runResult.dump()
                        # get the prompts (if any) and append to the set to output
                        if len(runResult.prompts) > 0:
                            promptsToPlay.append(runResult.prompts[0])
                        try:
                            nextStateID = runResult.nextState[0]
                            currentState = self.objects[nextStateID]
                        except KeyError:
                            if dbg: print "Error: In stateMachine.run() 6.1: Cannot find nextStateID:",nextStateID
                            return
                        if dbg: print "  Info: In stateMachine.run() 6.2: nextStateID=",nextStateID,"; name=",currentState.ObjectName
                        if dbg: print "  Info: In stateMachine.run() 6.3: promptsToPlay=",promptsToPlay
        if dbg: print "Info: sm.run: stopping"

class NewStateMachine():
    def __init__(self,inputFileName):
        dbg = False
        if dbg: print "Initializing "
        self.stateMachine = StateMachine()
        self.stateMachine.readDrawIOXMLFile(inputFileName)
        self.stateMachine.makeGraph()
        if dbg: print "Finished Initializing"

def runSimulations(inputFileName,startStateName):
    dbg = True
    mySimulation = NewStateMachine(inputFileName)
    states2inputs = {}
    for aGrammarStateID in mySimulation.stateMachine.grammarStateIDs:       # for each grammar state in the machine
        aGrammarState = mySimulation.stateMachine.objects[aGrammarStateID]
        possibleInputsList = aGrammarState.getPossibleInputs()                 # get the list of dictionaries of possible inputs mapped to semantic meanings (may be more than one grammar per state)
        allText = []
        for aGrammarInputDict in possibleInputsList:                            # for each of the input dicts
            inputText = aGrammarInputDict.keys()                                    # get the text 
            allText = allText + inputText                                           # add it into the whole
        states2inputs[aGrammarStateID] = allText                                # so foo = {'25':['sure', 'ok', 'no', 'yup', ... 'start over', 'stop', ' go back to the beginning', ' restart', 'cancel']}
    possibleInputs = list(itertools.product(*states2inputs.values()))
    grammarKeys = states2inputs.keys()
    simNumber = 0
    for aSim in possibleInputs:                                             # for each possible set of inputs
        if dbg: print "** new simulation",simNumber,"-------------------"
        simDict = {}
        ctr = 0
        for aKey in grammarKeys:                                                # create the inputs set for this run - this should be a value for each grammar
            simDict[aKey] = aSim[ctr]
            ctr = ctr + 1
        if dbg: print "simDict=",simDict
        aSimulation = NewStateMachine(inputFileName)                            # create a fresh machine
        simNumber = simNumber + 1
        aSimulation.stateMachine.run(startStateName,True,simDict)               # run it using the set of inputs for this run
    return aSimulation

if __name__ == "__main__":
    dbg = True
    inputFileName = "VTK 2.21.xml"
    startStateName = 'Module2Start'
    nsm = NewStateMachine(inputFileName)
    nsm = nsm.stateMachine.run(startStateName)                                  # run the statemachine live with user input starting at the top of the app
    #lastSimulation = runSimulations(inputFileName,startStateName)               # run through all possible accepted inputs
        


