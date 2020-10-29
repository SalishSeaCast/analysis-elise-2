import time
import subprocess
import socket
import multiprocessing as mp
import sys
import numpy as np

def busy(x):
    time.sleep(180)
    return x, socket.gethostname()

def main():
    pool=mp.Pool(processes=10)
    data=np.arange(0,10)
    results=[pool.apply_async(busy,args=(x,)) for x in data]
    vals=[p.get() for p in results]
    for el in vals:
        sys.stdout.write(str(el)+'\n')
    sys.stdout.flush()
    return

if __name__ == "__main__":
    main()
