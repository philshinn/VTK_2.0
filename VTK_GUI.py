from Tkinter import *
from VTK_Code import *
from tkFileDialog import *
from tkMessageBox import showerror, showinfo
#import xlwt
#import xlrd
from exceptions import *
from time import time
import os
import sys
import time
from ScrolledText import *

import thread

LOAD_XML_BUTTON='Browse'
INPUT_FILE_LABEL= 'Input DrawIO XML File: '
OUTPUT_FILE_LABEL='Output Prompt File:'
START_STATE_LABEL="Start State:"
APPLICATION_TITLE='Vuid Toolkit'
OUTPUT_FILE_BUTTON = 'Browse'
GENERATE_BUTTON='Export Prompts'
INTERACT_BUTTON='Live Interaction'
SIMULATE_BUTTON='Cyara Test Scripts'
JOURNEY_BUTTON='User Journeys'

LEFT_HEADER = "&F"
CENTER_HEADER = "&A"
RIGHT_HEADER = "&D &T"
LEFT_FOOTER= '\xA9 Your Name Here. All rights reserved.'
CENTER_FOOTER = ""
RIGHT_FOOTER = "Page &P of &N"
BUTTON_LOAD_SCRIPTFILE="Load a script file..."
TEXT_MATCH_CASE = 'Match Case?'
TEXT_DESC_FONT = 'Set font to 8 for Content cell?'
FONT_SIZE=8
COLUMN_WIDTH_TEXT = 70
COLUMN_WIDTH_PAGE = 10
COLUMN_WIDTH_SPEAKER = 10
COLUMN_WIDTH_CONTENTS_SCRIPT_NUM=10
LEFT_MARGIN=0.5
RIGHT_MARGIN=0.5
CELL_FONT_BOLD = "Bold"
CELL_COLOR_GRAY = 15
TITLE_ROW = 2
CALLER_ROW_TEXT = 'Caller'
        
