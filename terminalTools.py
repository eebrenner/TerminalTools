#File: spyderSmokeTest.py
#Description: Python script for teraterm functionality
#Date: Aug 12th, 2013
#Author: Marc Brenner

##############################
# Import                     #
##############################

import serial
import io
import time
import sys
import os
import ctypes

import Tkinter
from Tkinter import *
import tkMessageBox
import ScrolledText
import ScrolledText
from ScrolledText import ScrolledText

import threading
from threading import *
import time

##############################
# Class/Functions            #
##############################

def getFile(file):
	lines = [line.strip() for line in open(os.path.join(os.path.dirname(sys.executable),file))]
	return lines
	
class terminalProcess(threading.Thread):
	writeInterrupt = 0
	command = ""
	commandArray = []
	confirmation = ""
	programStatus = 0
	loggingStatus = 0
	ser=0
	
	
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		writeInterrupt = 0
		readText = ""
		i=0
		errorMsg = ""
		terminalProcess.ser.writelines('\r')										#Write lines to serial
		firstRead = 1
		while (True):
			try:
				readText = terminalProcess.ser.readline()								#Read Serial Line
			except ValueError:
				pass
			except (KeyboardInterrupt, SystemExit):
				raise
			if (readText != ""):										#Print if it is not a blank line
				sys.stdout.write(readText)
				#terminalMessage += readText
				if (terminalProcess.loggingStatus == 1):				#Print to log file
					log.write(readText)
			if (terminalProcess.writeInterrupt == 1):					#Check for write interrupt
				#command = "list\r" 
				terminalProcess.ser.writelines(terminalProcess.command)					#Write lines to serial
				time.sleep(.25)
				if (terminalProcess.loggingStatus == 1):				#Print to log file
						log.write(terminalProcess.command)
				print terminalProcess.command
				terminalProcess.writeInterrupt = 0
				errorMsg = terminalProcess.command + " command failed!"
			elif (terminalProcess.writeInterrupt == 2):					#Check for bulk write interrupt
				isCommandFailure = -1
				#isCommandSuccessful = -1
				terminalProcess.commandArray = filter(None,terminalProcess.commandArray)
				L = len(terminalProcess.commandArray)
				isFTM = (readText.find('FTM'))
				if (i == 0) or (isFTM >= 0):							#Write lines as long as there is an FTM
					line = str(terminalProcess.commandArray[i])
					terminalProcess.ser.writelines(line + '\r')							#Write bulk lines to serial
					time.sleep(.25)
					if (terminalProcess.loggingStatus == 1):			#Print to log file
						log.write(line)
					print line
					i = i + 1
					if (i == L):
						i = 0
						terminalProcess.writeInterrupt = 0
					errorMsg = line + " command failed!"
			isCommandSuccessful = (readText.find('SUCCESS'))
			if (isCommandSuccessful >= 0):									#Check to see if command was successful
				terminalProcess.confirmation = " Successful!"
			isCommandFailure = (readText.find('ERROR'))
			if isCommandFailure >= 0:										#Stop if error
				if (firstRead == 0):										
					ctypes.windll.user32.MessageBoxA(0,errorMsg,"ERROR",0)	#Pop up on error
					i = 0
					terminalProcess.writeInterrupt = 0
					terminalProcess.confirmation = " FAILURE!"
				elif (firstRead == 1):										#Ignore first error
					firstRead = 0
			if (terminalProcess.programStatus == 1):						#Exit
				break		

