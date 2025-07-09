#!/usr/bin/env python3

___version___ = "25.07.09"

try:
    import CyberRadioDriver as crd
except:
    print("CyberRadioDriver unavailible, utilizing basic c&c")
import socket
import json
import getopt
import sys
import time
import os
import tempfile
import logging
import signal

WINDOWS_ENV = False

if os.name == 'nt':
    WINDOWS_ENV = True
else:
    pass
    
try:
    import readline
except ImportError:
    print("readline module not available, command history will not be saved.")
    readline = None


class BasicCommandSocket:
    """
    A basic command socket for sending commands to an NDR radio.
    This class uses UDP to communicate with the radio, sending JSON commands
    and receiving JSON responses. It is designed for simple command and control
    operations, such as querying status or sending configuration commands.
    """
    def __init__(self, ip, port, timeout=1.0, debug=False):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.debug = debug
        self.msgid = 0

    def sendCommand(self, cmd, timeout=1.0):
        self.msgid = self.msgid + 1
        cmd["msg"] = self.msgid
        if self.debug:
            print("TX: " + str(cmd))
        try:
            self.sock.sendto(str.encode(json.dumps(cmd)), (self.ip, self.port))
            data, addr = self.sock.recvfrom(2048) # buffer size is 1024 bytes
        except socket.timeout:
            print("Socket timeout after {} seconds, radio can be rebooting.".format(timeout))
            return {}
        if self.debug:
            print("RX: " + str(data))
        return json.loads(data)


def signal_handler(sig, frame):
    """
    Handle the CTRL+C signal to gracefully exit the program.
    """
    print("Caught CTRL+C, exiting...")
    sys.exit(0)

temp_dir = tempfile.gettempdir()
LOG_FILENAME = temp_dir + '/ndrcommandline.log'
HISTORY_FILENAME = temp_dir + '/completer.hist'

logger = logging.getLogger('ndrcommandline')
logger.setLevel(logging.INFO)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)   
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(formatter)
stderr_handler.setFormatter(formatter)  
logger.addHandler(stdout_handler)
logger.addHandler(stderr_handler)
file_handler = logging.FileHandler(LOG_FILENAME)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


if readline is not None:
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set editing-mode vi')

def get_history_items():
    if readline is None:
        return []
    return [ readline.get_history_item(i) for i in range(1, readline.get_current_history_length() + 1) ]

ip = "127.0.0.1"

def usage():
    print("ndrcommandline.py -i <ip> -r <radio> -v [verbose] -h show this help")

# def prettyCommand(r, c):
#     """
#     Prints a json command or response in a pretty format.
#     This function is used to format the command or response for better readability.
#     """
#     print("%s"%(c['cmd']).center(80,'-'))
#     result = r.sendCommand(json.dumps(c), 1.0)
#     jr = json.loads(result)
#     print(json.dumps(jr, indent=4, sort_keys=True))
#     print("-".center(80,'-'))

def getIndexOfQuotes(inStr):
    """
    Get the start and end index of the first pair of quotes in a string.
    """
    beginQuote = -1
    endQuote = -1
    count = 0
    for char in inStr:
        if char == '"' and beginQuote == -1 and endQuote == -1:
            beginQuote = count
        elif char == '"' and beginQuote > -1 and endQuote == -1:
            endQuote = count
        count +=1
    return beginQuote, endQuote

def processCliCommand(inputStr, jsonToFill):
    """
    Process a CLI command from the input string and fill the JSON object.
    """
    # expected form: cli input "some command to run"
    begin, end = getIndexOfQuotes(inputStr)
    # we know to expect cli and input so ignore those.
    cliCommand = inputStr[begin+1:end]
    jsonToFill['cmd'] = "cli"
    jsonToFill['params']['input'] = cliCommand
    return jsonToFill

