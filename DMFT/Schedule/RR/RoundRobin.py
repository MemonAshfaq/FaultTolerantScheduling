"""
NUS - EE5903 - Real Time Systems

Author - Aspak Rogatiya (A0179741U)

Simulation: Round Robin Algorithm with Fault Tolerance

Task Model:
        Periodic (WCET <= Deadline <= Period)
        All task start to arrive at time 0.
Fault Model:
        MTTF
"""

#===============================================================================
# Imports
#===============================================================================

import fractions
from collections import OrderedDict
import matplotlib.pyplot as plt
import numpy as np

DEADLINEMISS=500
USE=1

#===============================================================================
# A Task class.
#===============================================================================
class Task:
    def __init__(self,name,C,D,P,color):
        self.name = name
        self.C = C
        self.bkpC = C
        self.P = P
        self.D = D
        self.color = color
        self.sc = 0 #shortness component
        self.pc = 0 #priority component
        self.cc = 0 #computed component
        self.csc = 0 #context switch component
        self.bcb = 0 #balanced cpu birst
        self.q = tq #intelligent time slice
        self.inst = 0 #number of instances in hyperperiod
        self.instDone = 0 #number of instances done

    def __str__(self):
        return self.name + "\t" + str(self.bkpC) + "\t" + str(self.D) + "\t" + str(self.P) + "\n"

#===============================================================================
# Global variables
#===============================================================================
avC=0 #average execution time
avD=0 #average D
tq = 4 #original time quantum
hyperperiod = []
util = 0 #CPU utilization 
tt = OrderedDict() # Time table. 
missedDeadlines = 0 # Number of deadlines missed during this simulation


#===============================================================================
# Useful function definitions
#===============================================================================
def _lcm(a,b): 
    return abs(a * b) / fractions.gcd(a,b) if a and b else 0

def lcm(a):
    return reduce(_lcm, a)

def avg(a, b):
    return (a + b) / 2.0

def task_table(tasks):
    textStr = "Task\tC\tD\tP\n"
    textStr += "------------------------------\n" 
    for task in tasks:
        textStr += str(task)
    textStr += "------------------------------\n"
    return textStr
        
def shiftLeftQueue(taskList):
    temp = taskList[0]
    for i in range(len(taskList)-1):
        taskList[i] = taskList[i+1]
    taskList[len(taskList)-1] = temp
    return taskList

def RoundRobin(taskList):
    """
    Implementation of Round-Robin function.
    """
    #===========================================================================
    # Local and global variable declarations
    #===========================================================================
    n = len(taskList) # Number of tasks in task list
    queue = []
    time = 0
    rp = 0
    done = 0
    start = 0
    global avC
    global avD
    global tt
    global hyperperiod 
    global util
    global missedDeadlines
    missFlag = False

    #===========================================================================
    # Calculate avC (average execution time) and avD (average deadline)
    #===========================================================================
    for t in taskList:
        avC+=t.C
        avD+=t.D
    avC/=n
    avD/=n
    print "Average Burst:",avC
    print "Average Deadline:",avD

    #===========================================================================
    # Calculate hyperperiod and utilization
    #===========================================================================
    for t in taskList:
        util += float(t.C)/float(t.P)
        hyperperiod.append(t.P)
    hyperperiod = lcm (hyperperiod)
    print "Hyperperiod:\t{}".format(hyperperiod)
    print "Utilization:\t{:.2f}".format(util)
    
    #===========================================================================
    # Calculate Intelligent Time Slice (ITS) for Round Robin to avoid very
    # frequent context switches in RTOS.
    # Reference paper : https://www.arpapress.com/Volumes/Vol2Issue2/IJRRAS_2_2_06.pdf
    # sc = Shortness Component
    # pc = Priority Component
    # bcb = Balanced Computation Burst
    # tq = original time quantum
    # q = calculated intelligent time quantum
    #===========================================================================    
    for t in taskList:
        if t.C <= avC:
            t.sc = 1
        if t.D <= avD:
            t.pc = 1
        t.cc = tq+t.pc+t.sc
        t.bcb = t.C - t.cc
        if t.bcb < tq:
            t.csc = t.bcb
        t.q = tq+t.pc+t.sc+t.csc
        print "T:{}\tsc:{}\tpc:{}\tcc:{}\tbcb:{}\tcsc:{}\tits:{}".format(t.name,t.sc,t.pc,t.cc,t.bcb,t.csc,t.q)
        
        # number of instances of this task throughout the hyperperiod
        t.inst = hyperperiod/t.P
    
    #===========================================================================
    # Create a time table of hyperperiod x n. Initially all 0. Used time instances
    # will be marked as 1. Missed deadline will be marked as 500. 
    #===========================================================================
    for t in taskList:
        tt[t.name] = [[0]*hyperperiod,t.color]

    #===========================================================================
    # Start scheduling the task list over the hyper period in round robin fashion
    #===========================================================================
    while time < hyperperiod:
        # Check for all the "new" tasks arrived on or before this time.
        for t in taskList:
            if (time - t.instDone * t.P) >= 0:
                t.C = t.bkpC
                queue.append(t)
                t.instDone += 1
                rp += 1
        
        # No remaining processes.. CPU is idle.
        if rp < 1:
            time += 1
            continue
        
        # Scheduling has started. Shift left to pick the first one in the queue.
        if start:
            queue = shiftLeftQueue(queue)
        
        # Pick the first task from queue and put it on CPU
        on_cpu = queue[0]
        # Assume that deadline won't be missed.
        missFlag = False
        # Is there an executable task on CPU?
        if on_cpu.C > 0 :
            # Yes there is. Is the time of this task bigger than time quantum?
            if on_cpu.C > on_cpu.q:
                # Yes it is. Execute for the assigned time quantum and put the remaining at
                # the end of queue.
                for i in range(time, time+on_cpu.q):
                    #Is the deadline missed already?
                    if i >= ((on_cpu.instDone - 1) * on_cpu.P + on_cpu.D):
                        # yes, mark this time instance as "missed deadline" on the time table
                        tt[on_cpu.name][0][i] = DEADLINEMISS
                        print "time:",i ," ", on_cpu.name, " missed the deadline!"
                        missFlag = True
                    else:
                        # No. We did it before deadline. Mark this time instance as a "success" on time table
                        tt[on_cpu.name][0][i] = USE
                on_cpu.C -= on_cpu.q
            else:
                # No, time quantum is sufficient for this task. Just execute it and get rid of it from the queue.
                for i in range(time,time+on_cpu.C):
                    # Is the deadline missed already?
                    if i >= ((on_cpu.instDone - 1) * on_cpu.P + on_cpu.D):
                        # yes, this time instance as "missed deadline" on the time table
                        tt[on_cpu.name][0][i] = DEADLINEMISS
                        print "time:",i ," ", on_cpu.name, " missed the deadline!"
                        missFlag = True
                    else:
                        # No. We did it before deadline. Mark this time instance as a "success" on time table
                        tt[on_cpu.name][0][i] = USE
                time+=on_cpu.C
                on_cpu.C = 0
                done+=1
                rp -= 1
            # Was a deadline missed? 
            if missFlag:
                # Yes. We missed one. 
                missedDeadlines += 1
            start=1
            
        else:
            # remove a "done" task from queue.
            queue.remove(on_cpu)

