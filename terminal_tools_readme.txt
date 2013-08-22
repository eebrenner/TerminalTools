This program is intended to aid terminal communications.  The communications will print to the command prompt.  

Logging:
	Logs are cleared when the program is launched
	Checking the "enable logging" check box will start logging the serial communications
	Unchecking will cease the logging.
	Logging will append to the log file during a single program session
	The logs can be viewed from the file menu
		To get the most current logs, uncheck the logging button prior to viewing

Individual Commands:
	The defaults for the 5 individual commands can be changed in teminal_tools_defaultCommands.txt
	Clicking the Send button next to the field will input the corresponding textbox text to the terminal

Bulk Commands:
	The tools can send bulk commands to the terminal
	Enter the commands on their own line in the bulk command section
	The program will wait till the previous command is successful before sending the next
	The bulk commands will cease sending if a command returns an error