def parseLine(inputList, jsonCommand):
    """
    Parse a line of input into a JSON command structure.
    This function takes a list of input strings, where the first element is the command,
    and the subsequent elements are parameters. It constructs a JSON command object
    with the command and its parameters, converting them to appropriate types (string, int, float, bool).
    It also handles special cases like scientific notation and quoted strings.
    The function returns the constructed JSON command and a boolean indicating if the command is a query.
    The inputList is expected to be a list of strings, where the first element is the command
    and the rest are parameters. The command is expected to be in the format:
    ["command", "param1", "param2", ...]
    The function will create a JSON object with the command and parameters, converting types as necessary.
    For example, if the inputList is ["qstatus", "verbose", "true"],
    the resulting JSON command would be:
    {
        "cmd": "qstatus",
        "params": {
            "verbose": true
        }
    }
    """
    count = 0
    query = False
    savedParam = None
    for c in inputList:
        if count == 0:
            jsonCommand['cmd'] = c
            saved_command = c
            if saved_command[0] == 'q':
                query = True
        elif savedParam == None:
            jsonCommand['params'][c] = None
            savedParam = c
        else:
            jsonCommand['params'][savedParam] = c
            #if isinstance(c, basestring) == True:
            dect='\"'
            cap = c
            c = c.lower()
            if dect in c:
                c = cap.replace(dect,"")
                jsonCommand['params'][savedParam] = c
            elif c.isdigit() == True:
                c = int(c)
                jsonCommand['params'][savedParam] = c
            elif c[0] == "-":
                if c[-2] == 'e':
                    sp = c.split('e')
                    freq = int(sp[0])
                    expo = int(sp[1])
                    result = freq*pow(10,expo)
                    c = result
                    jsonCommand['params'][savedParam] = c
                else:
                    c = int(c)
                    jsonCommand['params'][savedParam] = c
            elif c[-2] == 'e':
                sp = c.split('e')
                freq = sp[0]
                expo = sp[1]
                if expo.isdigit() == True:
                    expo = int(expo)
                    freq = int(freq)
                    result = freq*pow(10,expo)
                    c = result
                    jsonCommand['params'][savedParam] = c
                else:
                    jsonCommand['params'][savedParam] = c
            elif c == 'true':
                c = True
                jsonCommand['params'][savedParam] = c
            elif c == 'false':
                c = False
                jsonCommand['params'][savedParam] = c
            savedParam = None
        count = count + 1
    return jsonCommand,query 

def parseCLI( inputList, jsonCommand):
    """
    Parse a CLI command from the input list and fill the JSON command structure.
    This function takes a list of input strings, where the first element is the command,
    and the second element is 'input', followed by the actual command to run.
    It constructs a JSON command object with the command and its parameters.
    The inputList is expected to be in the format:
    ["cli", "input", "some command to run"]
    The function will create a JSON object with the command and parameters, converting them to appropriate types.
    For example, if the inputList is ["cli", "input", "ls -l /home/user"],
    the resulting JSON command would be:
    {
        "cmd": "cli",
        "params": {
            "input": "ls -l /home/user"
        }
    }
    """
    l = len(inputList)
    paramsstring = ""
    jsonCommand['cmd'] = inputList[0]
    count = 0
    for var in inputList[2:]:
        paramsstring = paramsstring + var.replace('\"',"")
        if count != l-1:
           paramsstring = paramsstring + " "
    jsonCommand['params'] = { "input" : paramsstring[:-1] }
    return jsonCommand, True

