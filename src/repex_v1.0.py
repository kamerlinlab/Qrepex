# One line to give the program's name and a brief idea of what it does.
# Copyright (C) 2021 Sebastian Brickel
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the 
# FreeSoftware Foundation; either version 2 of the License, or (at your 
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT 
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for 
# more details.
#
# You should have received a copy of the GNU General Public License along 
# with this program; if not, write to the Free Software Foundation, Inc., 59 
# Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os
import sys
import time
import numpy as np


# Input file processing.
if len(sys.argv) == 4:
    restart = 0

elif len(sys.argv) == 5:
    restart = int(sys.argv[4])

else:   
    sys.exit(sys.argv[0] + ': Expecting four command line argument -- input ',
             'basefile name; the number of files; number of runs')

inFile = sys.argv[1]
numFiles = int(sys.argv[2])
numRuns = int(sys.argv[3])


# Identify number of sockets (NUMA islands).
numSockets =  int(os.popen(
                  'cat /proc/cpuinfo | grep "physical id" | sort -u | wc -l'
                  ).read())
# Identify total number of CPUs.
numProc = open('/proc/cpuinfo').read().count('processor\t:')
# Identify available number of CPUs.
try:
    numProcAvail = int(os.popen('echo $SLURM_NTASKS').read())
except:
    numProcAvail = int(os.popen('echo $SLURM_JOB_CPUS_PER_NODE').read())

# Identify total number of Nodes.
numNodes = int(os.popen('echo $SLURM_NNODES').read())


# First Q run, must be sequential.
def initial_run_Q():
    for i in range(0,numFiles):
        process = "".join(['mpirun --np ',str(numProcAvail),' Qdyn6p ',
                          inFile,str(i),'.inp > ',inFile,str(i),'.log'])
        os.system(process)


# Run Q. Optimised per infastructure.
def run_Q(num):
    if numProcAvail < numProc:
        for i in range(0,numFiles):
            rename_dcd(i,num-1)
            rename_en(i,num-1)
            process = "".join(['mpirun --np ',str(numProcAvail),' Qdyn6p ',
                              inFile,str(i),'.inp > ',inFile,str(i),'.log'])
            os.system(process)

    else:
        num_sockets = 1
        for i in range(0,numFiles):
            rename_dcd(i,num-1)
            rename_en(i,num-1)
            if num_sockets < numSockets*numNodes:
                process = "".join(['mpirun --np ',str(int(numProc/numSockets)),
                                  ' Qdyn6p ',inFile,str(i),'.inp > ',inFile,
                                  str(i),'.log &'])
                os.system(process)
                num_sockets += 1
            else:
                process = "".join(['mpirun --np ',str(int(numProc/numSockets)),
                                  ' Qdyn6p ',inFile,str(i),'.inp > ',inFile,
                                  str(1),'.log'])
                os.system(process)
                num_sockets = 1


# Switch restart files. This is the replica exchange step.      
def exchange(start, end):
    for i in range(start, end, 2):
        filename = "".join([inFile+str(i+1)+'.re'])
        os.rename(filename,'restart.temp')

        filename = "".join([inFile+str(i)+'.re'])
        filename2 = "".join([inFile+str(i+1)+'.re'])
        os.rename(filename,filename2)

        filename = "".join(['restart.temp'])
        filename2 = "".join([inFile+str(i)+'.re'])
        os.rename(filename,filename2)


# Rename dcds, in order to keep all of the.    
def rename_dcd(i, num):
    filename = "".join([inFile,str(i),'.dcd'])
    filename2 = "".join([inFile,str(i),'_',str(num),'.dcd'])
    os.rename(filename,filename2)

# Rename en files, in order to keep all of the.    
def rename_en(i, num):
    filename = "".join([inFile,str(i),'.en']) 
    filename2 = "".join([inFile,str(i),'_',str(num),'.en'])
    os.rename(filename,filename2)


# Combine en files for analysis     
def combine_en(i, num):
    filename = "".join([inFile,str(i),'.en'])
    filename2 = "".join([inFile,str(i),'_',str(num),'.en'])
    process = "".join(['dd bs=36 skip=1 if=',filename2,' of=trimmed.dump'])
    os.system(process)
    process = "".join(['cp ',filename,' en.temp'])
    os.system(process)
    process = "".join(['cat en.temp trimmed.dump > ',filename])
    os.system(process)


# Main function
def main():
    # Check if input files exist.
    for i in range(0,numFiles):
        try:
            filename = "".join([inFile,str(i),'.inp'])
            f = open(filename, 'r')
        except FileNotFoundError:
            sys.exit('Input files not found: '+inFile+str(i)+'.inp')
            f.close()

    # Check if number of files is equal or odd. This is important for the 
    # exchange step.
    try:
        assert numFiles % 2 == 0
    except:
        numExchangeOdd = numFiles-1
        numExchangeEven = numFiles
    else:
        numExchangeOdd = numFiles
        numExchangeEven = numFiles-1

    # Main program, run Q
    if restart == 0:
        initial_run_Q()
        exchange(0, numExchangeOdd)
        num = 2

    else:
        num = restart

    while num <= numRuns:
        run_Q(num)
        # Wait for all Qdyn jobs to finish
        running = os.popen('ps -u $USER | grep Qdyn6p | sed -n $=').read()
        print(os.popen('ps -u $USER').read())
        while (not running) == False:
            time.sleep(30)
            running = os.popen('ps -u $USER | grep Qdyn6p | sed -n $=').read()
            print(os.popen('ps -u $USER | grep Qdyn6p | sed -n $=').read())
        # Check if total number of files is even for exchange step
        try:
            assert num % 2 == 0
        except:
            exchange(0, numExchangeOdd)
        else:
            exchange(1, numExchangeEven)
        num += 1

    # Combine .en files for analysis: NOT NEEDED
    #for i in range(0,numFiles):
    #    for num in range(1,numRuns):
    #        combine_en(i, num)


if __name__ == "__main__":
    main()

