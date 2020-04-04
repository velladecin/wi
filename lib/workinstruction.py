#!/usr/bin/env python3.7
import os
import re
import sys
import subprocess
from glob import glob
from pprint import pprint


##
## Instruction

class Workinstruction:
    def __init__(self, instruction, dirname):
        # should have a valid directory here
        self.instruction = instruction
        self.topics = {}
        for f in list(filter(lambda x: os.path.isfile(x) and re.search(r'[^~]$', x), glob("%s/*" % dirname))):
            t = re.search(r'.*/(.*)$', f)
            try:
                self.topics[t[1]] = f
            except IndexError:
                print("Could not retrieve topc")

    def getName(self):
        return self.instruction

    def getTopics(self):
        return self.topics

    def isTopic(self, t):
        try:
            self.topics[t]
            return True
        except KeyError:
            return False

    def readTopic(self, t):
        topic = self.__getTopic(t)

        try:
            with open(topic, 'r') as f:
                data = f.readlines()
        except (FileNotFoundError, TypeError):
            # Somebody removed our file, or topic does not exist.
            # This *should* not happen but..
            print("Could not retrieve topic: %s" % t)
            data = []

        return data

    def printTopic(self, t):
        for line in self.readTopic(t):
            print(line.rstrip())

    def editTopic(self, t):
        topic = self.__getTopic(t)
        subprocess.run(["vi", topic])

    def __getTopic(self, t):
        try:
            return self.topics[t]
        except KeyError:
            return None

##
## Shell

class CmdError(Exception):
    pass

class WiShell:
    def __init__(self, wi, prompt="wi>", history=50):
        self.wi = wi
        if not re.search(r'\s$', prompt):
            prompt = "%s " % prompt
        self.prompt = prompt
        self.history = history

    def run(self):
        currentTopic = None # topic cache
        cmdHistory = []

        while True:
            uinput = input("%s" % self.prompt).split()
            try:
                cmd = uinput[0]
                args = uinput[1:]
                cmdHistory.append(uinput)
            except IndexError:
                continue

            if len(cmdHistory) > self.history:
                cmdHistory = cmdHistory[1:] # remove oldest (first) element 

            if cmd == "exit" or cmd == "quit" or cmd == "q" or cmd == "x":
                break

            if cmd == "help":
                self.__help()
                continue

            if cmd == "ls":
                for w in sorted(self.wi):
                    print(w)
                    
                continue

            if cmd == "lt":
                if self.__cmdOK(cmd, args, 1):
                    # cache only single wi
                    # reset to default when more than single
                    currentTopic = args[0] if len(args) == 1 else None

                    for count in range(len(args)):
                        w = args[count]

                        print(" %s" % w)
                        try:
                            wi = self.wi[w]
                        except KeyError:
                            print("%s not found" % w)
                            currentTopic = None
                            continue

                        for t in wi.getTopics():
                            print("  %s" % t)

                        if count != (len(args)-1):
                            print(" ---")

                continue

            if cmd == "vt" or cmd == "et":
                if currentTopic and len(args) < 2:
                    args.insert(0, currentTopic)

                if self.__cmdOK(cmd, args, 2):
                    w = args[0]
                    t = args[1]

                    try:
                        wi = self.wi[w]
                    except KeyError:
                        print("%s not found" % w)
                        continue

                    if not wi.isTopic(t):
                        print("%s:%s not found" % (w, t))
                        continue

                    if cmd == "vt":
                        wi.printTopic(t)

                    if cmd == "et":
                        wi.editTopic(t)

                continue

    #
    # Private ;)

    def __help(self, cmd=None):
        cmds = {
            "ls": """
ls
    list all known work instructions (wi)""",
            "lt": """
lt <wi> [<wi> ..]
    List all known topics for <wi>.
    When single <wi> used, it is cached and implied for subsequent commands (requiring <wi> as argument) and <wi> can then be omitted in those commands.
    When multiple <wi> used, no caching and/or implication take place.""",
            "vt": """
vt <wi> <topic>
    view <topic> for <wi>""",
            "et": """
et <wi> <topic>
    edit <topic> for <wi>""",
            "ct": """
ct <wi> <topic>
    create <topic> for <wi>""",
            "exit": """
exit|x
    exit program""",
            "quit": """
quit|q
    same as exit"""
        }

        try:
            print(cmds[cmd])
        except KeyError:
            for c in cmds:
                print(cmds[c])

    def __cmdOK(self, cmd, args, require_arg=0):
        if require_arg > 0:
            if not args:
                self.__help(cmd)
                return False

            try:
                args[require_arg-1]
            except IndexError:
                self.__help(cmd)
                return False

        return True

