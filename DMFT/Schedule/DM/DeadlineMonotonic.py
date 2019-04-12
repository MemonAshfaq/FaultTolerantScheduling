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
import random
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict
import fractions
#===============================================================================
# Global variable and Constants
#===============================================================================
DEADLINEMISS_MARKER =   500
CPU_USAGE_MARKER    =   1
FAULT_MARKER        =   100
MTTF                =   50
RUNTIME             =   1000
FAULT_TOLERANCE     =   True

missedDeadlines = 0

#===============================================================================
# Few useful function definitions
#===============================================================================
def _lcm(a,b):
    '''
    returns an LCM of two numbers a and b
    '''
    return abs(a * b) / fractions.gcd(a,b) if a and b else 0

def lcm(a):
    '''
    returns an LCM of list a
    '''
    return reduce(_lcm, a)

def priority_cmp(one, other):
    '''
    function to compare priorities of two tasks
    '''
    if one.priority < other.priority:
        return -1
    elif one.priority > other.priority:
        return 1
    return 0

def tasktype_cmp(self, other):
    '''
    function to compare deadlines of two tasks
    '''    
    if self.D < other.D:
        return -1
    if self.D > other.D:
        return 1
    return 0

#===============================================================================
# A task instance
#===============================================================================
class TaskIns(object):
    '''
    A schedulable task instance
    '''
    def __init__(self, start, end, priority, D, name,color):
        self.start    = start #start time
        self.end      = end #finish time
        self.usage    = 0 #CPU time utilized by this task
        self.priority = priority #priority of this task compared to other task in taskset
        self.D = D #deadline of this task
        self.name     = name #Name given to this task. e.g. "T1"
        self.id = int(random.random() * 10000) #A random PID for each task
        self.color = color #Color to represent this task on plot

    def use(self, usage):
        '''
        Use CPU for "usage" time instances
        '''
        self.usage += usage
        if self.usage >= self.end - self.start:
            return True
        return False

    
class TaskType(object):
    '''
    A generic task which has properties such as execution time, deadline and period.
    '''
    def __init__(self, name, C, D, P,color):
        self.name = name #Unique name e.g. T1
        self.C  = C #WCET
        self.D  = D #deadline
        self.P  = P #period
        self.color = color #color to represent this task on the plot
        
    def __str__(self):
        return self.name + "\t" + str(self.C) + "\t" + str(self.D) + "\t" + str(self.P) + "\n"

def task_table(tasks):
    '''
    Function to print the task list in decorative manner.
    '''
    textStr = "Task\tC\tD\tP\n"
    textStr += "------------------------------\n" 
    for task in tasks:
        textStr += str(task)
    textStr += "------------------------------\n"
    return textStr

def avg(a, b):
    '''
    Function to calculate an average of two numbers a and b
    '''
    return (a + b) / 2.0

