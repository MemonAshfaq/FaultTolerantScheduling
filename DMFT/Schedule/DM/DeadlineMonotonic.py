'''
Created on 5 Apr 2019

@author: aspak.rogatiya
'''
import random
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict
import fractions

missedDeadlines = 0

IDLE=100
DEADLINEMISS=500
USE=1

def _lcm(a,b): return abs(a * b) / fractions.gcd(a,b) if a and b else 0

def lcm(a):
    return reduce(_lcm, a)

#Priority comparison
def priority_cmp(one, other):
    if one.priority < other.priority:
        return -1
    elif one.priority > other.priority:
        return 1
    return 0

#Deadline monotonic comparison
def tasktype_cmp(self, other):
    if self.deadline < other.deadline:
        return -1
    if self.deadline > other.deadline:
        return 1
    return 0

class TaskIns(object):
    def __init__(self, start, end, priority, deadline, name,color):
        self.start    = start
        self.end      = end
        self.usage    = 0
        self.priority = priority
        self.deadline = deadline
        self.name     = name
        self.id = int(random.random() * 10000)
        self.color = color

    def use(self, usage):
        self.usage += usage
        if self.usage >= self.end - self.start:
            return True
        return False

    #Get name as Name#id
    def get_unique_name(self):
        return str(self.name) + "#" + str(self.id)
    
class TaskType(object):
    def __init__(self, name, execution, deadline, period,color):
        self.name = name
        self.c  = execution
        self.d  = deadline
        self.p  = period
        self.color = color
        
    def __str__(self):
        return self.name + "\t" + str(self.c) + "\t" + str(self.d) + "\t" + str(self.p) + "\n"

def print_taskset(tasks):
    textStr = "Task\tC\tD\tP\n"
    textStr += "------------------------------\n" 
    for task in tasks:
        textStr += str(task)
    textStr += "------------------------------\n"
    return textStr

def avg(a, b):
    return (a + b) / 2.0

if __name__ == '__main__':
    taskfile = open('taskfile.txt','r')
    tasklines = taskfile.readlines()
    task_types = []
    hyperperiod = []
    tasks = []
    
    try:
        for line in tasklines:
            line = line.split('\t')
            name = line[0]
            color = line[4][:-1]
            for i in range (1,4):
                line[i] = int(line[i])
            task_types.append(TaskType(name=name, execution=line[1], deadline=line[2], period=line[3],color=color))

    except Exception as exc:
        print "Invalid task file structure. Error: ", exc
    
    print print_taskset(task_types)

    util = 0
    for task in task_types:
        util += float(task.c)/float(task.p)
        hyperperiod.append(task.p)
    hyperperiod = lcm (hyperperiod)
    print "hyperperiod:\t{}".format(hyperperiod)
    print "utilization:\t{}".format(util)

    if util > 1:
        print "Taskset is not schedulable! utilization: {}".format(util)
    tt = OrderedDict()
    for i in range(len(task_types)):
        tt[task_types[i].name] = [[0]*hyperperiod,task_types[i].color]

    #Create task instances
    for i in xrange(0, hyperperiod):
        for task_type in task_types:
            if  i  % task_type.p == 0:
                start = i
                end = start + task_type.c
                priority = task_type.d
                deadline = start + task_type.d
                tasks.append(TaskIns(start=start, end=end, priority=priority, deadline=deadline, name=task_type.name,color=task_type.color))    
    
    
    clock_step = 1
    for i in xrange(0, hyperperiod, clock_step):
        print "t:",i,":\t",
        #Fetch possible tasks that can use cpu and sort by priority
        possible = []
        for t in tasks:
            if t.start <= i:
                possible.append(t)
        possible = sorted(possible, priority_cmp)

        #Select task with highest priority
        if len(possible) > 0:
            on_cpu = possible[0]
            if i >= on_cpu.deadline: #missed deadline already
                print on_cpu.get_unique_name() , " missed the deadline. ",
                tt[on_cpu.name][0][i] = DEADLINEMISS #marker for missed deadline
                
                if tt[on_cpu.name][0][i-1] <= USE: # 1 or 0, 1 for used, 0 for not used.
                    missedDeadlines += 1
            else:
                tt[on_cpu.name][0][i] = USE
            print on_cpu.get_unique_name() , " on CPU. "
            if on_cpu.use(clock_step):
                tasks.remove(on_cpu)
                print "Finish!" 
        else:
            print "CPU free."
            #tt[on_cpu.name][0][i] = IDLE

    #Print remaining periodic tasks
    for p in tasks:
        print p.get_unique_name() + " is dropped due to overload at time: " + str(i)


    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axes.get_yaxis().set_visible(True)
    ax.set_aspect(1)
    plt.grid(False)
    
    for y, (name,(row,color)) in enumerate(tt.items()):
        for x, col in enumerate(row):
            x1 = [x, x+1]
            y1 = np.array([y, y])
            y2 = y1+1
            if col==USE:
                plt.fill_between(x1, y1, y2=y2, color=color)
                plt.text(avg(x1[0], x1[1]), avg(y1[0], y2[0]), name, 
                                            horizontalalignment='center',
                                            verticalalignment='center')
            if col==IDLE:
                plt.fill_between(x1, y1, y2=y2, color='grey')
                plt.text(avg(x1[0], x1[1]), avg(y1[0], y2[0]), "E", 
                                            horizontalalignment='center',
                                            verticalalignment='center')
                
            if col==DEADLINEMISS:
                plt.fill_between(x1, y1, y2=y2, color='yellow')
                plt.text(avg(x1[0], x1[1]), avg(y1[0], y2[0]), name, 
                                            horizontalalignment='center',
                                            verticalalignment='center')
                
        #mark deadlines and periods
        for task in task_types:
            for i in xrange(0,hyperperiod+1,clock_step):
                if (i % task.p == task.d) and (i > 0):
                    ax.annotate("",xy=(i,int(task.name[1])-1),xycoords= 'data',xytext=(i,int(task.name[1])),textcoords='data',
                        arrowprops=dict(arrowstyle='simple'))
                if (i % task.p == 0):
                    ax.annotate("",xy=(i,int(task.name[1])),xycoords= 'data',xytext=(i,int(task.name[1])-1),textcoords='data',
                        arrowprops=dict(arrowstyle='fancy'))

    plt.xticks(np.arange(0,hyperperiod+1,2))
    plt.yticks(np.arange(0,len(task_types)+1))
    plt.xlim(0,hyperperiod)
    plt.ylim(0,len(task_types)+3)
    
    #props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
     
    textStr = "*** Deadline Monotonic Scheduling ***\n"
    textStr += "------------------------------------------------------\n"
    textStr += print_taskset(task_types)
    textStr += "U:\t{:.2f}\n".format(util)
    textStr += "Missed Deadlines: {}".format(missedDeadlines)
    textStr = textStr.expandtabs()
    # place a text box in upper left in axes coords
    #ax.text(0.05, 0.95, textStr, transform=ax.transAxes, fontsize=8,
    #        verticalalignment='top', bbox=props)
    plt.title(textStr,fontdict={'fontsize': 8, 'fontweight': 'medium'},loc='left')
    plt.show()