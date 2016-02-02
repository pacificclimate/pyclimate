#!/usr/bin/env python

import os
import math
import multiprocessing
import time
import timeit

from tempfile import mkstemp

import netCDF4
import numpy as np
import time

class Consumer(multiprocessing.Process):
    
    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill means we should exit
                # print '%s: Exiting' % proc_name
                break
            # print '%s: %s' % (proc_name, next_task)
            answer = next_task()
            self.result_queue.put(answer)

class TaskMinMax(object):
    def __init__(self, f, var, i):
        self.f = f
        self.var = var
        self.i = i

    def __call__(self):
        nc = netCDF4.Dataset(self.f, 'r')
        var = nc.variables[self.var]
        slice_ = var[self.i,:,:]
        amin = np.amin(slice_)
        amax = np.amax(slice_)
        return (amin, amax)

    def __str__(self):
        return '%s zstep %s' % (self.var, self.i)

def multiprocess_minmax(filename, var):
    tasks = multiprocessing.Queue()
    results = multiprocessing.Queue()

    # Start consumers
    num_consumers = 8
#    print 'Creating %d consumers' % num_consumers
    consumers = [ Consumer(tasks, results)
                  for i in xrange(num_consumers) ]
    for w in consumers:
        w.start()
    
    # Enqueue jobs
    nc = netCDF4.Dataset(filename, 'r')
    zlen = nc.variables[var].shape[0]
    nc.close()

    for i in xrange(zlen):
        tasks.put(TaskMinMax(filename, var, i))
    
    # Add a poison pill for each consumer
    for i in xrange(num_consumers):
        tasks.put(None)
    
    # Start printing results
    r = []
    while zlen:
        result = results.get()
        r.append(result)
        # print 'Result:', result
        zlen -= 1

    return (min(x[0] for x in r), max(x[1] for x in r))

def singlethread_minmax(filename, var):
    nc = netCDF4.Dataset(filename, 'r')
    var = nc.variables[var]
    print(type(var))
    _min = float('inf')
    _max = float('-inf')
    amin = np.amin(var[:])
    amax = np.amax(var[:])
    return (amin, amax)
    

if __name__ == '__main__':
    _, filename = mkstemp(suffix='.nc', dir=os.getcwd())
    shape = (8, 1024, 1024)
    nc = netCDF4.Dataset(filename, 'w')
    nc.createDimension('lat', shape[2])
    nc.createDimension('lon', shape[1])
    nc.createDimension('time', shape[0])
    some_var = nc.createVariable('variable_name','f4',('time', 'lat', 'lon'))

    for t in range(shape[0]):
        some_var[t,:,:] = np.random.randn(shape[1], shape[2])
    nc.close()
    exit()
    ### TEST WITH python-netCDF ###

    print(netCDF4.__file__)

    t0 = time.time()
    multiprocess_minmax(filename, 'variable_name')
    time_multi = time.time() - t0
    
    t0 = time.time()
    singlethread_minmax(filename, 'variable_name')
    time_single = time.time() - t0

    print("Singleprocess time: {}".format(time_single))
    print("Multiprocess time: {}".format(time_multi))
    print("Speedup: {}".format(time_single/time_multi))

    ### TEST WITH h5netcdf ###

    import h5netcdf.legacyapi as netCDF4

    print("TESTING WITH H5PY {}".format(netCDF4.__file__))

    t0 = time.time()
    multiprocess_minmax(filename, 'variable_name')
    time_multi = time.time() - t0
    
    t0 = time.time()
    singlethread_minmax(filename, 'variable_name')
    time_single = time.time() - t0

    print("Singleprocess time: {}".format(time_single))
    print("Multiprocess time: {}".format(time_multi))
    print("Speedup: {}".format(time_single/time_multi))


#    timeit.timeit("multiprocess_minmax(filename, 'variable_name')", "import multiprocess_minmax", number=10)
#    timeit.timeit("singlethread_minmax(filename, 'variable_name')", number=10)

    os.remove(filename)
