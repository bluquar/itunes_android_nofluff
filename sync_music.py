import shell
import prints
import collections
import os
import re
import time

### BEGIN CONFIGURATION OPTIONS ###

# location of your itunes library
# (or whatever directory you want to recursively transfer)
ITUNES_LIBRARY = "/Users/chris/Music/iTunes/iTunes Media/Music/"
GALAXY_LIBRARY = "/sdcard/Music/" # use "adb -d shell ls /" to find this

# location of adb
# mine was originally at:
#       ~/Downloads/adt-bundle-mac-x86_64-20140321/sdk/platform-tools/adb
# I created a symlink for convenience, but this is not necessary.
ADB = "/usr/local/bin/adb"

# It often takes more than 1 try to connect to the device
# the device is `offline` at first but wakes up after the
# first attempt. 5 is a liberal number - 2 tries typically works.
CONNECTION_TRIES = 5

DBG_REPORT = True  # Whether to print a summary of the sync
DBG_ERROR  = True  # Whether to print errors
DBG_WARN   = True  # Whether to print warnings
DBG_VERB   = True  # Whether to print a summary of every transaction

### END CONFIGURATION OPTIONS ###

SHELL_ALIASES = {'adb': ADB,
                 'galaxy': '%s -d' % ADB, # Alias for sending commands to phone
                 'restart': '%s %s ; %s %s' %
                 (ADB, 'kill-server', ADB, 'start-server')}


DEVICE_STATES = collections.defaultdict(bool)
DEVICE_STATES.update({
    "offline": False,
    "device": True,
    "unauthorized": False,
    "no device": False,
})

# Parses the serial numbers and states returned by "adb devices"
DEVICE_REPORT_PATTERN = "\n([0-9\-a-zA-Z]+)\t(%s)" % (
    '|'.join(DEVICE_STATES.keys()))

# Shell interface - see shell.py. Global here but initialized in setup()
SH = None

def report(s):
    if DBG_REPORT:
        prints.stdout(s+'\n')

def warn(s):
    if DBG_WARN:
        prints.stdout(s+'\n')

def error(s):
    if DBG_ERROR:
        prints.stderr(s+'\n')

def log(s):
    if DBG_VERB:
        prints.stdout(s+'\n')

def i_to_g(s):
    """
    Convert iTunes path to Galaxy filesystem location.
    Technically this could fail if you had some weird
    artist/album/song names, but if it did it would at
    least fail consistently.
    """
    return s.replace(ITUNES_LIBRARY, GALAXY_LIBRARY)
def g_to_i(s):
    return s.replace(GALAXY_LIBRARY, ITUNES_LIBRARY)

def num_attached_devices():
    """ Issue 'adb devices' command to find the number of connected devices """
    res = SH.cmd('adb devices')
    devices = re.findall(DEVICE_REPORT_PATTERN, res)
    log = '\n'.join('Device #[%s] state: %s' %(serial,state) for
                       serial, state in devices)
    status = None if len(devices) != 1 else DEVICE_STATES[devices[0][1]]
    return len(devices), log, status

def check_num_devices():
    """
    Try to get a listing of devices, and return True if there's exactly 1.
    """
    num_devices, log, status = num_attached_devices()
    tries = CONNECTION_TRIES
    while num_devices <= 0:
        if tries > 0:
            warn('Could not find your android device. Trying again...')
        elif tries == 0:
            report('Could not find your android device. Aborting')
            return False
        tries -= 1
        time.sleep(2)
        SH.cmd('restart')
        time.sleep(2) # Give daemon some time to boot up
        num_devices, log, status = num_attached_devices()

    if num_devices > 1:
        error('Too many connected android devices - aborting.')
        error(log)
        return False
    return True

def check_device_state():
    num_devices, log, status = num_attached_devices()
    tries = CONNECTION_TRIES
    while not status:
        if tries > 0:
            warn('Device not online. Trying again.')
        elif tries == 0:
            error('Device is not online. Aborting.')
            return False
        tries -= 1
        time.sleep(2)
        SH.cmd('restart')
        time.sleep(2)
        num_devices, log, status = num_attached_devices()
    return True


def check_exists(string, flag):
    path = shell.escape(string)
    cmd = "if [ %s %s ]; then echo 'Exists'; else echo 'Not found'; fi" % (
        flag, path)
    command = 'galaxy shell "%s"' % cmd
    aliased = SH.apply_aliases(command)
    res = SH.cmd(command)
    if 'Exists' in res:
        return True
    elif 'Not found' in res:
        return False
    else:
        error("Invalid result from command %s" % aliased)
        error(res)

def g_has_dir(dirname):
    return check_exists(dirname, '-d')

def g_has_file(filename):
    return check_exists(filename, '-f')

def g_create_dir(dirname):
    res = SH.cmd('galaxy shell mkdir %s' % shell.escape(dirname))
    if not g_has_dir(dirname):
        error("Failed to create directory: %s" % dirname)
        error(SH.apply_aliases('galaxy shell mkdir %s' % shell.escape(dirname)))
        error(res)
    else:
        log("Successfully created directory: %s" % dirname)

def push_to(i_fname, g_dirname, g_filename):
    i_fname = shell.escape(i_fname)
    g_dirname = shell.escape(g_dirname)
    res = SH.cmd('galaxy push %(i_fname)s %(g_dirname)s' % locals())
    if not g_has_file(g_filename):
        error("Failed to push file: %s" % g_filename)
        error(SH.apply_aliases('galaxy push %(i_fname)s %(g_dirname)s' % locals()))
        error(res)
    else:
        log("Successfully pushed %s to %s.\n" % (i_fname, g_dirname))

def setup():
    if not os.path.exists(ITUNES_LIBRARY):
        error('Could not find itunes library: %s' % ITUNES_LIBRARY)
        return False
    if not os.path.exists(ADB):
        error('Could not find adb - maybe the location of your Android SDK changed?')
        error('adb = %s' % adb)
        return False
    global SH ; SH = shell.Shell(aliases=SHELL_ALIASES)
    SH.cmd('restart')
    return check_num_devices() and check_device_state()

def sync_music():
    if not setup():
        exit(1)
    moved = 0
    for root, dirs, files in os.walk(ITUNES_LIBRARY):
        groot = i_to_g(root)
        if not g_has_dir(groot):
            g_create_dir(groot)
        for i_filename in (os.path.join(root, fbase) for fbase in files):
            if os.path.basename(i_filename).startswith('.'): continue
            g_filename = i_to_g(i_filename)
            if not g_has_file(g_filename):
                push_to(i_filename, groot, g_filename)
                moved += 1
            else:
                log("[%s] already on device" % g_filename)
    if moved > 0:
        report('Transfered %d music files from iTunes to Galaxy.' % moved)


if __name__ == '__main__':
    sync_music()