class connection_tk(Tkinter.Tk):
	global defaultSerialSettings
	global ser
	serialStatus = 0
	
	def openSerialEnter(self, event):
		callSerial(self)
		
	def callSerial(self):
		port1 = int(self.connect0.get())
		baud1 = int(self.connect2.get())
		terminalProcess.ser = serial.Serial(port1,baud1,timeout=.01)	#Open Serial port with attributes
		if (terminalThread.isAlive() == False):
			terminalThread.start()										#Start terminal Thread
			print "Connected"
		self.destroy()
		
	def __init__(self,master):
		Tkinter.Tk.__init__(self,master)
		self.master = master
		self.initialize()
	
		self.protocol('WM_DELETE_WINDOW', self.destroy)
		
	def initialize(self):
		self.grid()
		
		port = int(defaultSerialSettings[1])
		port = port - 1
		baud = int(defaultSerialSettings[3])

		#Text Boxes
		self.connect0 = Tkinter.Entry(self)	#Create text box
		self.connect0.grid(column=1, row=1,sticky='EW')							#Align in GUI
		self.connect0.bind("<Return>", self.openSerialEnter)					#Add "enter key" event handler to text box
		self.connect0.insert(0, port)											#Set textbox default text
		
		self.connect2 = Tkinter.Entry(self)	#Create text box
		self.connect2.grid(column=1, row=3,sticky='EW')							#Align in GUI
		self.connect2.bind("<Return>", self.openSerialEnter)					#Add "enter key" event handler to text box
		self.connect2.insert(0, baud)											#Set textbox default text	
		
		#Buttons
		button0 = Tkinter.Button(self,text=u"Connect",command=self.callSerial)	#Create button with OnButtonClick event handler
		button0.grid(column=0,row=4,columnspan=2)

		#Labels
		label0 = Tkinter.Label(self,text="Com Port #:",anchor="w")		#Create label	
		label0.grid(column=0,row=1,columnspan=1,sticky='EW')
		
		label2 = Tkinter.Label(self,text="Baud Rate:",anchor="w")		#Create label	
		label2.grid(column=0,row=3,columnspan=1,sticky='EW')
		
		self.grid_columnconfigure(0,weight=1)							#Resize columns and rows when window is resized
		self.resizable(True,False)										#Prevent vertical sizing
		self.update()													#Render Objects
		self.geometry(self.geometry())									#Fix box size to box size
		self.connect0.focus_set()										#Set focus to entry box
		
