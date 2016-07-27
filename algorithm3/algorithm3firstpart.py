#!/opt/local/bin/python2.7
"""
This algorithm is basically Algorithm 2 in which instead of printing the
global minimum, we save all feasible signs in a file
In order to run it, the file enumeration.py needs to be in
the same folder
"""
from argparse import ArgumentParser
import warnings # TODO: search for the warning
import numpy
from numpy import float64 as float
import ctypes
import multiprocessing
from multiprocessing import Process
from multiprocessing import Queue
from itertools import izip, product
from enumeration import alternate, enumerate_list
import cPickle as pickle
import os

def ensure_dir(d):
    '''
    creates a directory if id does not exist
    '''
    if not os.path.exists(d):
        os.makedirs(d)

        
def signGet(p, solution):
    '''
    This function checks in which side of the hyperplane h*x=0
    lies point p.
    If it is on one side, it returns 1 or -1. If it is in the
    hyperplane, then returns  all possible signs.
    '''
    if numpy.dot(p.T,solution)<=0:
        return 1
    return 0



class dataset:

    def __init__(self, dimX, dimY, filename='', processes=1):
        '''
        Constructor of the class, only stores the data
        '''
        #We just instantiate a shared matrix for all the processes
        #Data and combinations should be shared to avoid replication
        #between processes ~ time and memory overhead.
        #This first approach is not very optimal,
        #combinations may be generated in parallel for each
        #process. TODO

        self.q = Queue()
        self.dimY = dimY #dimY is the number of rows of the matrix
        self.dimX=dimX #dimX is the number of columns of the matrix
        self.m=dimX+2
        self.processes = processes
        shared_array_base = multiprocessing.Array(ctypes.c_double, dimX*dimY)
        shared_array = numpy.ctypeslib.as_array(shared_array_base.get_obj())
        shared_array = shared_array.reshape(dimY, dimX)
        self.data = shared_array
        if not filename:
            numpy.random.seed(10)
            for j in xrange(dimY):
                for i in xrange(dimX):
                    self.data[j][i]=numpy.random.randn()
        else:
            data=[]
            count=0
            for row in open(filename,'r'):
                if count<dimY:
                    line=[float(n) for n in row.split(',')[:dimX]]
                    if line not in data:
                        data.append(line)
                        count+=1                        
                else:
                    break
            for j in xrange(dimY):
                for i in xrange(dimX):
                    self.data[j][i]=data[j][i]
        
        self.data_k=[numpy.array([-0.5]+list(p)) for p in self.data]




    def find_optimum_two_launch(self):
        '''
        This function launch several processes to calculate the
        optimum partition of a set in two clusters
        '''
        p_list = []
        for i in xrange(self.processes):
            p_list.append(Process(target=self.find_optimum_two,args = (i,)))       
        [p.start() for p in p_list]
        [p.join() for p in p_list]


    def find_optimum_two(self,pid,):
        '''
        This function finds the minimum when the data is split into 2
        different clusters
        '''
        for l in range(1,self.m):
            if l>1:
                enum = enumerate_list(self.data_k,l)
            else:
                enum = ([p] for p in self.data_k)            
            for supportVectors in alternate(enum,period=self.processes,phase=pid):
                for signs in product([0.5,0.0,-0.5],repeat=l):
                    sol,res,rank,s = numpy.linalg.lstsq(numpy.array(supportVectors), numpy.array(signs))
                    partition = [signGet(p, sol) for p in self.data_k]                    
                    with open('temp/output%s_%s.txt'%(self.dimX,self.dimY),'a') as f:
                        pickle.dump(partition,f)
                   
 

def testMode():
    "Algorithm 3 first part, k=2, print signs"
    nproc=15
    points=range(5,10)
    dims=[2]
    k=2
    numpy.seterr(all='raise')
    for dim in dims:
        for point in points:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                d=dataset(dim,point,'../dataset/linux.txt',processes = nproc)                   
            d.find_optimum_two_launch()
            all_p=set()
            with open('temp/output%s_%s.txt'%(d.dimX,d.dimY)) as f:
                while 1:
                    try:
                        part=pickle.load(f)
                        all_p.add(''.join([str(j) for j in part]))                
                    except Exception as e:
                        break
            
            with open('temp/output%s_%s.txt'%(d.dimX,d.dimY),'w') as f:
                cond=True
                for p in all_p:
                    if cond:
                        f.write(','.join([c for c in p]))
                        cond=False
                    else:
                        f.write('\n'+','.join([c for c in p]))
                        


            




                
if __name__=='__main__':
    ensure_dir('temp')
##    testMode()
    filen="../dataset/linux.txt"    
    dim = 2
    point = 10
    nproc = 4
    k=2
    d_s = 'Calculate the optimum k-means centroids for a given dataset'
    parser = ArgumentParser(description=d_s)
    parser.add_argument('-f','--file', help='Filename of dataset, the default name is "linux.txt"', required=False)
    parser.add_argument('-d','--dim', help='number of features in the dataset, 2 are used by default', required=False)
    parser.add_argument('-n','--points', help='number of lines in the dataset,\
    more files in the dataset are not considered, the default is 10',required=False)
    parser.add_argument('-p','--procs', help='number of processes to be used, 4 are used by default', required=False)
    parser.add_argument('-t','--testmode', help='run a benchmark', required=False)
    args = vars(parser.parse_args())
    if args['testmode']=='b':
        testMode()
    else:
        if args['file']:
            filen=args['file']
        if args['dim']:
            dim=int(args['dim'])
        if args['points']:
            point=int(args['points'])
        if args['procs']:
            nproc=int(args['procs'])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d=dataset(dim,point,filen,processes = nproc)                
        d.find_optimum_two_launch()
        all_p=set()
        with open('temp/output%s_%s.txt'%(d.dimX,d.dimY)) as f:
            while 1:
                try:
                    part=pickle.load(f)
                    all_p.add(''.join([str(j) for j in part]))                
                except Exception as e:
                    break
        
        with open('temp/output%s_%s.txt'%(d.dimX,d.dimY),'w') as f:
            cond=True
            for p in all_p:
                if cond:
                    f.write(','.join([c for c in p]))
                    cond=False
                else:
                    f.write('\n'+','.join([c for c in p]))