class VTK_GUI_Generator(object):
    def __init__(self, master=None):
        'Creates the GUI'
        # Set up the main frame
        self.workingDir = os.getcwd()
        self.main_frame = Frame(master)
        master.minsize(width=600,height=400)
        self.main_frame.grid()
        if master:
            master.title(APPLICATION_TITLE)
        else:
            self.main_frame.title(APPLICATION_TITLE)
        self.startStateMenu = None
        self.startState = "Start State"
        self.stateNames = None
        self.stateMachine = None
        # Set up the xml file entry field
        xmlFileRow = Frame(self.main_frame)
        xmlFileRow.grid(column=0,row=0)
        xmlFileLabel = Label(xmlFileRow, text=INPUT_FILE_LABEL,width=20)
        xmlFileLabel.grid(row=0,column=1,sticky='W')
        self.xmlFileText = Entry(xmlFileRow,width=40)
        self.xmlFileText.grid(row=0,column=3)
        self.xmlFileSelector = Button(xmlFileRow, text=LOAD_XML_BUTTON, command=self.onXMLFileSelect)
        self.xmlFileSelector.grid(row=0,column=5)
        # Set up output file text entry field
        outputFileRow = Frame(self.main_frame)
        outputFileRow.grid(row=1,column=0)
        outputFileLabel = Label(outputFileRow,text=OUTPUT_FILE_LABEL,width=20)
        outputFileLabel.grid(row=1,column=0,sticky='W')
        self.outputFileText = Entry(outputFileRow,width=40)
        self.outputFileText.grid(row=1,column=3)
        self.outputFileSelector = Button(outputFileRow, text=LOAD_XML_BUTTON, command=self.onOutputFileSelect)
        self.outputFileSelector.grid(row=1,column=5,sticky='E')
        # blank line
        self.blankRow = Frame(self.main_frame)
        self.blankRow.grid(column=0,row=3)
        self.blankLabel = Label(self.blankRow, text = '   ')
        self.blankLabel.grid(column=0,row=3)
        # Set up the listbox to communicate messages to user
        boxRow = Frame(self.main_frame)
        boxRow.grid(column=0,row=4)
        scrollbar = Scrollbar(boxRow, orient=VERTICAL)
        self.listbox = Listbox(boxRow, selectmode=EXTENDED, yscrollcommand=scrollbar.set,width=80,height=20)
        self.listbox.grid(column=0,row=4,columnspan=4) 
        scrollbar.config(command=self.listbox.yview)
        scrollbar.grid(column=4,row=4,sticky='ns')
        # blank line
        self.blankRow2 = Frame(self.main_frame)
        self.blankRow2.grid(column=0,row=5)
        self.blankLabel2 = Label(self.blankRow2, text = '   ')
        self.blankLabel2.grid(column=0,row=5)
        # Set up the generater button row
        sixthRow = Frame(self.main_frame)
        B1 = Button(sixthRow, text=GENERATE_BUTTON, command=self.onGenerate)
        B2 = Button(sixthRow, text=INTERACT_BUTTON, command=self.onInteract)
        B3 = Button(sixthRow, text=SIMULATE_BUTTON, command=self.onSimulate)
        B4 = Button(sixthRow, text=JOURNEY_BUTTON, command=self.onJourney)
        sixthRow.grid(column=0,row=6)
        B1.grid(column=0,row=6)
        B2.grid(column=1,row=6)
        B3.grid(column=2,row=6)
        B4.grid(column=3,row=6)
        # set up the start state collector
        self.seventhRow = Frame(self.main_frame)
        self.seventhRow.grid(column=0,row=7)
        optionList = ['(load xml file)']
        self.startStateLabel = Label(self.seventhRow,text='Start State')
        self.startStateLabel.grid(column=0,row=7)
        self.startStateMenu = OptionMenu(self.seventhRow,self.startState,*optionList)
        self.startStateMenu.grid(column=1,row=7)


    def onXMLFileSelect(self, event=None):
        'Opens a dialogue box to select the xml file'
        f = askopenfilename(initialdir=self.workingDir)
        if f:
            self.rewriteEntryField(self.xmlFileText, f)
            self.workingDir = os.path.dirname(f)

    def onOutputFileSelect(self, event=None):
        'Opens a dialogue box to select the output file'
        f = asksaveasfilename(initialdir=self.workingDir)
        if f:
            self.rewriteEntryField(self.outputFileText, f)
            self.workingDir = os.path.dirname(f)
        
    def onGenerate(self, event=None):
        dbg = False
        if dbg: print "--> onGenerate"
        goOn = True
        outputFile = ''
        outputFile = self.getFieldText(self.outputFileText)
        inputFile = ''
        inputFile = self.getFieldText(self.xmlFileText)
        if dbg:
            print "Info: PromptFileGenerator.onGenerate: inputFile =",inputFile
            print "Info: PromptFileGenerator.onGenerate: outputFile =",outputFile
        if outputFile == '':
            self.listbox.insert(END,"Please specify an output file")
            goOn = False
        if inputFile == '':
            self.listbox.insert(END,"Please specify an input file")
            goOn = False
        if goOn:
            sm = self.makeStateMachine(inputFile,outputFile)
            if sm.errorMsgs:
                for msg in sm.errorMsgs:
                    self.listbox.insert(END,msg)
            else:
                #self.writeXLPrompts(sm,outputFile)
                self.writePrompts(sm,outputFile)
        if dbg: print "<-- onGenerate"
        return
    
    def onInteract(self, event=None):
        dbg = False
        if dbg: print "--> onInteract"
        if dbg: print  "self.xmlFileText=",self.getFieldText(self.xmlFileText)
        inputFile = self.getFieldText(self.xmlFileText)
        if dbg:
            print "Info: PromptFileGenerator.onInteract: inputFile =",inputFile
        if inputFile == '':
            self.listbox.insert(END,"Please specify an input xml file")
        else:
            if self.stateNames:
                if self.startState:
                    if self.startState in self.stateNames:
                        self.stateMachine.run(self.startState,False,None)
            else:            
                if dbg: print "self.startStateMenu=",self.startStateMenu
                if self.startStateMenu:                                     # if we already have the start state menu
                    self.startStateMenu.pack_forget()                           # kill the old one                                                       
                self.stateMachine = self.makeStateMachine(inputFile)            # read in the state machine
                if len(self.stateMachine.errorMsgs) > 0:
                    for msg in self.stateMachine.errorMsgs:
                        self.listbox.insert(END,msg)
                self.startState = StringVar()
                #self.startState = None
                self.stateNames = self.stateMachine.objectName2Index.keys()                     # get the list of states
                if dbg: print "    in onInteract, stateNames=",self.stateNames
                self.startStateMenu = OptionMenu(self.seventhRow,self.startState,*self.stateNames,command=self.setStartState)
                #self.startStateMenu.pack()
                self.startStateMenu.grid(column=1,row=7)
                if dbg: print "start State is",self.startState
                if self.startState in self.stateNames:
                    self.stateMachine.run(self.startState,False,None)
                else:
                    if dbg: print "no start state"
                    self.listbox.insert(END,"Please choose a start state")    
        if dbg: print "<-- onInteract"
        return

    def setStartState(self,value):
        dbg = False
        if dbg: print "setting startState to",value
        self.startState = value

    def onSimulate(self, event=None):
        dbg = False

        if dbg: print "--> onSimulate"
        if dbg: print  "self.xmlFileText=",self.getFieldText(self.xmlFileText)
        inputFile = self.getFieldText(self.xmlFileText)
        if dbg:
            print "Info: PromptFileGenerator.onSimulate: inputFile =",inputFile
        if inputFile == '':
            self.listbox.insert(END,"Please specify an input xml file")
        else:
            if self.stateNames:
                if self.startState:
                    if self.startState in self.stateNames:
                        #lastSimulation,lastTestCase = runSimulations(inputFile,self.startState ,True)
                        mySimulator = Simulator(inputFile,self.startState,outputType='cyaraXML')       # run a simulation using simulated inputs 
                        self.listbox.insert(END,"Done! Cyara scripts written to sub-directory named CyaraXML")    

            else:            
                if dbg: print "self.startStateMenu=",self.startStateMenu
                if self.startStateMenu:                                     # if we already have the start state menu
                    self.startStateMenu.pack_forget()                           # kill the old one
                self.stateMachine = self.makeStateMachine(inputFile)                       # read in the state machine
                                                     
                self.startState = StringVar()
                #self.startState = None
                self.stateNames = self.stateMachine.objectName2Index.keys()                     # get the list of states
                if dbg: print "    in onSimulate, stateNames=",self.stateNames
                #self.startStateMenu = OptionMenu(self.startStateRow,self.startState,*self.stateNames,command=self.setStartState)
                #self.startStateMenu.pack()

                self.startStateMenu = OptionMenu(self.seventhRow,self.startState,*self.stateNames,command=self.setStartState)
                #self.startStateMenu.pack()
                self.startStateMenu.grid(column=1,row=7)
                
                if dbg: print "start State is",self.startState
                if self.startState in self.stateNames:
                        #lastSimulation,lastTestCase = runSimulations(inputFile,self.startState ,True)
                        mySimulator = Simulator(inputFile,self.startState,outputType='cyaraXML')       # run a simulation using simulated inputs 

                else:
                    if dbg: print "no start state"
                    self.listbox.insert(END,"Please choose a start state")    

        if dbg: print "<-- onSimulate"
        return

    def onJourney(self, event=None):
        dbg = False

        if dbg: print "--> onJourney"
        if dbg: print  "self.xmlFileText=",self.getFieldText(self.xmlFileText)
        inputFile = self.getFieldText(self.xmlFileText)
        if dbg:
            print "Info: PromptFileGenerator.onJourney: inputFile =",inputFile
        if inputFile == '':
            self.listbox.insert(END,"Please specify an input xml file")
        else:
            if self.stateNames:
                if self.startState:
                    if self.startState in self.stateNames:
                        #lastSimulation,lastTestCase = runSimulations(inputFile,self.startState ,True)
                        mySimulator = Simulator(inputFile,self.startState,outputType='journeyTXT')       # run a simulation using simulated inputs 
                        self.listbox.insert(END,"Done! Journey scripts written to sub-directory named journeyTXT") 
            else:            
                if dbg: print "self.startStateMenu=",self.startStateMenu
                if self.startStateMenu:                                     # if we already have the start state menu
                    self.startStateMenu.pack_forget()                           # kill the old one
                self.stateMachine = self.makeStateMachine(inputFile)                       # read in the state machine
                                                     
                self.startState = StringVar()
                #self.startState = None
                self.stateNames = self.stateMachine.objectName2Index.keys()                     # get the list of states
                if dbg: print "    in onJourney, stateNames=",self.stateNames
                #self.startStateMenu = OptionMenu(self.startStateRow,self.startState,*self.stateNames,command=self.setStartState)
                #self.startStateMenu.pack()

                self.startStateMenu = OptionMenu(self.seventhRow,self.startState,*self.stateNames,command=self.setStartState)
                #self.startStateMenu.pack()
                self.startStateMenu.grid(column=1,row=7)
                
                if dbg: print "start State is",self.startState
                if self.startState in self.stateNames:
                        #lastSimulation,lastTestCase = runSimulations(inputFile,self.startState ,True)
                        mySimulator = Simulator(inputFile,self.startState,outputType='journeyXLS')       # run a simulation using simulated inputs 

                else:
                    if dbg: print "no start state"
                    self.listbox.insert(END,"Please choose a start state")    

        if dbg: print "<-- journeyXLS"
        return

    def writeXLPrompts(self,sm,outputFile):
        dbg = 1
        if dbg: print "-->writeXLtest"
        self.listbox.insert(END,"Creating output prompts xls file")
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet('Prompts',cell_overwrite_ok=True)
        sheet.write(0,0,'Prompt Name')
        sheet.write(0,1,'Prompt Text')
        rowCtr = 1
        for aPromptName in sm.prompts:
            aPrompt = sm.prompts[aPromptName]
            sheet.write(rowCtr,0,aPrompt.name)
            sheet.write(rowCtr,1,aPrompt.text)
            rowCtr = rowCtr + 1
        wbk.save(outputFile)
        if dbg: print "<-- writeXLtest"

    def writePrompts(self,sm,outputFile):
        dbg = False
        if dbg: print "-->writePrompts"
        self.listbox.insert(END,"Creating output prompts file")
        with open(outputFile,"w") as outFile:
            outFile.write("Prompt Name\tPrompt Text\n")
            for aPromptName in sm.prompts:
                aPromptObj = sm.prompts[aPromptName]
                if dbg: print aPromptObj.name,aPromptObj.text
                outText =  aPromptObj.text.encode('utf8')

                outFile.write("%s\t%s\n" %(aPromptObj.name,outText))
        outFile.close()
        if dbg: print "<-- writePrompts"

    def rewriteEntryField(self, field, text):
        'Clears out the text in <field> and inserts <text>'
        field.delete(0, END)
        field.insert(0, text)

    def getFieldText(self, field):
        'Gets the text in <field>'
        return field.get()

    def makeStateMachine(self,inputFileName,outputFileName=None):
        dbg = False
        if dbg: print "--> makeStateMachine"
        self.listbox.insert(END,"Initializing state machine")
        sm = StateMachine()
        self.listbox.insert(END,"Reading input DrawIO xml file")
        sm.readDrawIOXMLFile(inputFileName)
        sm.makeGraph()
        return sm
        if dbg: print "<-- makeStateMachine"



if __name__ == '__main__':
    dbg = False
    if dbg: print "starting"
    root = Tk()
    app = VTK_GUI_Generator(root)
    root.mainloop()
    if dbg: print "stopping"
