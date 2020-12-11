from config import DEFAULT_HEADERS
from managers import ConnectionManager
from threading import Thread
from utils import FilenameIterator, update_stats, get_args
from urllib.parse import urljoin
import argparse
import string
import itertools
import random
import time
import os

args = get_args()
combinations = (len(args.charset) ** args.length) * len(args.ext)
fname_iter = FilenameIterator(args.charset, args.length,
                              args.ext)

if args.skip:
    if args.skip.isdigit():
        args.skip = int(args.skip)
    
    if isinstance(args.skip, int):
        for _ in range(args.skip):
            next(fname_iter)
    
    elif isinstance(args.skip, str):
        while next(fname_iter) != args.skip:
            pass

class StatsUpdater(Thread):
    def __init__(self, interval=0.10):
        self.interval = interval
        super().__init__()

    def update(self):
        p = (fname_iter.position/combinations * 100) if fname_iter.position else 0 
        update_stats(" | ".join([
            "fbrute",
            f"{fname_iter.position:,} / {combinations:,} ({p:.4f}%)"
        ]))
    
    def run(self):
        while 1:
            self.update()
            time.sleep(self.interval)

class Worker(Thread):
    manager: ConnectionManager
    
    def __init__(self):
        self.new_manager()
        super().__init__()

    def new_manager(self):
        proxy = "http://"+next(args.proxies) if args.proxies else None
        self.manager = ConnectionManager(proxy)

    def do_task(self, filename):
        url = urljoin(args.url, filename)
        method = "HEAD" if args.head else "GET"
        resp = self.manager.request(method, url, headers=DEFAULT_HEADERS)
        
        if resp.status in args.success:
            print("[FOUND]", url)

            if args.outputfile:
                args.outputfile.write(url+"\n")
                args.outputfile.flush()

            if args.download:
                if method == "HEAD":
                    resp = self.manager.request("GET", url, headers=DEFAULT_HEADERS)
                
                fpath = os.path.join(args.download, filename)
                with open(fpath, "wb") as f:
                    f.write(resp.content)
                
                print(f"[SAVED] {fpath} ({len(resp.content)/1024:.2f} KB)")

        elif resp.status in args.ignore:
            pass

        else:
            raise Exception(f"{url}: Unrecognized status code {resp.status}")

    def run(self):
        while 1:
            try:
                filename = next(fname_iter)
            except StopIteration:
                break
            
            while 1:
                try:
                    self.do_task(filename)
                    break
            
                except Exception as exc:
                    if args.debug:
                        print("[ERROR]", exc, type(exc))
                    
                    # switch proxy if available
                    if args.proxies:
                        self.manager.clear()
                        self.new_manager()

def main():
    StatsUpdater().start()
    for _ in range(args.threads):
        Worker().start()

if __name__ == "__main__":
    main()