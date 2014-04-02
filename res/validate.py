# -*- coding: utf-8 -*-

import sys
import os
import shutil
import subprocess
from pprint import pprint

# ------------------------------------------------------------------------------

rootDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
logsDir = os.path.join(rootDir, 'logs')
resDir  = os.path.join(rootDir, 'res')
srcDir  = os.path.join(rootDir, 'src')

# ------------------------------------------------------------------------------

class Arduino:
    if sys.platform == 'darwin':
        binary  = '/Applications/Arduino.app/Contents/MacOS/JavaApplicationStub'
        home    = os.path.expanduser('~/Documents/Arduino')
    elif sys.platform == 'win32':
        binary  = 'arduino.exe'
        home    = os.path.expanduser('~/My Documents/Arduino')
    elif sys.platform == 'linux':
        binary  = 'arduino'
        home    = os.path.expanduser('~/Arduino')
    else:
        print('Unsupported platform %s' % str(sys.platform))
        sys.exit(1)

    libraryDir = os.path.join(home, 'libraries')

    boards = {
        'Uno':          'arduino:avr:uno',
        'Leonardo':     'arduino:avr:leonardo',
        'Mega':         'arduino:avr:mega',
    }

    def checkReturnCode(code):
        if code == 0:
            return True
        if code == 1:
            print('Operation failed.')
        if code == 2:
            print('File not found')
        if code == 3:
            print('Invalid argument')
        return False

    def verify(sketch, board):
        return  Arduino.checkReturnCode(subprocess.call([
                Arduino.binary,
                '--verify', sketch,
                '--board',  board,
                #'--verbose-build',
            ], stdout = open(os.devnull, 'wb')))

# ------------------------------------------------------------------------------

class ArduinoMidiLibrary:
    def __init__(self):
        self.path       = os.path.join(Arduino.libraryDir, 'MIDI')
        self.sources    = self.getSources()
        self.resources  = self.getResources()

    def getSources(self):
        sources = dict()
        for root, dirs, files in os.walk(srcDir):
            for name, ext in [os.path.splitext(f) for f in files]:
                if ext in ('.cpp', '.hpp', '.h'):
                    source  = os.path.join(root, name + ext)
                    dest    = os.path.join(self.path, os.path.relpath(source, srcDir))
                    sources[source] = dest
        return sources

    def getResources(self):
        return {
            os.path.join(resDir, 'keywords.txt'): os.path.join(self.path, 'keywords.txt'),
            os.path.join(resDir, 'examples/'): os.path.join(self.path, 'examples/'),
        }

    def install(self):
        payloads = dict(list(self.sources.items()) + list(self.resources.items()))
        for s,d in payloads.items():
            if not os.path.exists(os.path.dirname(d)):
                os.makedirs(os.path.dirname(d))
            if os.path.isfile(s):
                shutil.copy2(s, d)
            elif os.path.isdir(s):
                if os.path.exists(d):
                    shutil.rmtree(d)
                shutil.copytree(s, d)

    def getInstalledExamples(self):
        exDir = os.path.join(self.path, 'examples')
        return [os.path.join(exDir, x, x + '.ino') for x in os.listdir(exDir)]

    def validate(self):
        for boardName, boardId in Arduino.boards.items():
            # Validate examples
            print('Validation for Arduino %s' % boardName)
            for example in self.getInstalledExamples():
                if not Arduino.verify(example, boardId):
                    print('{0:40} {1}'.format(os.path.basename(example), 'FAILED'))
                    return False
                else:
                    print('{0:40} {1}'.format(os.path.basename(example), 'PASSED'))
        return True

# ------------------------------------------------------------------------------

def main():
    lib = ArduinoMidiLibrary()
    lib.install()
    if lib.validate():
        print('Validation passed')
    else:
        print('Validation failed')

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()
