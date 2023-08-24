#!/usr/bin/env python3



import frida
import threading
import sys
import os
import argparse
from pathlib import Path
from subprocess import Popen

# include path to labot
sys.path.append(Path(__file__).absolute().parents[1].as_posix())

from labot.logs import logger
from labot.mitm.bridge import *

from fritm import hook, start_proxy_server
import subprocess

# FILTER = "port == 5555 || port == 443"
FILTER = "port == 5555 || port == 443"



class DofusWaiter(object):

    def waitForDofus(self, onDofusLaunched):
        self.callback = onDofusLaunched;
        self.device = frida.get_local_device(); 
        self.device.on("child-added", lambda child: self.onNewChild(child))

        launcherPID = self.getPID_FromProcess("Ankama Launcher.exe");
        # print("PID is => "+str(launcherPID))
        self.dofusSession = self.device.attach(launcherPID)
        self.dofusSession.enable_child_gating()
        self.dofusSession.resume();

    def onNewChild(self, child):
        # print("Got child => "+str(child))
        if "Dofus" in child.path:
            self.dofusSession.resume();
            self.dofusSession.disable_child_gating()
            print("DOFUS DETECTED!")
            self.callback(child.pid)



    def on_message(self, message, data):
        print ("[%s] -> %s" % (message, data))

    # windows only - cheh
    def getPID_FromProcess(self, process_name):
        output = subprocess.check_output(["tasklist", "/FO","CSV", "/FI", f'imagename eq {process_name}'], text=True)
        lines = output.strip().replace('\"', "").split('\n')[1:] # remove first because header (image name, pid, ...)
        for line in lines:
            info = line.split(",")
            if info[1] is not None:
                return int(info[1])
        return None


def onDofusLaunched(pid):
    print("I GOT THE DOFUS ! => "+str(pid))

    try:
        hook(pid, args.port, FILTER)
        print("Hooked to => %s with port => %s" % (target, args.port))
    except Exception as e:
        print("That's some error my dude")
        raise e;


def launch_dofus():
    """to interrupt : dofus.terminate()"""
    return # can't launch dofus anymore because update
    platform = sys.platform
    if platform == "darwin":
        path = "/Applications/Dofus.app/Contents/Data/Dofus.app/Contents/MacOS/Dofus"
    elif platform == "win32":
        appdata = os.getenv("appdata")
        parent = os.path.dirname(appdata)
        # path = parent + "\\Local\\Ankama\\zaap\\dofus\\Dofus.exe"
        path = parent + "\\Local\\Ankama\\Dofus\\Dofus.exe"
    else:
        assert False, (
            "Your platform (%s) doesn't support automated launch yet" % sys.platform
        )
    return Popen(path)


def make_parser():
    parser = argparse.ArgumentParser(
        description="Start the proxy",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("--server", action="store_true", help="Run a proxy server")
    parser.add_argument(
        "--port", type=int, default=8080, help="Listening port of the proxy server"
    )
    parser.add_argument(
        "--dump-to", type=Path, default=None, help="Capture file (pickle format)"
    )
    # parser.add_argument(
    #     "--launch", action="store_true", help="Launch a new hooked Dofus instance"
    # )
    parser.add_argument(
        "--attach", action="store_true", help="Attach to an existing Dofus instance"
    )
    parser.add_argument(
        "--pid",
        type=int,
        default=None,
        help="PID of the Dofus process, only required if there are multiple instances already launched",
    )
    parser.add_argument("--verbose", default="INFO", help="Logging level")
    return parser

httpd = None
if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args()

    logger.setLevel(args.verbose)

    if not args.server:
        assert args.dump_to is None, "dump-to not used"
    if not args.attach:
        assert args.pid is None, "pid is not used"
    if args.server:
        bridges = []
        print("Launching server")

        dumper = Dumper(args.dump_to) if args.dump_to else None

        def my_callback(coJeu, coSer):
            print("Change this line to implement own Bridge handler - totos")
            global bridges


            bridge = InjectorBridgeHandler(coJeu, coSer, dumper=dumper)
            bridges.append(bridge)
            bridge.loop()

        # to interrupt : httpd.shutdown()
        # httpd = start_proxy_server(my_callback, "crashhere")
        httpd = start_proxy_server(my_callback, args.port)

    # if args.launch:
    #     dofus = launch_dofus()
    #     target = dofus.pid

    if args.attach:
        target = args.pid
        if target is None:
            if sys.platform == "darwin":
                target = "dofus"
            elif sys.platform == "win32":
                target = "Dofus.exe"
            else:
                assert False, "Your platform requires a pid to attach"

    # if args.launch or args.attach:
    waiter = DofusWaiter()
    waiter.waitForDofus(onDofusLaunched)

    # if args.attach:
        # try:
        #     hook(target, args.port, FILTER)
        #     print("Hooked to => %s with port => %s" % (target, args.port))
        # except Exception as e:
        #     print("You need to launch the server before starting dofus, else we can't hook to the connect function!")
    if not sys.flags.interactive:
        print("Launched")
        try:
            sys.stdin.read()  # infinite loop
            pass
        except KeyboardInterrupt as e:
            if httpd is not None:
                httpd.shutdown()
                httpd.server_close()
                print("# Closed server\n")
















#python .\mitm.py --server  --dump-to C:\Projects\LaBot\LOGS\firstLog.txt --attach --verbose INFO

#                              Foreign adress 26116
# dofus adress check 1 =>  127.0.0.1:64619       : pid    24736
# dofus adress check 1 =>  127.0.0.1:64666       : pid    540

"""

Problem => Connect function isn't called from dofus => can't redirect
            force reco? 
            intercept before first connection?
            use send to force reconnection?
            Make Ankama launcher launch dofus and auto attach ?



"""