class terminalApp_tk(Tkinter.Tk):
	def quitNow(self):
		if (connection_tk.serialStatus == 1):
			terminalProcess.ser.close()
		terminalProcess.programStatus = 1
		self.destroy()
	
	def openLog(self):
		os.system("start notepad.exe terminal_tools_Log.txt") 		#Open workbook in open office automatically
	
	def readMe(self):
		os.system("start notepad.exe terminal_tools_readme.txt") 	#Open workbook in open office automatically
	
	def __init__(self,parent):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.initialize()
		self.protocol('WM_DELETE_WINDOW', self.quitNow)
	
	def connectPage(self):
		print connection_tk.serialStatus
		if (connection_tk.serialStatus == 0):
			connection_tk.serialStatus = 1
			connectPage = connection_tk(None)							#Create GUI named app
			connectPage.title('Connect Page')						#Give app some text in titlebar
			connectPage.mainloop()
			
		else:
			terminalProcess.ser.close()
			connection_tk.serialStatus = 0
			print "Not Connected"
			
	def initialize(self):
		self.grid()

		#MenuBar
		#File
		menubar = Menu(self)										#Create Menu bar
		fileMenu = Menu(menubar,tearoff=0)
		fileMenu.add_command(label="Connect/Disconnect",command=self.connectPage)	#Add submenu for opening log
		fileMenu.add_command(label="View Log",command=self.openLog)	#Add submenu for opening log
		fileMenu.add_command(label="Exit",command=self.quitNow)		#Add submenu for quiting program
		menubar.add_cascade(label="File", menu=fileMenu)			#Add top level menu
		
		
		
		#Help
		helpMenu = Menu(menubar,tearoff=0)
		helpMenu.add_command(label="Readme",command=self.readMe)	
		#helpMenu.add_command(label="About",command=self.about)		
		menubar.add_cascade(label="Help", menu=helpMenu)			
		self.config(menu=menubar)									#Display the menubar
		
		#Logging
		self.logCheckValue = IntVar()
		self.logCheckBox = Checkbutton(self, text = "Enable Logging", variable = self.logCheckValue, command = self.logCheckFunction, height = 1, width = 25)
		self.logCheckBox.grid(column=0, row=0, columnspan=2,sticky='EW')		#Align in GUI
		
		#Text Boxes
		self.terminalVariable0 = Tkinter.StringVar()
		self.terminal0 = Tkinter.Entry(self,textvariable=self.terminalVariable0)#Create text box
		self.terminal0.grid(column=0, row=2,sticky='EW')						#Align in GUI
		self.terminal0.bind("<Return>", self.commandEnter0)						#Add "enter key" event handler to text box
		self.terminalVariable0.set(defaultCommands[0])							#Set textbox default text
		
		self.terminalVariable1 = Tkinter.StringVar()
		self.terminal1 = Tkinter.Entry(self,textvariable=self.terminalVariable1)#Create text box
		self.terminal1.grid(column=0, row=3,sticky='EW')						#Align in GUI
		self.terminal1.bind("<Return>", self.commandEnter1)						#Add "enter key" event handler to text box
		self.terminalVariable1.set(defaultCommands[1])							#Set textbox default text
		
		self.terminalVariable2 = Tkinter.StringVar()
		self.terminal2 = Tkinter.Entry(self,textvariable=self.terminalVariable2)#Create text box
		self.terminal2.grid(column=0, row=4,sticky='EW')						#Align in GUI
		self.terminal2.bind("<Return>", self.commandEnter2)						#Add "enter key" event handler to text box
		self.terminalVariable2.set(defaultCommands[2])							#Set textbox default text
		
		self.terminalVariable3 = Tkinter.StringVar()
		self.terminal3 = Tkinter.Entry(self,textvariable=self.terminalVariable3)#Create text box
		self.terminal3.grid(column=0, row=5,sticky='EW')						#Align in GUI
		self.terminal3.bind("<Return>", self.commandEnter3)						#Add "enter key" event handler to text box
		self.terminalVariable3.set(defaultCommands[3])							#Set textbox default text
		
		self.terminalVariable4 = Tkinter.StringVar()
		self.terminal4 = Tkinter.Entry(self,textvariable=self.terminalVariable4)#Create text box
		self.terminal4.grid(column=0, row=6,sticky='EW')						#Align in GUI
		self.terminal4.bind("<Return>", self.commandEnter4)						#Add "enter key" event handler to text box
		self.terminalVariable4.set(defaultCommands[4])							#Set textbox default text	
		
		self.lumpText = ScrolledText(self, undo=True, wrap=WORD, width = 25, height = 5)
		self.lumpText.grid(column=0,row=8,columnspan=2,sticky='EW')
		
		#Buttons
		button0 = Tkinter.Button(self,text=u"Send 1",command=self.commandButton0)	#Create button with OnButtonClick event handler
		button0.grid(column=1,row=2)
		
		button1 = Tkinter.Button(self,text=u"Send 2",command=self.commandButton1)	#Create button with OnButtonClick event handler
		button1.grid(column=1,row=3)
		
		button2 = Tkinter.Button(self,text=u"Send 3",command=self.commandButton2)	#Create button with OnButtonClick event handler
		button2.grid(column=1,row=4)

		button3 = Tkinter.Button(self,text=u"Send 4",command=self.commandButton3)	#Create button with OnButtonClick event handler
		button3.grid(column=1,row=5)
		
		button4 = Tkinter.Button(self,text=u"Send 5",command=self.commandButton4)	#Create button with OnButtonClick event handler
		button4.grid(column=1,row=6)
		
		button5 = Tkinter.Button(self,text=u"Send Bulk Commands", 
									width=35, command=self.commandButton5)			#Create button with OnButtonClick event handler
		button5.grid(column=0,row=9,columnspan=2)
		
		self.seperator0 = Frame(height=2,bd=1,relief=SUNKEN,bg='#000000')
		self.seperator0.grid(column=0,row=1,columnspan=2,padx=0,pady=5,sticky='EW')
		
		self.seperator1 = Frame(height=2,bd=1,relief=SUNKEN,bg='#000000')
		self.seperator1.grid(column=0,row=7,columnspan=2,padx=0,pady=10,sticky='EW')
		
		#Labels
		#self.labelVariable = Tkinter.StringVar()
		#label = Tkinter.Label(self,textvariable=self.labelVariable,	#Create label
		#						anchor="w",fg="white",bg="blue")	
		#label.grid(column=0,row=5,columnspan=2,sticky='EW')
		#self.labelVariable.set(u"")
		
		self.grid_columnconfigure(0,weight=1)							#Resize columns and rows when window is resized
		self.resizable(True,False)										#Prevent vertical sizing
		self.update()													#Render Objects
		self.geometry(self.geometry())									#Fix box size to box size
		#self.terminal0.focus_set()										#Set focus to entry box
		#self.terminal0.selection_range(0, Tkinter.END)					#Select text in entry box
		
	def logCheckFunction(self):
		global log
		terminalProcess.loggingStatus = self.logCheckValue.get()
		if (terminalProcess.loggingStatus == 0):
			if (log.closed == False):
				log.close()
		elif (terminalProcess.loggingStatus == 1):
			if (log.closed == True):
				log = open((os.path.join(os.path.dirname(sys.executable),'terminal_tools_log.txt')), 'a')

	def commandEnter0(self, event):
		self.commandButton0()
	def commandEnter1(self, event):
		self.commandButton1()
	def commandEnter2(self, event):
		self.commandButton2()
	def commandEnter3(self, event):
		self.commandButton3()
	def commandEnter4(self, event):
		self.commandButton4()	
			
	def commandButton0(self):
		terminalProcess.command = self.terminalVariable0.get() + '\r'
		terminalProcess.writeInterrupt = 1
		#self.labelVariable.set("Command 1" + terminalProcess.confirmation)			#Set label to textbox + "enter" on hitting return
		
	def commandButton1(self):
		terminalProcess.command = self.terminalVariable1.get() + '\r'
		terminalProcess.writeInterrupt = 1											#Interrupt to write to serial
		#self.labelVariable.set("Command 2" + terminalProcess.confirmation)			#Set label to success or failure
		
	def commandButton2(self):
		terminalProcess.command = self.terminalVariable2.get() + '\r'
		terminalProcess.writeInterrupt = 1
		#self.labelVariable.set("Command 3" + terminalProcess.confirmation)			#Set label to success or failure
		
	def commandButton3(self):
		terminalProcess.command = self.terminalVariable3.get() + '\r'
		terminalProcess.writeInterrupt = 1											#Interrupt to write to serial
		#self.labelVariable.set("Command 4" + terminalProcess.confirmation)			#Set label to success or failure
		
	def commandButton4(self):
		#self.labelVariable.set(terminalProcess.confirmation)						#Set label to textbox + "enter" on hitting return
		terminalProcess.command = self.terminalVariable4.get() + '\r'
		terminalProcess.writeInterrupt = 1		
		#self.labelVariable.set("Command 5" + terminalProcess.confirmation)			#Set label to success or failure
		
	def commandButton5(self):
		commandLumpText = self.lumpText.get(1.0, END)
		commandSplit = commandLumpText.split('\n')
		terminalProcess.commandArray = commandSplit
		terminalProcess.writeInterrupt = 2	
		
##############################
# Main                       #
##############################

if __name__ == "__main__":
	defaultCommands = getFile('terminal_tools_defaultCommands.txt')				#Grab default commands from file
	defaultSerialSettings = getFile('terminal_tools_defaultSerialSettings.txt')	#Grab default serial settings from file
	
	log = open((os.path.join(os.path.dirname(sys.executable),'terminal_tools_log.txt')), 'r+')
	log.write("FTM >")
	log.close()
	app = terminalApp_tk(None)							#Create GUI named app
	app.title('Terminal Tools 1.0')						#Give app some text in titlebar
	terminalThread = terminalProcess(1, "Thread-1", 1)	#Need seperate thread so GUI doesn't lock up
	
	app.mainloop()										#Loop GUI
