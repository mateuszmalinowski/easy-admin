#!/usr/bin/env python

import sys, os, time, atexit
from signal import SIGTERM


class Daemon:
    """
    Daemon class.

    Based on the Sander Marechal's code.
    http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python
    """

    def __init__(self, pidfile, 
            stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin=stdin
        self.stdout=stdout
        self.stderr=stderr
        self.pidfile=pidfile

    def daemonize(self):
        """
        Do the UNIX double-fork magic.
        After first forking and decoupling the new process becomes the session
        leader and hence can acquire tty.
        """
        try:
            pid = os.fork()
            if pid > 0:
                # be orphaned by the parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n"%(e.errno, e.strerror))
            sys.exit(1)

        # decouple from the parent
        os.chdir('/home/mmalinow/.daemons')
        os.setsid()
        os.umask(0)

        # do the second fork in order to lift up leadership
        # session leader can still acquire access to tty
        try:
            pid=os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n"%(e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stdin.flush()
        sys.stderr.flush()

        si=file(self.stdin,'r')
        so=file(self.stdout, 'a+')
        se=file(self.stderr, 'a+', 0)

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        atexit.register(self.delpid)
        pid=str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        try:
            pf=file(self.pidfile,'r')
            pid=int(pf.read().strip())
            pf.close()
        except IOError:
            pid=None

        if pid:
            msg="pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(msg % self.pidfile)
            sys.exit(1)

        self.daemonize()
        self.run()

    def stop(self):
        try:
            pf=file(self.pidfile,'r')
            pid=int(pf.read().strip())
            pf.close()
        except:
            pid = None

        if not pid:
            msg="pidfile %s doesn't exist. Daemon not running?\n"
            sys.stderr.write(msg % self.pidfile)
            return

        try:
            while True:
                os.kill(pid,SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err=str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                else:
                    print str(err)
                    sys.exit(1)

    def restart(self):
        self.stop()
        self.start()

    def run(self):
        """
        To override.
        """

