'''
Created on 5 Apr 2019

@author: aspak.rogatiya
'''
import random
from prime import lcm
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict

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
    def __init__(self, start, end, priority, name,color):
        self.start    = start
        self.end      = end
        self.usage    = 0
        self.priority = priority
        self.name     = name.replace("\n", "")
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
        return self.name + "\t" + str(self.c) + "\t" + str(self.d) + "\t" + str(self.p) 

def print_taskset(tasks):
    print "Task\tc\td\tp"
    print "--------------------------" 
    for task in tasks:
        print task
    print "--------------------------"


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
    
    print_taskset(task_types)

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
                tasks.append(TaskIns(start=start, end=end, priority=priority, name=task_type.name,color=task_type.color))    
    
    
    clock_step = 1
    for i in xrange(0, hyperperiod, clock_step):
        #Fetch possible tasks that can use cpu and sort by priority
        possible = []
        for t in tasks:
            if t.start <= i:
                possible.append(t)
        possible = sorted(possible, priority_cmp)

        #Select task with highest priority
        if len(possible) > 0:
            on_cpu = possible[0]
            print on_cpu.get_unique_name() , " uses the processor. " ,
            tt[on_cpu.name][0][i] = 1
            if on_cpu.use(clock_step):
                tasks.remove(on_cpu)
                print "Finish!" ,
        else:
            print 'No task uses the processor. '
            tt[on_cpu.name][0][i] = 100
        print "\n"

    #Print remaining periodic tasks
    for p in tasks:
        print p.get_unique_name() + " is dropped due to overload at time: " + str(i)


    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axes.get_yaxis().set_visible(True)
    ax.set_aspect(1)
    plt.grid(True)
    
    for y, (name,(row,color)) in enumerate(tt.items()):
        for x, col in enumerate(row):
            x1 = [x, x+1]
            y1 = np.array([y, y])
            y2 = y1+1
            if col==1:
                plt.fill_between(x1, y1, y2=y2, color=color)
                plt.text(avg(x1[0], x1[1]), avg(y1[0], y2[0]), name, 
                                            horizontalalignment='center',
                                            verticalalignment='center')
            if col==100:
                plt.fill_between(x1, y1, y2=y2, color='grey')
                plt.text(avg(x1[0], x1[1]), avg(y1[0], y2[0]), "E", 
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
    plt.xlim(0)
    plt.show()