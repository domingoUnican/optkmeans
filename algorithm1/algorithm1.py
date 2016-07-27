#!/opt/local/bin/python2.7
""" In order to execute the algorithm, the file
enumaration.py needs to be in the same folder"""
from argparse import ArgumentParser
import warnings # TODO: search for the warning
import numpy
from numpy import float64 as float
from scipy import array
from itertools import izip, product, combinations
import ctypes
import multiprocessing
from multiprocessing import Process
from multiprocessing import Queue
from enumeration import alternate, enumerate_list
import time



def signGet(p, signs , supp_vector, k):
    '''
    This function checks in which side of the hyperplane h*x=0
    lies point p.
    If it is on one side, it returns 1 or -1. If it is in the
    hyperplane, then returns  all possible signs.
    '''
    dX = len(p)
    result = []
    partials = []
    for i in range(k-1):
        ext_p =  [0]*(i*dX+k-1)+list(p)+[0]*((k-2-i)*dX)  
        ext_p[i] = -0.5
        partials.append(array(ext_p))
    sol,res,rank,s = numpy.linalg.lstsq(supp_vector, signs)
    booleans = []
    for p_m in partials:
        booleans.append(numpy.dot(p_m.T,sol)<=0)
    put = 1 if all(booleans) else 0
    result.append(put)
    for i in range(0,k-2):
        if put < 1:
            booleans = [numpy.dot(partials[i].T,sol)>0]
            for j in range(i+1,k-1):
                booleans.append(numpy.dot((partials[j]-partials[i]).T, sol)<=0)
            put = 1 if all(booleans) else 0
            result.append(put)
        else:
            result.append(0)
    if 1 in result:
        result.append(0)
    else:
        result.append(1)
    return result


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
        self.q = Queue()
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
        depends heavily in the intra_cluster measure and it is not
        difficult to find examples, where the intracluster measure is
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


    def find_optimum_launch(self,k):
        '''
        This function launch several processes to calculate the
        optimum partition of a set in two clusters
        '''
        p_list = []
        dX = self.dimX
        dY = self.dimY
        results = []
        for p in self.data:
            partials = []
            for i in range(k-1):
                temp =[0]*(k-1+i*dX)+list(p)+[0]*((k-2-i)*dX)
                temp[i] = - 0.5
                partials.append(array(temp))
            results += partials
            for l in combinations(partials,2):
                results.append(l[1]- l[0])
        self.data_k = array(results)
        for i in xrange(self.processes):
            p_list.append(Process(target=self.find_optimum,
                                  args = (i,k)))
        [p.start() for p in p_list]
        [p.join() for p in p_list]


    def find_optimum(self, pid, k):
        '''
        This function finds the minimum when the data is split into k
        different clusters
        '''
        min_dist = numpy.infty
        min_par = []
        m=(self.dimX+1)*(k-1)
        total_proc = self.processes
        for l in range(1,m+1):
            if l>1:
                enum = enumerate_list(self.data_k,l)
            else:
                enum = ([p] for p in self.data_k)            
            for supportVectors in alternate(enum,period=total_proc,phase=pid):
                for signs in product([0.5,0,-0.5],repeat=l):
                    partition_0 = [signGet(p, numpy.array(signs), numpy.array(supportVectors),k) for p in self.data]
                    partition = []
                    for i in range(k):
                        partition.append([p[i] for p in partition_0])
                    new_dist = self.inter_cluster(partition)
                    if min_dist>new_dist:
                        min_dist = new_dist
        self.q.put(min_dist)




def testMode():
    "Algorithm 1"
    nproc=15
    points=range(5,10)
    dims=[2]
    clusters = [2]
    numpy.seterr(all='raise')
    for dim in dims:
        for point in points:
            for k in clusters:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    d=dataset(dim,point,'../dataset/linux.txt',processes = nproc)                   
                t1=time.time()
                d.find_optimum_launch(k)
                opttime=time.time()-t1
                min_dist = numpy.infty
                while not d.q.empty():
                    dist=d.q.get()
                    if dist < min_dist:
                        min_dist = dist
                print '%d,%d,%d,%.6f,%.6f'%(k,dim,point,opttime,min_dist)
                
                




                
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
            d=dataset(dim,point,filen,processes = nproc)                
        t1=time.time()
        d.find_optimum_launch(k)
        min_dist = numpy.infty
        while not d.q.empty():
            dist=d.q.get()
            if dist < min_dist:
                min_dist = dist
        opttime=time.time()-t1
        print '%d,%d,%d,%.6f,%.6f'%(k,dim, point, opttime,min_dist)


