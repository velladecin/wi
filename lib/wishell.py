#!/usr/bin/env python3.7
import os.path
import re
import sys, tty, termios
from pprint import pprint
from glob import glob
from vella.workinstruction import Workinstruction

class CmdError(Exception):
    pass

class WiShell:
    def __init__(self, location, prompt="wi>", history=50):
        self.wi = {}
        for name in glob("%s/*" % location):
            if not os.path.isdir(name):
                continue

            i = re.search(r'(.*/)?(.*)$', name)
            if not i:
                print("Could not match instruction name in '%s', skipping" % name)
                continue

            wi = Workinstruction(i.group(2), name)
            self.wi[wi.getName()] = wi

        if not re.search(r'\s$', prompt):
            prompt = "%s " % prompt
        self.prompt = prompt
        self.history = history

    def run(self):
        currentTopic = None # topic cache
        cmdHistory = []
        arrowUp = 0

        while True:
            uinput = input("%s" % self.prompt).split()

            """
            fd = sys.stdin.fileno()
            oldsetting = termios.tcgetattr(fd)

            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(3) # only interested in arrow up
                                        # TODO <tab><tab>
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, oldsetting)

            if len(cmdHistory):
                if key == '\x1b[A':
                    uinput = input("%s%s" % (self.prompt, cmdHistory[-1])).split()
            else:
                uinput = input("%s" % self.prompt).split()

            if key == '\x1b[A':
                if len(cmdHistory):
                    arrowup += 1
                    idx = arrowup * -1

                    try:
                        c = cmdHistory[idx]
                    except IndexError:
                        c = cmdHistory[idx+1]
                        arrowup -= 1

                    uinput = input("%s%s" % (self.prompt, c)).split()
            else:
                arrowup = 0
            """

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
