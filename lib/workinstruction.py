#!/usr/bin/env python3.7
import os
import re
import sys
import subprocess
from glob import glob
from pprint import pprint

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

