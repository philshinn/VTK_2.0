import string
import sys
from VTKTests import *
import itertools
import re
import json
import os
import xml.etree.ElementTree as etree
import time
import datetime
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom
from slackclient import SlackClient
from VTKSlackInfo import *

class Step():                                                       # A step in Cyara xml format
    def __init__(self):
        self.timeStamp = time.strftime("%c")
        self.name = None
        self.replyText = None
        self.promptText = None

class Log():                                                        # A live interaction traversal from a start state to an end is stored in a log
    def __init__(self):
        i = datetime.datetime.now()
        self.name = ("%s_%s_%s_%s_%s_%s") % (i.year,i.month,i.day,i.hour,i.minute,i.second) + '.log'
        self.steps = []
    def printMe(self):
        dbg = True
        if os.name == 'posix':
            pathmarker = '/' 
        else:
            pathmarker = '\\'
        path = os.getcwd()+ pathmarker
        logDir = path + "logs"
        if not os.path.exists(logDir):
            os.makedirs(logDir)
        fileName = logDir + pathmarker + self.name
        with open(fileName,"w") as outFile:
            for step in self.steps:
                outFile.write(step.timeStamp + "\t")
                if step.replyText:
                    outFile.write("user:%s\n" %step.replyText)
                if step.promptText:
                    outFile.write("system:%s\n" %step.promptText)
        outFile.close()
        dbg = True
        
