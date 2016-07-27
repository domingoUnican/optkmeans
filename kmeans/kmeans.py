# -*- coding: cp1252 -*-
from scipy.cluster.vq import *
import numpy as np
import random
import itertools
import time
from argparse import ArgumentParser

def loadData(filename,dimX,dimY):
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
    return np.array(data)

def intra_cluster(cluster):
    '''
    return the intra cluster measure of a cluster.
    '''
    if not cluster:
        return float(0)
    std=np.std(np.array(cluster),0)
    return sum(std*std)*len(cluster)

def inter_cluster(data,clusters,k):
    partitions=[[] for i in range(k)]
    for i,x in enumerate(clusters):
        partitions[x].append(data[i])
    min_dist=0
    for p in partitions:
        min_dist+=intra_cluster(p)
    return min_dist
    
def testMode(n_init):
    "kMeans"
    k=2
    points=range(5,10)
    dims=[2]
    for dim in dims:
        for point in points:
            X=loadData('../dataset/linux.txt',dim,point)
            t1=time.time()
            min_dist=np.infty
            for i in range(n_init):
                centroid,label=kmeans2(X, k, minit='points', missing='warn')
                m=inter_cluster(X,label,k)
                if m<min_dist:
                    min_dist=m
            opttime=time.time()-t1
            print '%d,%d,%d,%.6f,%.6f'%(k,dim,point,opttime,min_dist)
                


if __name__=='__main__':
    n_init=10
##    testMode(n_init)
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
        X=loadData('../dataset/linux.txt',dim,point)
        t1=time.time()
        min_dist=np.infty
        for i in range(n_init):
            centroid,label=kmeans2(X, k, minit='points', missing='warn')
            m=inter_cluster(X,label,k)
            if m<min_dist:
                min_dist=m
        opttime=time.time()-t1
        print '%d,%d,%d,%.6f,%.6f'%(k,dim,point,opttime,min_dist)
                





