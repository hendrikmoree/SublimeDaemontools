from subprocess import Popen, PIPE, TimeoutExpired
from os.path import dirname, abspath
from SublimeUtils.sublimeutils import projectRoot

mydir = dirname(abspath(__file__))


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