################################################################################
##
################################################################################
def createAndSendJsonCommand(input, radio, verbose):
    """
    Create a JSON command from the input string and send it to the radio.
    This function takes an input string, which can be a command or a CLI command,
    parses it into a JSON command structure, and sends it to the radio using the
    BasicCommandSocket class. It handles both regular commands and CLI commands,
    and prints the response from the radio in a formatted way.
    The input string is expected to be in the format:
    "command param1 param2 ..."
    or for CLI commands:
    "cli input \"some command to run\""
    The function will create a JSON object with the command and parameters,
    converting them to appropriate types (string, int, float, bool).
    It will then send the command to the radio and print the response.
    For example, if the input is "qstatus verbose true",
    the resulting JSON command would be:
    {
        "cmd": "qstatus",
        "params": {
            "verbose": true
        }
    }
    """
    msgId = 1
    jsonCommand = { 'cmd' : None, 'params' : { } }
    cmd_line = input.split(' ')
    if "cli" in cmd_line:
        jsonCommand, query = parseCLI( cmd_line, jsonCommand)
    else:
        jsonCommand, query = parseLine(cmd_line, jsonCommand)
    logger.info("TX: " + str(jsonCommand))
    response = radio.sendCommand(jsonCommand,5.0)
    hool = json.dumps(jsonCommand, indent=4, sort_keys=True)
    if verbose is  True:
        logger.debug("JSON TX: " + str(hool))
        logger.debug("JSON RX: " + str(response))
    msgId = msgId + 1
    checker = response.get("success")
    if checker == True:
        if query:
            jrsp = response.get("result")
            jrsp = json.dumps(jrsp, indent=4, sort_keys=True)
            if jrsp == "null":
                logger.error("Query command detected with no result")
            else:
                logger.info("RX: " + str(jrsp))
        else:
            logger.info("RX: " + str(response))
    else:
        logger.error("!!!ERROR!!!")
        error = json.loads(response).get("error")
        error = json.dumps(error, indent=4, sort_keys=True)
        logger.error(error)

def sendCommandsFromFile(filename, radio, verbose):
    """
    Send commands from a file to the radio.
    """
    msgId = 1
    jsonCommand = { 'msg' : msgId, 'cmd' : None, 'params' : { } }
    fd = open(filename, 'r')
    lines = fd.readlines()
    for line in lines:
        if line == "\n":
            break
        # split the line on spaces
        line = line.replace("\n", "")
        createAndSendJsonCommand(line, radio, verbose)

def main():
    """
    Main function to handle command line arguments and execute commands.
    This function sets up signal handling, parses command line options,
    initializes the radio connection, and processes user input or command files.
    It supports interactive command input and reading commands from a file.
    It also handles graceful shutdown on receiving a CTRL+C signal.
    It uses the BasicCommandSocket class to communicate with the radio.
    It supports verbose output and command history saving.
    """
    signal.signal(signal.SIGINT, signal_handler)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:hi:vr:", ["help"])
    except getopt.GetoptError as err:
            # print help information and exit:
            print(str(err))  # will print something like "option -a not recognized"
            usage()
            sys.exit(2)
    verbose = False
    inputFile = None
    for o, a in opts:
        if o == "-v":
            verbose = True
            print("Verbose Mode is True")
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o == "-i":
            ip = a
            print("IP Set to: " + ip)
        elif o == '-f':
            inputFile = a
            print("Command File set to: %s" % inputFile)
        else:
            assert False, "unhandled option"
            sys.exit(1)

    radio = BasicCommandSocket(ip, 19091, timeout=1.0, debug=verbose)
    # radio = crd.getRadioObject(radiochecker, host=ip ,verbose=verbose)

    if os.path.exists(HISTORY_FILENAME):
        try:
            readline.read_history_file(HISTORY_FILENAME)
        except FileNotFoundError:
            print("History file not found, starting fresh.")

    if inputFile is None:
        try:
            while True:
                cmd = input('>> ')
                if cmd == "quit":
                    sys.exit()
                if cmd == "":
                    logger.warning("No input provided")
                else:
                    createAndSendJsonCommand(cmd, radio, verbose)
        finally:
            try:
                logger.info("Final history : \n" + str(get_history_items()))
            except KeyboardInterrupt:
                print("Exiting due to keyboard interrupt.")
            except Exception as e:
                logger.error("Error while getting history items: " + str(e))
            try:
                readline.write_history_file(HISTORY_FILENAME)
            except FileNotFoundError:
                print("History file not found, cannot save history.")
    else:
        # we have a command file.
        sendCommandsFromFile(inputFile, radio, verbose)

if __name__ == "__main__":
    main()
