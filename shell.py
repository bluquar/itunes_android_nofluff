import subprocess

ESCAPE_CHARS = {"'", ' ', '(', ')', '&', ',', ';'}

class Shell(object):
    def __init__(self, aliases=None):
        self.aliases = aliases

    def apply_aliases(self, command):
        if self.aliases is not None:
            for key, val in self.aliases.iteritems():
                command = command.replace(key, val)
        return command

    def cmd(self, command, _shell=True):
        command = self.apply_aliases(command)
        p = subprocess.Popen(command, shell=_shell,
                             stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
        text, err = p.communicate()
        return text

def escape(s):
    L = []
    for c in s:
        if c in ESCAPE_CHARS:
            L.append('\\')
        L.append(c)
    return ''.join(L)
