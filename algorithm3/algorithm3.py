""" In order to execute the algorithm, the file
algortihm3secondpart.exe needs to be in the same folder"""
import subprocess
import time
from argparse import ArgumentParser

def testMode():
    "Algorithm 3"
    nproc=15
    points=range(5,10)
    dims=[2]
    k=3
    for dim in dims:
        for point in points:     
                t1=time.time()
                proc=subprocess.Popen('./algorithm3secondpart.exe ../dataset/linux%s.txt %s %s %s ./temp/output%s_%s.txt '%(dim,point,dim,k,dim,point),
                                      stdout=subprocess.PIPE,shell=True)
                out,err = proc.communicate()
                t1=time.time()-t1
                print ','.join([str(i) for i in [k,dim,point]])+',%.6f,%.6f'%(t1,float(out.strip()))

if __name__=='__main__':
##    testMode()
    filen="../dataset/linux.txt"    
    dim = 2
    point = 10
    nproc = 4
    k=3
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
        t1=time.time()
        proc=subprocess.Popen('./algorithm3secondpart.exe ../dataset/linux%s.txt %s %s %s ./temp/output%s_%s.txt '%(dim,point,dim,k,dim,point),
                              stdout=subprocess.PIPE,shell=True)
        out,err = proc.communicate()
        t1=time.time()-t1
        print ','.join([str(i) for i in [k,dim,point]])+',%.6f,%.6f'%(t1,float(out.strip()))


