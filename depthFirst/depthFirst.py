#!/opt/local/bin/python2.7

from argparse import ArgumentParser
import warnings # TODO: search for the warning
import numpy
import time
import multiprocessing
import ctypes
from itertools import izip
from numpy import float64 as float



def intra_cluster(cluster):
    '''
    return the intra cluster measure of a cluster.
    '''
    if not cluster:
        return float(0)
    std=numpy.std(numpy.array(cluster),0)
    return sum(std*std)*len(cluster)


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
        self.dimY = dimY #dimY is the number of rows of the matrix
        self.dimX=dimX #dimX is the number of columns of the matrix
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

    def inter_cluster(self,clusters):
        '''
        return the inter cluster measure of a partition.
        clusters is a list of indicator functions, e. g.
        clusters[i] is a vector of 0 and 1's such that if
        self.data[j] in C_i iff clusters[i][j] == 1.
        To save just a litte of memory, the length of clusters is
        going to be k-1. The points in C_{k-1} are the points that are
        not in any of the other clusters. It is nice to notice that
        the mass centers are important, the intra_cluster measure
        depends heavily on the intra_cluster measure and it is not
        difficult to find examples where the intracluster measure is
        smaller taking "fake" centroids.
        '''
        partition = []
        dist = float(0)
        for cluster in clusters:
            part = []
            for p, i in izip (self.data, cluster):
                if i>0:
                    part.append(p)
            dist += intra_cluster(part)
        part = []
        for d in izip(self.data,*clusters):
            if not any(i>0 for i in d[1:]):
                part.append(d[0])
        dist += intra_cluster(part)
        return dist

class Partition(object):
    def __init__(self, intercluster, l ):
        self.intercluster = intercluster
        self.l = l
    def adyacents(self):
        k = len(self.l)
        for i in range(k):
            result = []
            for k,l1 in enumerate(self.l):
                result.append(l1+[1 if k==i else 0])
            yield result
    def __cmp__(self, other):
        return cmp(self.intercluster, other.intercluster)


def DepthFirst(d,n,k, o= None):
    """
    Try all possible clusters with minimum memory
    Arguments:
    - `d`: an object with of type dataset
    - `n`: number of points
    - `k`: number of clusters
    """
    if not o:
        partition = [[1]]
        for i in range(k-1):
            partition.append([0])
        o = Partition(d.inter_cluster(partition), partition)
    if len(o.l[0])>= n:
        return o.intercluster

    return min(DepthFirst(d,n,k,Partition(d.inter_cluster(p), p)) for p in o.adyacents())
       
                
def testMode():
    "DepthFirst"
    nproc=1
    points=range(5,10)
    dims=[2]
    clusters = [2]
    numpy.seterr(all='raise')
    for dim in dims:
        for point in points:
            for k in clusters:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    d=dataset(dim,point,'linux.txt',processes = nproc)                
                t1=time.time()
                min_o=DepthFirst(d,point,k)
                opttime=time.time()-t1
                print '%d,%d,%d,%.6f,%.6f'%(k,dim, point, opttime,min_o)
                




                
if __name__=='__main__':
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
    parser.add_argument('-k','--clusters', help='number of clusters, 2 are used by default', required=False)
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
        if args['clusters']:
            k=int(args['clusters'])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            d=dataset(dim,point,'../dataset/linux.txt',processes = nproc)                
        t1=time.time()
        min_o=DepthFirst(d,point,k)
        opttime=time.time()-t1
        print '%d,%d,%d,%.6f,%.6f'%(k,dim, point, opttime,min_o)
                