class TestCase():                                                   # A test case in Cyara xml format
    def __init__(self):
        self.name = None
        self.phoneNumber = None
        self.steps = []
    def dump(self):
        print "name=",self.name
        print "phone number=",self.phoneNumber
        print "Step name\t\t DTMF"
        for step in self.steps:
            if step.replyText:
                print step.promptText,"\t\t",step.replyText
            else:
                print step.promptText

    def prettify(self,elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def cyaraXML(self):
        dbg = False
        root = Element('TestSpecification')
        root.set('xmlns', 'TestSpecification.xsd')
        testCases = SubElement(root,'TestCases')
        testCase = SubElement(testCases,'TestCase')
        testCaseName = SubElement(testCase,'TestCaseName')
        testCaseName.text = self.name
        folderPath = SubElement(testCase,'FolderPath')
        folderPath.text = 'Phil'
        description = SubElement(testCase,'Description')
        phoneNo = SubElement(testCase,'PhoneNo')
        phoneNo.text = self.phoneNumber
        notes = SubElement(testCase,'Notes')
        alertMsg = SubElement(testCase,'AlertMsg')
        preConnectAudio = SubElement(testCase,'PreConnectAudio')
        minorThresholdCriticalCount = SubElement(testCase,'MinorThresholdCriticalCount')
        minorThresholdCriticalCount.text = '3'
        majorThresholdCriticalCount = SubElement(testCase,'MajorThresholdCriticalCount')
        majorThresholdCriticalCount.text = '1'
        dataInputs = SubElement(testCase,'DataInputs')
        steps = SubElement(testCase,'Steps')
        ringingStep = SubElement(steps,'RingingStep')
        minPauseTime = SubElement(ringingStep,'MinPauseTime')
        minPauseTime.text = '0'
        maxPauseTime = SubElement(ringingStep,'MaxPauseTime')
        maxPauseTime.text = '0'
        minorThresholdTime = SubElement(ringingStep,'MinorThresholdTime')
        minorThresholdTime.text = '5'
        majorThresholdTime = SubElement(ringingStep,'MajorThresholdTime')
        majorThresholdTime.text = '10'
        callSteps = SubElement(steps,'CallSteps')
        ctr = 1
        for aStep in self.steps:
            step = SubElement(callSteps,'Step')
            stepNo = SubElement(step,'StepNo')
            stepNo.text = str(ctr)
            stepDescription = SubElement(step,'Description')
            stepDescription.text = aStep.name
            expectedText = SubElement(step,'ExpectedText')
            replyText = SubElement(step,'ReplyText')
            expectedExchangeType = SubElement(step,'ExpectedExchangeType')
            expectedExchangeType.text = 'MPSR'
            replyExchangeType = SubElement(step,'ReplyExchangeType')
            replyExchangeType.text = 'Speech'
            minPauseTime = SubElement(step,'MinPauseTime')
            minPauseTime.text = '0'
            maxPauseTime = SubElement(step,'MaxPauseTime')
            maxPauseTime.text = '0'
            blockPath = SubElement(step,'BlockPath')
            minorThresholdTime = SubElement(step,'MinorThresholdTime')
            majorThresholdTime = SubElement(step,'MajorThresholdTime')
            minConfidenceLevel = SubElement(step,'MinConfidenceLevel')
            postSpeechSilenceTimeout = SubElement(step,'PostSpeechSilenceTimeout')
            # if there is a response, give it, else give the prompt name
            if aStep.replyText != None:
                expectedText.text = ''
                replyText.text = aStep.replyText
                minorThresholdTime.text = '0'
                majorThresholdTime.text = '0'
                minConfidenceLevel.text = '0'
                postSpeechSilenceTimeout.text = '0'
            else:
                expectedText.text = aStep.promptText
                replyText.text = ''
                minorThresholdTime.text = '3'
                majorThresholdTime.text = '5'
                minConfidenceLevel.text = '80'
                postSpeechSilenceTimeout.text = '3'               
            ctr = ctr + 1
        if dbg: print self.prettify(root)
        return self.prettify(root)

    def journeyTXT(self,outputFile):
        dbg = True
        with open(outputFile,"w") as outFile:
            outFile.write("Actor\tText\n")
            for aStep in self.steps:
                if aStep.replyText:
                    outFile.write("User:\t%s\n" %aStep.replyText.strip())
                if aStep.promptText:
                    outFile.write("System:\t%s\n" %aStep.promptText.strip())
        outFile.close()
        
    
    def printMe(self,fileName,outputType):

        if os.name == 'posix':
            pathmarker = '/' 
        else:
            pathmarker = '\\'
        path = os.getcwd()+ pathmarker
        dbg = True
        if outputType == 'cyaraXML':
            simdir = path + "cyaraXML"
            if not os.path.exists(simdir):
                os.makedirs(simdir)
            where = simdir + pathmarker + str(fileName) + ".xml"
            if dbg: print "output directory =",where
            with open(where,"w") as outFile:
                outFile.write("%s" %self.cyaraXML())
            outFile.close()
        else:
            if outputType == 'journeyTXT':
                simdir = path + "journeyTXT"
                if not os.path.exists(simdir):
                    os.makedirs(simdir)
                where = simdir + pathmarker + str(fileName) + ".txt"
                if dbg: print "output directory =",where

                self.journeyTXT(where)

class Simulator():                                                  # Discovers and simulates paths through the statemachine, builds test cases
    def __init__(self,inputFileName,startStateName,**kwargs):
        dbg = True
        if dbg: print "kwargs=",kwargs
        if kwargs.has_key('outputType'):
            self.outputType = kwargs['outputType']
        else:
            self.outputType = 'CyaraXML'
        mySimulation = StateMachine()
        mySimulation.readDrawIOXMLFile(inputFileName)
        mySimulation.makeGraph()
        grammarStateIDs = self.getGrammarStatesInGG(mySimulation,startStateName)
        states2inputs = {}
        possibleInputsList = []
        terseFlag = True
        for aGrammarStateID in grammarStateIDs:                                 # for each grammar state grammar states after the start state
            aGrammarState = mySimulation.objects[aGrammarStateID]
            if aGrammarState.ObjectName != 'Global':
                if terseFlag:                                                       # if we only want to get one semantic meaning, rather than all
                    if aGrammarState.Simulations:
                        possibleInputsList = aGrammarState.Simulations.split(';')
                        states2inputs[aGrammarStateID] = possibleInputsList
                        if dbg: print "in runSimulations 0, possibleInputsList=",possibleInputsList
                    else:
                        print "Error: No simulations in grammar state",aGrammarState.ObjectName
                        #exit()
                else:
                    possibleInputsList = aGrammarState.getPossibleInputs()                 # get the list of dictionaries of possible inputs mapped to semantic meanings (may be more than one grammar per state)
                    allText = []
                    for aGrammarInputDict in possibleInputsList:                            # for each of the input dicts
                        inputText = aGrammarInputDict.keys()                                    # get the text 
                        allText = allText + inputText                                           # add it into the whole
                    states2inputs[aGrammarStateID] = allText                                # so foo = {'25':['sure', 'ok', 'no', 'yup', ... 'start over', 'stop', ' go back to the beginning', ' restart', 'cancel']}
        if dbg:
            print "**in runSimulations 2, possibleInputsList",possibleInputsList
            print "**in runSimulations 3, states2inputs=",states2inputs
        possibleInputs = list(itertools.product(*states2inputs.values()))
        if dbg:
            print "**in runSimulations 4,states2inputs=",states2inputs    
        grammarKeys = states2inputs.keys()
        simNumber = 0
        for aSim in possibleInputs:# for each possible set of inputs
            if dbg: print "** new simulation",simNumber,"-------------------"
            simDict = {}
            ctr = 0
            for aKey in grammarKeys:                                                # create the inputs set for this run - this should be a value for each grammar
                simDict[aKey] = aSim[ctr]
                ctr = ctr + 1
            if dbg: print "simDict=",simDict
            aSimulation = NewStateMachine(inputFileName)                            # create a fresh machine
            simNumber = simNumber + 1
            atestCase = aSimulation.stateMachine.run(startStateName,True,simDict)               # run it using the set of inputs for this run
            if simNumber > 100:
                break
            atestCase.printMe(simNumber,self.outputType)
            
    def walkGraph(self, sm, startStateName):
        ''' walks the graph from a start state to return a list of lists of state names '''
        dbg = False
        if dbg: print "walkGraph: startStateName=",startStateName
        startStateID = sm.objectName2Index[startStateName]
        gg = {}
        ggnames = {}
        self.recurseWalkGraph(sm,startStateID,gg,ggnames)
        if dbg:
            print gg
            print ggnames
        return gg,ggnames

    def recurseWalkGraph(self,sm,startStateID,gg,ggnames):
        dbg = False
        if dbg: print "recurseWalkGraph: startStateID=",startStateID
        nextState = sm.objects[startStateID]
        if dbg: print "recurseWalkGraph: nextState=",nextState.__dict__
        if hasattr(nextState,'nextStates'):
            nextStateList = list(itertools.chain(*nextState.nextStates.values()))
        else:
            nextStateList = nextState.nextState
        if nextState.ObjectType == 'SubDialog':
            subDialogStartName = nextState.SubDialogStartName
            if dbg: print "** subdialog **",subDialogStartName
            subDialogStartID = sm.objectName2Index[subDialogStartName]
            self.recurseWalkGraph(sm,subDialogStartID,gg,ggnames)
        gg[startStateID] = nextStateList
        ggnames[nextState.ObjectName] = []
        if dbg: print "recurseWalkGraph: nextStateList = ",nextStateList
        #while nextStateList:
        for nextStateID in nextStateList:
            #recurseWalkGraph(sm,nextStateID)
            #nextStateID = nextStateList.pop()
            objName = sm.objects[nextStateID].ObjectName
            if objName not in ggnames[nextState.ObjectName]:
                ggnames[nextState.ObjectName].append(objName)
            if nextStateID not in gg.keys():  # don't recurse
                self.recurseWalkGraph(sm,nextStateID,gg,ggnames)

    def getGrammarStatesInGG(self, sm,startStateName):
        dbg = False
        gg,ggnames = self.walkGraph(sm,startStateName)
        grammarStateIDs = []
        nodelist = list(set(gg.keys() + list(itertools.chain(*gg.values()))))
        if dbg: print nodelist
        for nodeID in nodelist:
            if sm.objects[nodeID].ObjectType == 'GrammarState':
                grammarStateIDs.append(nodeID)
        if dbg: print grammarStateIDs
        return grammarStateIDs


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
        try:
            aPrompt = Prompt(dic['No_Match_Prompt_1_Name'])
            aPrompt.text = dic['No_Match_Prompt_1_Text']
            sm.addPrompt(aPrompt)
            aPrompt = Prompt(dic['No_Input_Prompt_1_Name'])
            aPrompt.text = dic['No_Input_Prompt_1_Text']
            sm.addPrompt(aPrompt)
        except KeyError:
            pass
        
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
class StopState(State):                                             # Stopping point of application or sub dialog
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

class InitDB(State):                                                # Initialize a database, create tables, populate with values
    def __init__(self,dic,sm):
        dbg = False
        State.__init__(self,dic,sm)
        if hasattr(self,"DBName"):
            if os.name == 'posix':
                path = os.getcwd() + '/' + self.DBName
            else:
                path = os.getcwd()+'\\' + self.DBName 
            if not os.path.isfile(path):
                print "Error: InitDB.init: cannot find db file at",path
                msg = "Error: InitDB.init: cannot find db file at " + path
                sm.errorMsgs.append(msg)
            else:
                sm.externalDBs.append(self.DBName)
                myStr = 'import '+ self.MakeDBModule
                if dbg: print "  Info: in InitDB 1, myStr=",myStr
                exec('import '+ self.MakeDBModule)
                myStr = self.MakeDBModule + "." + self.MakeDBProcedure  + "('" + self.DBName + "')"
                if dbg: print "  Info: in InitDB 2, myStr=",myStr
                exec(myStr)

class AccessDB(State):                                              # initialize a database, create tables, populate with values
    def __init__(self,dic,sm):
        dbg = False
        State.__init__(self,dic,sm)
        if hasattr(self,"DBName"):
            if os.name == 'posix':
                path = os.getcwd() + '/' + self.DBName
            else:
                path = os.getcwd()+'\\' + self.DBName 
            if not os.path.isfile(path):
                msg = "Error: AccessDB.init: cannot find db file at" + path
                sm.errorMsgs.append(msg)
                #exit()

    def run(self,sm):
        # VTK_doesAccountNumberAndPINMatch(dbName,1111,1111)
        dbg = False
        args = self.Args
        if dbg: print "  Info: in AccessDB.run, args=",args
        importStr = "import "+self.AccessDBModule
        if dbg:  "  Info: in AccessDB.run(): importStr=",importStr
        exec(importStr)
        myStr = self.AccessDBModule + "." + self.AccessDBProcedure + "('" + self.DBName +"'"
        argList = self.Args.split(' ')
        if dbg: print "  Info: in AccessDB.run, argList=",argList
        for arg in argList:
            if dbg: print "  Info: in AccessDB.run, arg=[",arg,"]"
            newVal = arg
            if arg[0] == '$':
                newArg = arg[1:]
                if sm.db.has_key(newArg):
                    newVal = sm.db[newArg]
                    if dbg: print "  Info: in AccessDB.run, newVal=",newVal
            myStr = myStr + ",'" + newVal + "'"
        myStr = "returnValue = " +myStr + ")"
        if dbg: print "  Info: in AccessDB.run(): myStr=",myStr
        exec(myStr)
        if dbg: print "  Info: in AccessDB.run(): returnValue=",returnValue
        sm.db[self.ReturnValue] = returnValue
        runResult = RunResult()
        try:
            runResult.nextState = self.nextStates['default']
        except KeyError:
            if len(self.nextStates) == 1:
                runResult.nextState = self.nextStates.values()[0]
        return runResult

class PythonState(State):                                           # A python state runs arbitrary python code
    def __init__(self,dic,sm):
        State.__init__(self,dic,sm)
        self.prompts = []
        self.objectType = 'PythonState'
        self.addPrompts(dic,sm)
        # find the python code and make sure it exists
        if hasattr(self,"PythonRoutineName"):
 #           path = os.getcwd()+'\\' + self.PythonRoutineName

            if os.name == 'posix':
                path = os.getcwd() + '/' + self.PythonRoutineName
            else:
                path = os.getcwd()+'\\' + self.PythonRoutineName
                
            if not os.path.isfile(path):
                msg = "Error: PythonState.init: cannot find python file at",path
                sm.errorMsgs.append(msg)

    def run(self,sm):
        dbg = False
        if dbg: print "Info: Python.run",self.dump()
        runResult = RunResult()
        runResult.prompts = self.prompts
        try:
            runResult.nextState = self.nextStates['default']
        except KeyError:
            if len(self.nextStates) == 1:
                runResult.nextState = self.nextStates.values()[0]
        myStr = 'import ' + self.PythonRoutineName[:-3]
        exec(myStr)
        if dbg: print "  Info: in PythonState.run(): myStr=",myStr
        myStr =  self.PythonRoutineName[:-3]
        myExecStr = "returnValue = " + myStr + "." + myStr + "()"
        if dbg: print "  Info: in PythonState.run(): myExecStr=",myExecStr
        exec(myExecStr)
        if dbg: print "  Info: in PythonState.run(): returnValue=",returnValue
        myMod = sys.modules[myStr]
        if dbg: print "  Info: in PythonState.run(): myMod=",myMod
        return runResult       
        
class Grammar:                                                      # User's input is parsed by a grammar, returning meaning
    def __init__(self,dic,sm):
        dbg = False
        if dbg: print "Info: initializing grammar"
        for attrKey in dic.keys():
            setattr(self,attrKey,dic[attrKey])
        if hasattr(self,'Type'):
            if self.Type == 'List':
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
            else:
                if self.Type == 'Digits':
                    self.members = ['0','1','2','3','4','5','6','7','8','9']
                else:
                    msg = "***Warning: unknown grammar type",dic
                    sm.errorMsgs.append(msg)


        sm.grammarName2ObjectIndex[self.ObjectName] = self.id                           
        if sm.grammars.has_key(self.ObjectName):                                    # the name is like 'YNQ'
            print "Info: Same grammar name seen twice:",self.ObjectName
        else:
            sm.grammars[self.ObjectName] = self
        if dbg:
            print "self.vars=",vars(self)
            print "Info: done initializing grammar"
    def Parse(self,text):
        if hasattr(self,'Type'):
            if self.Type == 'List':
                try:
                    return self.text2meanings[text]
                except KeyError:
                    pass
                else:
                    return None
            else:
                if self.Type == 'Digits':
                    for char in text.strip():
                        if char not in self.members:
                            return []
                    return '$digits'
    def getPossibleInputs(self):
        if hasattr(self,'Type'):
            if self.Type == 'List':
                return self.text2meanings
            else:
                if self.Type == 'Digits':
                    return {'1234':'1234'}
    def getPossibleInputsTerse(self):
        dbg = False
        if dbg: print "In agrammar.getPossibleInputsTerse 0"
        if hasattr(self,'Type'):
            if self.Type == 'List':
                if dbg: print "In agrammar.getPossibleInputsTerse 1, self.type = List, self.semanticMeanings=",self.semanticMeanings
                meanings = []
                for meaning in self.semanticMeanings:
                    meanings.append({meaning:meaning})
                if dbg: print "In agrammar.getPossibleInputsTerse 2, self.type = List, meanings=",meanings

                return meanings
            else:
                if dbg: print "In agrammar.getPossibleInputsTerse 3, self.type =",self.Type

                meanings = []
                if self.Type == 'Digits':
                    meanings.append({'1234':'1234'})
                    return meanings
        
class GrammarState(State):                                          # A grammar state plays a prompt, collects user input and parses it
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
        self.noInputCtr = 0
        self.noMatchCtr = 0
        self.errorCtr = 0
        self.rawInputs = []                                                 # a list of the input text each time state is queried
        
    def run(self,sm):                                                   # this gets the prompts (if any) of the grammar state and returns them to the main run method
        dbg = False
        if dbg: print "Info: running grammar state",self.__dict__
        runResult = RunResult()                                             # to run a state make a new run result structure
        runResult.prompts = self.getPrompts()                               # put any prompts the state has into it
        return runResult
    def parseInput(self,text,sm):                                          # after the prompts (if any) are rendered, the main state machine run method calls parseInput 
        dbg = False
        meanings = []
        self.rawInputs.append(text)
        for aGrammarName in self.grammarNames:
            aGrammar = self.grammars[aGrammarName]
            if dbg: print "working in runParse with aGrammar",aGrammar.__dict__
            result = aGrammar.Parse(text)
            if dbg: print "in runparse, result=",result,"type(result)=",type(result)
            if result:
                if result not in meanings:
                    meanings.append(result)
                    if result == '$digits':
                        sm.digits = text
                        
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

    def getPossibleInputsTerse(self):                                        # this is used to run simulations - it gathers just one possible input per distinct semantic meaning
        dbg = False
        possibleInputs = []                                                 # this is a list of text to meaning dicts
        for aGrammarName in self.grammarNames:
            aGrammar = self.grammars[aGrammarName]
            #if dbg: print "working in getPossibleInputsTerse with aGrammar",aGrammar.__dict__
            result = aGrammar.getPossibleInputsTerse()
            if dbg: print "in getPossibleInputsTerse, result=",result,"type(result)=",type(result)
            if result:
                for item in result:
                    if item not in possibleInputs:
                        possibleInputs.append(item)
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
            msg = "***Warning: no source for edge",json.dumps(self.__dict__)
            sm.errorMsgs.append(msg)
            self.source = ""
        if props.attrib.has_key('target'):
            self.target = props.attrib['target']
        else:
            msg = "***Warning: no target for edge",json.dumps(self.__dict__)
            sm.errorMsgs.append(msg)
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
        if dbg: print "Info: in DecisionState.run, dir(self)=",dir(self)
        runResult = RunResult()
        try:                                                                # get the variable name to branch on
            variableName = getattr(self,'VariableName')                         # e.g. 'feelings'
            if dbg: print  "Info: in DecisionState.run, variableName=",variableName
            if sm.db.has_key(variableName):                                        # if it has been set in the db by some other state
                varValue = sm.db[variableName]                                         # get the value (e.g. 'bad')
                if dbg: print  "Info: in DecisionState.run, varValue=",varValue    
                if self.nextStates.has_key(varValue):                               # if that is an index in the nextStates dic of the decision object
                    if dbg: print  "Info: in DecisionState.run, self.nextStates[varValue]=",self.nextStates[varValue]    
                    runResult.nextState = self.nextStates[varValue]                    # get the next state number to go to
                else:
                    if dbg: print  "Info: in DecisionState.run, no key varValue in nextStates"
            else:
                if dbg: print  "Info: in DecisionState.run, no key in sm.db for",variableName  
        except AttributeError:
            msg = "in Decisionstate.run, I decision state has no attribute 'VariableName'"
            sm.errorMsgs.append(msg)
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
            val = val.strip()
            if val == '$digits':
                val = sm.digits
                sm.db[attr.strip()] = val
            else:
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
        dbg = False
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
        self.globalErrorCtr = 0                                             # total errors encountered in an execution
        self.externalDBs = []                                               # refers to any external databases
        self.forest = {}                                                    # used for simulations
        self.errorMsgs = []                                                 # keep track of errors
        self.log = None

    def addPrompt(self,newPrompt):                                      # adds a prompt
        if self.prompts.has_key(newPrompt.name):
            oldPrompt = self.prompts[newPrompt.name]
            if not oldPrompt.text == newPrompt.text:
                msg = "Warning: trying to add duplicate prompt names with different text: prompt name=" + oldPrompt.name + "; old prompt text=" + oldPrompt.text + "; new prompt text="+newPrompt.text+": keeping old."
                self.errorMsgs.append(msg)
        else:
            self.prompts[newPrompt.name] = newPrompt
            
    def addGrammar(self,newGrammar):                                    # adds a grammar
        if self.grammars.has_key(newGrammar.name):
            oldGrammar = self.grammars[newGrammar.name]
            if not oldGrammar.is_same_as(newGrammar):
                msg = "101: Warning: duplicate grammar names with different text2 meanings",newPrompt.name,oldPrompt.name,"keeping old"
                self.errorMsgs.append(msg)
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
        dbg =False
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
                            elif objectType == 'PythonState':
                                if dbg: print "should be calling pythonstate init"
                                newState = PythonState(element.attrib,self)
                            elif objectType == 'InitDB':
                                newState = InitDB(element.attrib,self)
                            elif objectType == 'AccessDB':
                                newState = AccessDB(element.attrib,self)
                            else:
                                msg = "102: Warning: unknown object type in input xml file:",objectType
                                self.errorMsgs.append(msg)
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
                        msg = "Error: makeGraph 1: no source object with id",edge.source
                        self.errorMsgs.append(msg)
                        msg =  "Hint: load the xml file into chrome and look for an object with that ID.  it is probably not linked correctly"
                        self.errorMsgs.append(msg)
                    try:    
                        self.objects[edge.target].parents.append(edge.id)
                    except KeyError:
                        msg = "Error: makeGraph 2: no target object with id",edge.target
                        self.errorMsgs.append(msg)
                        msg =  "Hint: load the xml file into chrome and look for an object with that ID.  it is probably not linked correctly"
                        self.errorMsgs.append(msg)
                else:
                    msg = "Warning:No target for edge",edge
                    self.errorMsgs.append(msg)
            else:
                msg = "Warning: No source for edge",edge
                self.errorMsgs.append(msg)
        for obj in self.objects.values():                                             # for each object
            if dbg:
                print "in makegraph lookin at:",obj,obj.__dict__
            if obj.children:                                                            # if it has children
                for edgeID in obj.children:                                                 # for each of the outgoing edges in its children list
                    thisEdge = self.edges[edgeID]
                    if thisEdge.label:                                                          # if the edge is labelled (has a semantic value)
                        if obj.nextStates.has_key(thisEdge.label):                                  # if it has a duplicate key print a warning
                            msg = warningMsg1,obj.__class__.__name__,"with same label",thisEdge.label,"in module",obj.module
                            self.errorMsgs.append(msg)
                            obj.nextStates[thisEdge.label].append(self.objects[thisEdge.target].id)
                        else:
                            obj.nextStates[thisEdge.label] = [self.objects[thisEdge.target].id]     # make the next state the goto state indexed by label
                    else:                                                                       # else the edge has no label
                        if obj.nextStates.has_key('default'):                                       # if there is already an edge with the default label, print a warning                         
                            msg = warningMsg1,obj.__class__.__name__,"in module",obj.module
                            self.errorMsgs.append(msg)
                            obj.nextStates['default'] = obj.nextStates['default'] + self.objects[thisEdge.target].id
                           
                        else:
                            try:
                                obj.nextStates['default'] = [self.objects[thisEdge.target].id]            # else use the label 'default'
                            except KeyError:
                                msg = "Error: makeGraph 3: no target object with id",edge.target
                                self.errorMsgs.append(msg)
                                msg =  "Hint: load the xml file into chrome and look for an object with that ID.  it is probably not linked correctly"
                                self.errorMsgs.append(msg)

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
                    msg = "Warning: grammar referred to in state",grammarState.dump(),"does not exist"      # print a warning
                    self.errorMsgs.append(msg)
                    sm.reconcilationOK = False
                else:
                    thisGrammar = self.grammars[grammarName]
                    if hasattr(thisGrammar,'Type'):
                        if thisGrammar.Type == 'List':
                            semanticMeanings = self.grammars[grammarName].semanticMeanings + semanticMeanings
            if dbg: print "Info: all semanticMeanings for this state=",semanticMeanings
            for key in grammarState.nextStates:                                                     # for each of the labelled arcs coming out of the state
                if key != '$digits':
                    if dbg:print "Info: key=",key
                    if key.lower() not in semanticMeanings:                                                 # if the semantic tag does not exist in any of the referred to grammars
                        msg = "Warning: the labelled arc",key,"in grammar state",grammarState.id,"is not in a grammar"
                        self.errorMsgs.append(msg)
                        self.reconcilationOK = False                                                            # print a warning
        for grammarStateID in self.grammarStateIDs:                                             # for each grammar state
            grammarState = self.objects[grammarStateID]
            for grammarName in grammarState.grammarNames:                                           # for each of the grammar names referred to in the state
                grammarState.grammars[grammarName] = self.grammars[grammarName]                         # assign the grammar (not just the name) to the state
        if self.reconcilationOK:
            if dbg: print "Info: No issues reconciling grammars."

    def run(self,stateName=None,simulation=False,simDict=None,ioChannel=None):         # runs the state machine
        dbg = False
        slk_dbg = False
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
        self.log = Log()                                                                                            # log the interaction
        globalObject = self.objects[self.objectName2Index['Global']]
        if dbg: print "  Info: In stateMachine.run() 1.5: globalObject.max_Loops=",globalObject.Max_Loops
        maxLoops = int(globalObject.Max_Loops)
        maxStates = int(globalObject.Max_States)
        stateCtr = 0
        
        if simulation:
            if dbg: print "  Info: In stateMachine.run() 1.5.1: Building test case"
            testCase = TestCase()
        else:           # set up the slack client
            if ioChannel == "slack":
                slack_client = SlackClient(BOT_TOKEN)

        while notDone:
            # get the type of the current state
            stateType = currentState.__class__.__name__
            if dbg:
                print stateCtr,"------------------------------"
                print "  Info: In stateMachine.run() 2: stateType =",stateType, "; ObjectName=",currentState.ObjectName,"; id=",currentState.id
            # run the state to collect any prompts we need to display and set any variables that need to be set
            # this should run through all state
            stateCtr = stateCtr + 1
            if dbg: print "  Info: In stateMachine.run() 2.5: stateCtr=",stateCtr,"; maxLoops=",maxLoops
            #if stateCtr > maxStates:
            if stateCtr > 100:
                msg = "  Info: In stateMachine.run(): Terminating due to Max_States limit of",maxStates,".  To run more, increase Global Behavior Max_States value."
                self.errorMsgs.append(msg)
                break
            if stateType == 'GrammarState':                                                                         # if a grammar state
                runResult = currentState.run(self)
                outputText = ''
                if dbg: print "  Info: In stateMachine.run() 3: runResult=",runResult.dump(),"outputtext=",outputText,"promptsToPlay=",promptsToPlay
                outputText = self.flushBuffer(promptsToPlay,runResult)                                                  # get all the output from prior states and current
                promptsToPlay = []
                #    outputText = outputText + ' ' + newValue
                if dbg: print "  Info: In stateMachine.run() 3.6: outputText =",outputText
                if not simulation:  # live input comes from either the console or from slack
                    thisStep = Step()
                    thisStep.promptText = outputText
                    self.log.steps.append(thisStep)
                    if ioChannel == "slack":
                        if slk_dbg: print "ioChannel=",ioChannel
                        if slack_client.rtm_connect():
                            READ_WEBSOCKET_DELAY = 1
                            slack_client.api_call("chat.postMessage", channel=channel,text=outputText, as_user=True)            # output to the slack channel
                            ctr = 0
                            userInput = ""
                            while ctr < 10:
                                output_list = slack_client.rtm_read()                                                           # get the user's input from slack
                                if slk_dbg: print ctr,"output_list=",output_list
                                if output_list and len(output_list) > 0:
                                    if slk_dbg: print "analysing some user input"
                                    for output in output_list:
                                        if slk_dbg: "output item=",output
                                        if output and 'text' in output and AT_BOT in output['text']:
                                            userInput = userInput + output['text'].split(AT_BOT)[1].strip().lower()
                                            if slk_dbg: print "userInput=",userInput
                                            break
                                if slk_dbg: print "userInput=",userInput
                                time.sleep(READ_WEBSOCKET_DELAY)
                                ctr = ctr + 1
                                if len(userInput) > 0:
                                    break
                        else:
                            if slk_dbg: "slack_client_conect failed in statemachine.run, running from console"
                            print outputText
                            userInput = raw_input()

                    else:
                        print outputText                                                                                        # print the output prompts to user to console
                        userInput = raw_input()                                                                                 # get the user's response
                    thisStep = Step()
                    thisStep.replyText = userInput
                    self.log.steps.append(thisStep)
                else:  # this is a simulation, so get intput from simDict
                    if dbg: print "  Info: System:",outputText
                    step = Step()
                    step.promptText = outputText
                    if dbg: print "  Info: step.promptText",step.promptText
                    testCase.steps.append(step)
                    userInput = simDict[currentState.id]
                    if dbg: print "  Info: User:",userInput
                    step = Step()
                    step.replyText = userInput
                    if dbg: print "  Info: step.replyText =",step.replyText
                    testCase.steps.append(step)
                if dbg: print "  Info: In stateMachine.run() 3.7: userInput =",userInput
                meanings = currentState.parseInput(userInput,self)                                                           # parse the users input
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
                        msg = "Error: In stateMachine.run() 3.11: Cannot find nextStateID:",nextStateID
                        self.errorMsgs.append(msg)
                        return
                else:
                    if len(possibleNextStates) == 0:                                                                    # else if there was no next state to go to
                        if len(meanings) > 0:                                                                               # if there was a meaning
                            if meanings[0] == 'start over':                                                                     # check for globals
                                if hasattr(currentState,'Start_Over_Goto_State'):
                                    gotoStateName = currentState.Start_Over_Goto_State
                                else:
                                    gotoStateName = globalObject.Start_Over_Goto_State
                                gotoStateIndex = self.objectName2Index[gotoStateName]
                                currentState = self.objects[gotoStateIndex]
                            if meanings[0] == 'stop':
                                if hasattr(currentState,'Quit_Goto_State'):
                                    gotoStateName = currentState.Quit_Goto_State
                                else:
                                    gotoStateName = globalObject.Quit_Goto_State
                                gotoStateIndex = self.objectName2Index[gotoStateName]
                                currentState = self.objects[gotoStateIndex]                              
                        else:                                                                                               # else we got no meanings      
                            if dbg: print "  Info: In stateMachine.run() 3.12: No match"
                            currentState.noMatchCtr = currentState.noMatchCtr + 1                                               # increment state-specific no match counter
                            self.globalErrorCtr = self.globalErrorCtr + 1                                                       # increment global error counter
                            if dbg: print "  Info: In stateMachine.run() 3.13: self.globalErrorCtr=",self.globalErrorCtr,"currentState.noMatchCtr=",currentState.noMatchCtr
     
                            if dbg: print "  Info: In stateMachine.run() 3.14: globalObject.Max_Global_Errors=",globalObject.Max_Global_Errors
                            if self.globalErrorCtr > int(globalObject.Max_Global_Errors):                                       # if we have too many total errors so far
                                giveupGotoStateName = globalObject.Giveup_Goto_State
                                giveupGotoStateIndex = self.objectName2Index[giveupGotoStateName]
                                currentState = self.objects[giveupGotoStateIndex]                                                   # quit
                                if dbg: print "  Info: In stateMachine.run() 3.15: giveupGotoStateName=",giveupGotoStateName
                            else:
                                if hasattr(currentState,'Max_State_Errors'):                                                    # if the grammar state has a maximum number of errors
                                    maxStateErrors = int(currentState.Max_State_Errors)                                           # get the value
                                else:
                                    maxStateErrors = int(globalObject.Max_State_Errors)                                         # else get the global
                                if dbg: print "  Info: In stateMachine.run() 3.16: maxStateErrors=",maxStateErrors
                                if currentState.noMatchCtr > maxStateErrors:                                                    # if there were too many errors for this state
                                    giveupGotoStateName = globalObject.Giveup_Goto_State
                                    giveupGotoStateIndex = self.objectName2Index[giveupGotoStateName]
                                    currentState = self.objects[giveupGotoStateIndex]                                               # quit                         
                                    if dbg: print "  Info: In stateMachine.run() 3.17: giveupGotoStateName=",giveupGotoStateName
                            if hasattr(currentState,'No_Match_Prompt_1_Name'):                                                  # if the grammar state has no match prompt
                                noMatchPrompt = currentState.No_Match_Prompt_1_Name
                            else:
                                noMatchPrompt = globalObject.No_Match_Prompt_1_Name
                            promptsToPlay = [noMatchPrompt]

            else:
                if stateType == 'SubDialogState':                                                                   # if its a sub dialog state
                    runResult = currentState.run(self)                                                                  # run the sub dialog to get the name of the next start state
                    if dbg: print "  Info: In stateMachine.run() 4: runResmsult=",runResult.dump()
                    try:                                        # push the id of the subdialog state on a stack
                        self.subDialogStack.append(currentState.id)
                        if dbg: print "  Info: In stateMachine.run() 4.01: pushing id on stack",currentState.id
                    except KeyError:
                        msg = "  Error: In stateMachine.run() 4.1: currentState.id=",currentState.id
                        self.errorMsgs.append(msg)
                    try:
                        nextStateID = runResult.nextState[0]
                        currentState = self.objects[nextStateID]                                                        # get the next state to go to
                    except KeyError:
                        msg = "Error: In stateMachine.run() 4.2: Cannot find nextStateID:",nextStateID
                        self.errorMsgs.append(msg)
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
                            outputText = self.flushBuffer(promptsToPlay,RunResult())                                          # get all the output from prior states and current
                            if dbg: print "  Info: In stateMachine.run() 3.5: outputText =",outputText
                            if not simulation:
                                if ioChannel == "slack":                                                                        # if we are using slack as output
                                    slack_client.api_call("chat.postMessage", channel=channel,text=outputText, as_user=True)        # write the output to slack
                                else:
                                    print outputText                                                                            # else print the final output to the console
                                

                                thisStep = Step()
                                thisStep.promptText = outputText
                                self.log.steps.append(thisStep)                              
                                self.log.printMe()
                    
                            else:
                                if dbg: print " Info: System:",outputText                                                              # flush the buffer
                                if len(outputText.strip()) > 0:
                                    step = Step()
                                    step.promptText = outputText
                                    if dbg: print " Info: step.promptText = ",step.promptText 
                                    testCase.steps.append(step)
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
                            msg = "Error: In stateMachine.run() 6.1: Cannot find nextStateID:",nextStateID
                            self.errorMsgs.append(msg)
                            return
                        if dbg: print "  Info: In stateMachine.run() 6.2: nextStateID=",nextStateID,"; name=",currentState.ObjectName
                        if dbg: print "  Info: In stateMachine.run() 6.3: promptsToPlay=",promptsToPlay
        if dbg: print "Info: sm.run: stopping"
        if simulation:
            return testCase
        else:
            return None
        
    def flushBuffer(self,promptsToPlay,runResult):
        dbg = False
        outputText = ''
        for prompt in promptsToPlay:                                                                            # get prompts from previous states
            if prompt[0] == '$':                                                                                    # if the prompt is dynamic (e.g., $dynamic1)
                newValue = self.db[self.prompts[prompt].text]                                                           # get the db key (e.g. acctNum) and get its value (e.g. 1234)                                                  
            else:
                newValue = self.prompts[prompt].text
            outputText = outputText + ' ' + newValue
            if dbg: print  "  Info: In stateMachine.flushBuffer() 1: outputText=",outputText
        promptsToPlay = []
        for aPrompt in runResult.prompts:                                                                       # get prompts from current state
            if aPrompt[0] == '$':                                                                                    # if the prompt is dynamic (e.g., $dynamic1)
                newValue = self.db[self.prompts[aPrompt].text]                                                           # get the db key (e.g. acctNum) and get its value (e.g. 1234)                                                  
            else:
                newValue = self.prompts[aPrompt].text
            outputText = outputText + ' ' + newValue
        if dbg: print  "  Info: In stateMachine.flushBuffer() 2: outputText=",outputText
        return outputText

class NewStateMachine():
    def __init__(self,inputFileName):
        dbg = False
        if dbg: print "Initializing "
        self.stateMachine = StateMachine()
        self.stateMachine.readDrawIOXMLFile(inputFileName)
        self.stateMachine.makeGraph()
        if dbg: print "Finished Initializing"

if __name__ == "__main__":
    dbg = False
    inputFileName = "VTK 2.34.xml"
    startStateName = 'Module2Start'
    nsm = NewStateMachine(inputFileName)
    nsm.stateMachine.run(startStateName,ioChannel="slack")                              # run the statemachine live with user input from slack
    #nsm.stateMachine.run(startStateName)                                                # run the statemachine live with user input from console
    #mySimulator = Simulator(inputFileName,startStateName,outputType='cyaraXML')        # run a simulation using simulated inputs 
    #mySimulator = Simulator(inputFileName,startStateName)                              # run a simulation using simulated inputs 
    #mySimulator = Simulator(inputFileName,startStateName,outputType='journeyTXT')      # run a simulation using simulated inputs 

