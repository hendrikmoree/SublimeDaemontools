from subprocess import Popen, PIPE, TimeoutExpired
from os.path import dirname, abspath
from time import sleep

mydir = dirname(abspath(__file__))

def projectRoot(view):
    currentFile = view.file_name()
    if currentFile and view.window():
        for folder in view.window().folders():
            if folder in currentFile:
                return folder
    elif view.window() and view.window().folders():
        return view.window().folders()[0]

def remoteCommand(view, command):
    rootDir = view.rootDir if hasattr(view, 'rootDir') else projectRoot(view)
    args = ["bash", "remote_command.sh", rootDir] + ['"' + command + '"']
    proc = Popen(' '.join(args), cwd=mydir, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
    try:
        stdout, stderr = proc.communicate(timeout=2)
    except TimeoutExpired:
        proc = Popen(' '.join(args), cwd=mydir, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
        stdout, stderr = proc.communicate(timeout=2)
    return stdout.decode('utf-8')
