def testPrompts(sm):
    for index in sm.objects.keys():
        prompts = sm.objects[index].prompts
        print sm.objects[index].ObjectName
        print "prompts=",prompts

def testGrammarStates(sm):
    dbg = True
    grammarStateName = 'HowsIt'
    grammarState = sm.objects[sm.objectName2Index[grammarStateName]]
    runResult = grammarState.run(sm)
    possibleNextStates = []
    if dbg:
        print "Info: in testGrammarState:1 grammarStateName=",grammarStateName
        print "Info: in testGrammarState:2",grammarState.__dict__
        print "Info: in testGrammarState:3 runResult=",runResult.dump()
    text = 'yes'
    meanings = grammarState.parseInput(text)
    if dbg:
        print "Info:in testGrammarState:4 meanings=", meanings
    for meaning in meanings:
        if grammarState.nextStates.has_key(meaning):
            possibleNextStates = possibleNextStates + grammarState.nextStates[meaning]
    if dbg:
        print "Info:in testGrammarState:5 possibleNextStates=", possibleNextStates

    possibleNextStates = []
    text = 'no'
    meanings = grammarState.parseInput(text)
    if dbg:
        print "Info:in testGrammarState:4 meanings=", meanings
    for meaning in meanings:
        if grammarState.nextStates.has_key(meaning):
             possibleNextStates = possibleNextStates + grammarState.nextStates[meaning]
    if dbg:
        print "Info:in testGrammarState:5 possibleNextStates=", possibleNextStates
    possibleInputs = grammarState.getPossibleInputs()
    if dbg:
        print "Info:in testGrammarState:6 possibleInputs=", possibleInputs

    

def testPromptStates(sm):
    dbg = True
    promptStateName = 'Good'
    promptState1 = sm.objects[sm.objectName2Index[promptStateName]]
    runResult = promptState1.run(sm)
    if dbg:
        print "Info: in testPromptStates:1 promptStateName=",promptStateName
        print "Info: in testPromptStates:2",promptState1.dump()
        print "Info: in testPromptStates:3 runResult=",runResult.dump()

def testStartStates(sm):
    dbg = True
    startStateName = 'Module2Start'
    startState1 =  sm.objects[sm.objectName2Index[startStateName]]
    runResult = startState1.run(sm)
    if dbg:
        print "Info: in testStartStates:1 promptStateName=",startStateName
        print "Info: in testStartStates:2",startState1.dump()
        print "Info: in testStartStates:3 runResult=",runResult.dump()

def testDecisionStates(sm):
    dbg = True
    stateName = 'Decision1'
    stateName =  sm.objects[sm.objectName2Index[stateName]]
    runResult = stateName.run(sm)
    if dbg:
        print "Info: in testDecisionStates:1 stateName=",stateName
        print "Info: in testDecisionStates:2",stateName.dump()
        print "Info: in testDecisionStates:3 runResult=",runResult.dump()

def testComputationStates(sm):
    dbg = True
    stateName = 'feel bad'
    stateName =  sm.objects[sm.objectName2Index[stateName]]
    runResult = stateName.run(sm)
    if dbg:
        print "Info: in testComputationStates:1 stateName=",stateName
        print "Info: in testComputationStates:2",stateName.dump()
        print "Info: in testComputationStates:3 runResult=",runResult.dump()

def testSubDialogStates(sm):
    dbg = True
    stateName = 'IIWII1'
    stateID = sm.objectName2Index[stateName]
    subState =  sm.objects[stateID]
    runResult = subState.run(sm)                                                    # run the sub dialog to get the name of the next start state
    if dbg:
        print "Info: in testSubDialogStates:1 stateName=",stateName, "stateID=",stateID
        print "Info: in testSubDialogStates:2",subState.dump()
        print "Info: in testSubDialogStates:3 runResult=",runResult.dump()

    if subState.nextStates.has_key('default'):                                      # if there is an arc coming out of the subdialog state (it is a subdialog not a goto)
        sm.subDialogStack.append(stateID)                                               # push the name of the subdialog state on a stack
    else:                                                                                # ... do other states here within the subdialog module
        sm.subDialogStack.append(stateID)                                                                            
                                                                                    # if/when the main loop encounters a stop state with a return label
    lastSubDialogStateID = sm.subDialogStack.pop()                                  # pop the stack to get the last subdialog state name
    subState =  sm.objects[lastSubDialogStateID]
    nextStateID = subState.resumeRun(sm) 
    if dbg:
        print "Info: in testSubDialogStates:4 lastSubDialogStateID=",lastSubDialogStateID
        print "Info: in testSubDialogStates:5 nextStateID=",nextStateID

def ioTest():
    sendOutput('text','Type something')
    inputText = getUserInput('Live')
    #sendOutput('text',inputText)
    inputText = 'you said: ' + inputText
    print "<",'text',inputText
def sendOutput(typeOfMsg,msg):
    print "<",typeOfMsg,msg

def getUserInput(Mode):
    if Mode == 'Live':
        userInput = raw_input("Chat here:  ")
        userInput = userInput.strip()
        return userInput
    else:
        return None

def program_logic(line):
    global line_count
    line_count += 1
    print str(line_count) + ': ' + line.rstrip()
    return line.rstrip()

def read_from_stdin():
    global line_count
    for line in sys.stdin:
        program_logic(line)

def prompt_user():
    prompt = 'Type "quit" to exit.'
    line = raw_input(prompt)
    if line == 'quit':
        sys.exit()
    inputSoFar = program_logic(line)
    while (True):
        line = raw_input(inputSoFar)
        if line == 'quit':
            sys.exit()
        inputSoFar = program_logic(line)

def runtests(sm):
    #sm.run('Foobar')
    #testPromptStates(sm)
    #testStartStates(sm)
    testGrammarStates(sm)
    #testComputationStates(sm)
    #testDecisionStates(sm)
    #testSubDialogStates(sm)
    #ioTest()
    #testPrompts(sm)
    #sm.run('Foobar')

if __name__ == "__main__":
    dbg = True
    sm = StateMachine()                                                                                                     # create an instance of general state machine
    sm.readDrawIOXMLFile("VTK 2.15.xml")                                                                                    # read in the data from the GUI of a particular design
    if dbg:
        print "Info: read",len(sm.objects),"objects and",len(sm.edges),"edges."
        print 'Info: here are the objects as read from the GUI before making the graph'
        print "\nInfo: states:",sm.jsize(sm.objects)
        print "\nInfo: prompts:",sm.jsize(sm.prompts)
        print "\nInfo: grammars:",sm.jsize(sm.grammars)
        print "\nInfo: edges:",sm.jsize(sm.edges)
    sm.makeGraph()
    if dbg:
        print "\nInfo: Here are the objects after the graph has been made and the grammar state references reconciled"
        for objNum in sm.objects:
            print "Object ID=",objNum,"Object reference=",sm.objects[objNum],"\nObject dict=",sm.objects[objNum].__dict__,"\n"
        runtests(sm)
    