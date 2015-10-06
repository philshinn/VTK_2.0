from Tkinter import *
from MakeScriptsValues import *
from VTK_Code import *
from tkFileDialog import *
from tkMessageBox import showerror, showinfo
import xlwt
import xlrd
from exceptions import *
from time import time
import os
import sys

class PromptFileGenerator(object):

    def __init__(self, master=None):
        'Creates the GUI'
        # Set up the main frame
        self.workingDir = os.getcwd()
        self.main_frame = Frame(master)
        if master:
            master.title(APPLICATION_TITLE)
        else:
            self.main_frame.title(APPLICATION_TITLE)
        self.main_frame.pack(fill=BOTH, expand=1)

        # Set up the xml file entry field
        xmlFileRow = Frame(self.main_frame)
        xmlFileLabel = Label(xmlFileRow, text=INPUT_FILE_LABEL)
        xmlFileLabel.pack(side=LEFT)
        self.xmlFileText = Entry(xmlFileRow)
        self.xmlFileText.pack(side=LEFT, expand=1,fill=X)
        self.xmlFileSelector = Button(xmlFileRow, text=LOAD_XML_BUTTON, command=self.onXMLFileSelect)
        self.xmlFileSelector.pack(side=LEFT)
        xmlFileRow.pack(fill=X)
        
        # Set up output file text entry field
        outputFileRow = Frame(self.main_frame)
        Label(outputFileRow,text=OUTPUT_FILE_LABEL).pack(side=LEFT)
        self.outputFileText = Entry(outputFileRow)
        self.outputFileText.pack(side=LEFT, expand=1,fill=X)
        Button(outputFileRow, text=OUTPUT_FILE_BUTTON, command=self.onOutputFileSelect).pack(side=LEFT)
        outputFileRow.pack(fill=X)

        # Set up the listbox to communicate
        boxRow = Frame(self.main_frame)
        scrollbar = Scrollbar(boxRow, orient=VERTICAL)
        self.listbox = Listbox(boxRow, selectmode=EXTENDED, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        #self.listbox.bind('<Double-Button-1>', self.launchFile)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
        boxRow.pack(fill=BOTH, expand=1)
        
        # Set up the generate button row
        finalRow = Frame(self.main_frame)
        Button(finalRow, text=GENERATE_BUTTON, command=self.onGenerate).pack(fill=BOTH)
        finalRow.pack(side=BOTTOM,fill=BOTH)

    def onXMLFileSelect(self, event=None):
        'Opens a dialogue box to select the xml file'
        f = askopenfilename(initialdir=self.workingDir)
        if f:
            self._rewriteEntryField(self.xmlFileText, f)
            self.workingDir = os.path.dirname(f)

    def onOutputFileSelect(self, event=None):
        'Opens a dialogue box to select the output file'
        f = asksaveasfilename(initialdir=self.workingDir)
        if f:
            self._rewriteEntryField(self.outputFileText, f)
            self.workingDir = os.path.dirname(f)
        
    def onGenerate(self, event=None):
        dbg = True
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
            self.writeXLPrompts(sm,outputFile)
        if dbg: print "<-- onGenerate"
        return
    
    def writeXLPrompts(self,sm,outputFile):
        dbg = 1
        if dbg: print "-->writeXLtest"
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

    def _rewriteEntryField(self, field, text):
        'Clears out the text in <field> and inserts <text>'
        field.delete(0, END)
        field.insert(0, text)

    def getFieldText(self, field):
        'Gets the text in <field>'
        return field.get()

    def makeStateMachine(self,inputFileName,outputFileName):
        dbg = True
        if dbg: print "--> makeStateMachine"
        self.listbox.insert(END,"Initializing state machine...")
        sm = StateMachine()
        self.listbox.insert(END,"Reading XML file...")
        sm.readDrawIOXMLFile(inputFileName)
        sm.makeGraph()
        return sm
        if dbg: print "<-- makeStateMachine"

if __name__ == '__main__':
    dbg = True
    if dbg: print "starting"
    root = Tk()
    app = PromptFileGenerator(root)
    root.mainloop()
    if dbg: print "stopping"
