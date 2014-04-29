import sys

def stdout(s):
    sys.stdout.write(s)
    sys.stdout.flush()

def stderr(s):
    sys.stderr.write(s)
    sys.stderr.flush()