#===============================================================================
# Start execution from here
#===============================================================================
if __name__ == '__main__':
    
    # Read task list from taskfile.txt
    taskfile = open('taskfile.txt','r')
    tasklines = taskfile.readlines()
    taskList = []
    
    try:
        for line in tasklines:
            line = line.split('\t')
            name = line[0]
            color = line[4][:-1]
            C = int(line[1])
            D = int(line[2])
            P = int(line[3])
            taskList.append(Task(name=name, C=C,D=D,P=P,color=color))
    except Exception as exc:
        print "Invalid task file structure. Error: ", exc
        print "expected task structure as: ", "Task\tC\tD\tP\n"

    #Schedule this task list in round-robin fashion
    RoundRobin(taskList)
    
    #===========================================================================
    # for item in tt:
    #     print tt[item]
    #===========================================================================

    
    #plot properties
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_aspect('auto')

    # Major ticks every 2, minor ticks every 1
    major_xticks = np.arange(0, hyperperiod+1, hyperperiod/10)
    minor_xticks = np.arange(0, hyperperiod+1, 1)
    
    ax.set_xticks(major_xticks)
    ax.set_xticks(minor_xticks, minor=True)

    ylabels = ['Task (C,D,P)']
    for t in taskList:
        ylabels.append(t.name + " (" + str(t.bkpC) + "," + str(t.D) + "," + str(t.P)+ ")" )

    major_yticks = np.arange(0, len(taskList)+1, 1)
    ax.set_yticks(major_yticks)
    
    ax.set_yticklabels(ylabels,minor=False,rotation=15)
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)
    
    for y, (name,(row,color)) in enumerate(tt.items()):
        #Traverse through the hyperperiod. Mark deadline and period of each task with arrows.
        for j,task in enumerate(taskList):
            for i in xrange(0,hyperperiod+1,1):
                if (i % task.P == task.D) and (i > 0):
                    ax.annotate("",xy=(i,j),xycoords= 'data',xytext=(i,j+1),textcoords='data',
                        arrowprops=dict(arrowstyle='->',color='orange'))
                if (i % task.P == 0):
                    ax.annotate("",xy=(i,j+1),xycoords= 'data',xytext=(i,j),textcoords='data',
                        arrowprops=dict(arrowstyle='->',color='blue'))

        for x, col in enumerate(row):
            x1 = [x, x+1]
            y1 = np.array([y, y])
            y2 = y1+1
            if col==USE:
                plt.fill_between(x1, y1, y2=y2, color=color)
                plt.text(avg(x1[0], x1[1]), avg(y1[0], y2[0]), s='', 
                                            horizontalalignment='center',
                                            verticalalignment='center')
                
            if col==DEADLINEMISS:
                plt.fill_between(x1, y1, y2=y2, color='red')
                plt.text(avg(x1[0], x1[1]), avg(y1[0], y2[0]), s='', 
                                            horizontalalignment='center',
                                            verticalalignment='center')
                


    plt.xlim(0,hyperperiod)
    plt.ylim(0,len(taskList))
         
    textStr = "*** Round-Robin Scheduling ***\n"
    textStr += "------------------------------------------------------\n"
    #textStr += task_table(taskList)
    textStr += "U:\t{:.2f}\n".format(util)
    textStr += "Missed Deadlines: {}".format(missedDeadlines)
    textStr = textStr.expandtabs()
    plt.title(textStr,fontdict={'fontsize': 12, 'fontweight': 'medium'},loc='left')
    plt.show()