#===============================================================================
# main entry point
#===============================================================================
if __name__ == '__main__':

    #declare necessary local variables
    taskList = []
    hyperperiod = []
    tasks = []

    #open taskfile.txt to read the list of tasks
    taskfile = open('taskfile.txt','r')
    tasklines = taskfile.readlines()
    
    #read taskfile line by line. Each line represents a task. Extract name, WCET, deadline, period and color from each line 
    try:
        for line in tasklines:
            line = line.split('\t')
            name = line[0]
            color = line[4][:-1]
            C=int(line[1]) #WCET
            D=int(line[2]) #deadline
            P=int(line[3]) #period
            taskList.append(TaskType(name=name, C=C, D=D, P=P,color=color))

    except Exception as exc:
        print "Invalid task file structure. Error: ", exc
        print "Task set should look like: Task\tC\tD\tP\tcolor\n"
    
    print task_table(taskList)
    
    #===========================================================================
    # Calculate hyperperiod and utilization for given taskset
    #===========================================================================
    util = 0
    for task in taskList:
        util += float(task.C)/float(task.P)
        hyperperiod.append(task.P)
    hyperperiod = lcm (hyperperiod)
    print "hyperperiod:\t{}".format(hyperperiod)
    print "utilization:\t{:.2f}".format(util)

    if util > 1:
        print "Taskset is not schedulable! utilization: {}".format(util)

    #===========================================================================
    # We will create a hyperperiod x n size dictionary (tt) for time table. Each 
    # entry represents if the CPU was used by this task at that instance. If yes, 
    # mark it with 1 (CPU_USAGE_MARKER) Flag. If deadline missed, mark that instance with 500 
    # (DEADLINEMISS_MARKER) flag. 
    #===========================================================================
    
    #initialize all time entries in the time table with 0. 
    tt = OrderedDict()
    for i in range(len(taskList)):
        tt[taskList[i].name] = [[0]*RUNTIME,taskList[i].color]

    #Traverse through RUNTIME and find out all eligible task at each instance. Append each
    #task in a list. We will pick the task with shortest deadline at each instance and put
    #it on CPU when it is time to schedule.
    for i in xrange(0, RUNTIME):
        for task_type in taskList:
            if  i  % task_type.P == 0:
                start = i
                end = start + task_type.C
                priority = task_type.D
                D = start + task_type.D
                tasks.append(TaskIns(start=start, end=end, priority=priority, D=D, name=task_type.name,color=task_type.color))    
    
    faults = []
    if FAULT_TOLERANCE:
        for i in xrange(0,RUNTIME):
            if i % MTTF == 0:
                faults.append(random.randint(i,i+MTTF-1))

    #Simulate a clock
    clock_step = 1
    for i in xrange(0, RUNTIME, clock_step):
        print "t:",i,":\t",
        #Fetch possible tasks that can use CPU and sort them by priority
        possible = []
        for t in tasks:
            if t.start <= i:
                possible.append(t)
        possible = sorted(possible, priority_cmp)

        #Select task with highest priority (shortest deadline)
        
        if len(possible) > 0:
            on_cpu = possible[0]
            if i in faults:
                tt[on_cpu.name][0][i] = FAULT_MARKER
                possible[0].usage = 0
                print "Task {} faulted!".format(on_cpu.name) 
                continue
            if i >= on_cpu.D: #missed a deadline already
                print on_cpu.name, " missed the deadline!"
                tt[on_cpu.name][0][i] = DEADLINEMISS_MARKER #marker for missed deadline
                if tt[on_cpu.name][0][i-1] <= CPU_USAGE_MARKER: # 1 or 0, 1 for USE, 0 for IDLE.
                    missedDeadlines += 1
            else:
                tt[on_cpu.name][0][i] = CPU_USAGE_MARKER
            print on_cpu.name , " is on CPU."
            #Is this task finished?
            if on_cpu.use(clock_step):
                # Yes, remove it from list
                tasks.remove(on_cpu)
                print "Finish!" 
        else:
            print "CPU free."

    #===========================================================================
    # Scheduling is completed. Now, plot the time table.
    #===========================================================================
    #plot properties
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_aspect('auto')

    # Major ticks every 2, minor ticks every 1
    major_xticks = np.arange(0, RUNTIME+1, RUNTIME/10)
    minor_xticks = np.arange(0, RUNTIME+1, 1)
    
    ax.set_xticks(major_xticks)
    ax.set_xticks(minor_xticks, minor=True)

    ylabels = ['Task (C,D,P)']
    for t in taskList:
        ylabels.append(t.name + " (" + str(t.C) + "," + str(t.D) + "," + str(t.P)+ ")" )

    major_yticks = np.arange(0, len(taskList)+1, 1)
    ax.set_yticks(major_yticks)
    
    ax.set_yticklabels(ylabels,minor=False,rotation=15)
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)
    
    for y, (name,(row,color)) in enumerate(tt.items()):
        #Traverse through the RUNTIME. Mark deadline and period of each task with arrows.
        for j,task in enumerate(taskList):
            for i in xrange(0,RUNTIME+1,clock_step):
                if (i % task.P == task.D) and (i > 0):
                    ax.annotate("",xy=(i,j),xycoords= 'data',xytext=(i,j+1),textcoords='data',
                        arrowprops=dict(arrowstyle='->',color='black'))
                if (i % task.P == 0):
                    ax.annotate("",xy=(i,j+1),xycoords= 'data',xytext=(i,j),textcoords='data',
                        arrowprops=dict(arrowstyle='->',color='blue'))        

        for x, col in enumerate(row):
            x1 = [x, x+1]
            y1 = np.array([y, y])
            y2 = y1+1
            if col==CPU_USAGE_MARKER:
                plt.fill_between(x1, y1, y2=y2, color=color)
                plt.text(avg(x1[0], x1[1]), avg(y1[0], y2[0]), s='', 
                                            horizontalalignment='center',
                                            verticalalignment='center')
                
            if col==DEADLINEMISS_MARKER:
                plt.fill_between(x1, y1, y2=y2, color='red')
                plt.text(avg(x1[0], x1[1]), avg(y1[0], y2[0]), s='', 
                                            horizontalalignment='center',
                                            verticalalignment='center')
                
            if col==FAULT_MARKER:
                plt.fill_between(x1, y1, y2=y2, color='yellow')
                plt.text(avg(x1[0], x1[1]), avg(y1[0], y2[0]), s='', 
                                            horizontalalignment='center',
                                            verticalalignment='center')


    plt.xlim(0,RUNTIME)
    plt.ylim(0,len(taskList))
         
    textStr = "*** Deadline Monotonic Scheduling ***\n"
    textStr += "------------------------------------------------------\n"
    #textStr += task_table(taskList)
    textStr += "CPU utilization:\t{:.2f}\n".format(util)
    #textStr+= r'$Average\ Task\ Utilization\ \alpha: {}$'.format(util / len(taskList)) + "\n"
    textStr += "Hyperperiod:\t{}\n".format(hyperperiod)    
    textStr += "Missed Deadlines: \t{}".format(missedDeadlines)
    textStr = textStr.expandtabs()
    plt.title(textStr,fontdict={'fontsize': 8, 'fontweight': 'medium'},loc='left')
    plt.show()