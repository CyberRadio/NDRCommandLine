#!/usr/bin/python3

___version___ = "23.06.01"

import CyberRadioDriver as crd
import json
import getopt
import sys
import time
import os
import readline
import logging
import signal

def signal_handler(sig, frame):
    print("Caught CTRL+C, exiting...")
    sys.exit(0)

LOG_FILENAME = '/tmp/completer.log'
HISTORY_FILENAME = '/tmp/completer.hist'

logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')

def get_history_items():
    return [ readline.get_history_item(i) for i in range(1, readline.get_current_history_length() + 1) ]

ip = "127.0.0.1"

def usage():
    print("ndrcommandline.py -i <ip> -r <radio> -v [verbose] -h show this help")

def prettyCommand(r, c):
    print("%s"%(c['cmd']).center(80,'-'))
    result = r.sendCommand(json.dumps(c), 1.0)
    jr = json.loads(result)
    print(json.dumps(jr, indent=4, sort_keys=True))
    print("-".center(80,'-'))

def getIndexOfQuotes(inStr):
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
       print("We found a CLI command")
       # expected form: cli input "some command to run"
       begin, end = getIndexOfQuotes(inputStr)
       print(begin)
       print(end)
       # we know to expect cli and input so ignore those.
       cliCommand = inputStr[begin+1:end]
       print(cliCommand)
       jsonToFill['cmd'] = "cli"
       jsonToFill['params']['input'] = cliCommand
       return jsonToFill

def parseLine(inputList, jsonCommand):
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
    # inputList[0] == "cli" 
    # [1] == "input"
    # [2:-1] == input value.
    print("We have %d params" % len(inputList))
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


def createAndSendJsonCommand(input, radio, verbose):
    msgId = 1
    jsonCommand = { 'cmd' : None, 'params' : { } }
    cmd_line = input.split(' ')
    if "cli" in cmd_line:
        jsonCommand, query = parseCLI( cmd_line, jsonCommand)
    else:
        jsonCommand, query = parseLine(cmd_line, jsonCommand)
    print("TX: " + str(jsonCommand))
    response = radio.sendCommand(json.dumps(jsonCommand),5.0)
    hool = json.dumps(jsonCommand, indent=4, sort_keys=True)
    if verbose is  True:
        print("JSON TX: " + str(hool))
        print("JSON RX: " + str(response))
    msgId = msgId + 1
    checker = json.loads(response).get("success")
    if checker == True:
        if query:
            jrsp = json.loads(response).get("result")
            jrsp = json.dumps(jrsp, indent=4, sort_keys=True)
            if jrsp == "null":
                print("Query command detected with no result")
            else:
                print("RX: " + str(jrsp))
        else:
            print("RX: " + str(response))
    else:
        print("!!!ERROR!!!")
        error = json.loads(response).get("error")
        error = json.dumps(error, indent=4, sort_keys=True)
        print(error)

def sendCommandsFromFile(filename, radio, verbose):
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
    signal.signal(signal.SIGINT, signal_handler)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:hi:vr:", ["help"])
    except getopt.GetoptError as err:
            # print help information and exit:
            print(str(err))  # will print something like "option -a not recognized"
            usage()
            sys.exit(2)
    output = None
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
        elif o == "-r":
            radiochecker = a
            if radiochecker not in crd.getSupportedRadios():
                print("Unsupported Radio: Please check the supported Radios listed below...")
                print(crd.getSupportedRadios())
                sys.exit()
        elif o == '-f':
            inputFile = a
            print("Command File set to: %s" % inputFile)
        else:
            assert False, "unhandled option"
            sys.exit(1)


    try:
        if radiochecker == None:
            print("Radio was not selected. Please select one of the supported radios listed below...")
            print(crd.getSupportedRadios())
            sys.exit()
    except:
        print("Something went wrong. Please make sure there is -i and -r on the command line before running...")
        print("ndr562commandline.py -i <ip> -r <radio> -v [verbose] -h show this help")
        sys.exit()

    msgId = 1

    radio = crd.getRadioObject(radiochecker, host=ip ,verbose=verbose)

    if os.path.exists(HISTORY_FILENAME):
        readline.read_history_file(HISTORY_FILENAME)
        #print 'Max history file length:', readline.get_history_length()
        #print 'Startup history:', get_history_items()

    if inputFile is None:
        try:
            while True:
                saved_command = ''
                query = False
                cmd = input('>> ')
                if cmd == "quit":
                    sys.exit()
                if cmd == "":
                    print("No input provided")
                else:
                    createAndSendJsonCommand(cmd, radio, verbose)
        finally:
            print("Final history : \n", get_history_items())
            readline.write_history_file(HISTORY_FILENAME)
    else:
        # we have a command file.
        sendCommandsFromFile(inputFile, radio, verbose)

if __name__ == "__main__":
    main()
