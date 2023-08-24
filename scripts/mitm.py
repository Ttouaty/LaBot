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
from datetime import datetime

FILTER = "port == 5555 || port == 443"

class DofusWaiter(object):

    def waitForDofus(self, onDofusLaunched):
        self.callback = onDofusLaunched;
        self.device = frida.get_local_device(); 
        self.device.on("child-added", lambda child: self.onNewChild(child))

        launcherPID = self.getPID_FromProcess("Ankama Launcher.exe");
        print("Ankama launcher PID is => "+str(launcherPID))
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
    try:
        hook(pid, args.port, FILTER)
        print("Hooked to => %s with port => %s" % (pid, args.port))
    except Exception as e:
        print("That's some error my dude")
        raise e;

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
        date =str(datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss"));
        dumpFilePath = args.dump_to if args.dump_to else Path(__file__).absolute().parents[1] /"LOGS" / f"serverLog - {date}.txt"
        dumper = Dumper(dumpFilePath)

        def my_callback(coJeu, coSer):
            global bridges

            # bridge = InjectorBridgeHandler(coJeu, coSer, dumper=dumper)
            bridge = TTCustomBridgeHandler(coJeu, coSer, dumper=dumper)
            bridges.append(bridge)
            bridge.loop()

        # to interrupt : httpd.shutdown()
        # httpd = start_proxy_server(my_callback, "crashhere")
        httpd = start_proxy_server(my_callback, args.port)

    # if args.launch or args.attach:
    waiter = DofusWaiter()
    waiter.waitForDofus(onDofusLaunched)

    if not sys.flags.interactive:
        print("Waiting for dofus to start")
        print("Press - Ctrl+C - to close the server anytime")
        print("You can also close this window to close the server")
        try:
            sys.stdin.read()  # infinite loop
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