import fractions
import time
from collections import OrderedDict
import matplotlib.pyplot as plt
import numpy as np

def _lcm(a,b): return abs(a * b) / fractions.gcd(a,b) if a and b else 0

def lcm(a):
    return reduce(_lcm, a)

def avg(a, b):
    return (a + b) / 2.0

chart = []

avC=0 #average execution time
avD=0 #average deadline

tq = 4
hyperperiod = []
util = 0
tt = OrderedDict()
missedDeadlines = 0

class Process:
    def __init__(self,pid,AT,BT,deadline,period,color):
        self.pid = pid
        self.arrival = AT
        self.burst = BT
        self.bkpburst = BT
        self.period = period
        self.deadline = deadline
        self.color = color
        self.sc = 0 #shortness component
        self.pc = 0 #priority component
        self.cc = 0 #computed component
        self.csc = 0 #context switch component
        self.bcb = 0 #balanced cpu birst
        self.q = tq #intelligent time slice
        self.inst = 0 #number of instances in hyperperiod
        self.instDone = 0 #number of instances done
        
        
def shiftCL(plist):
    temp = plist[0]
    for i in range(len(plist)-1):
        plist[i] = plist[i+1]
    plist[len(plist)-1] = temp
    return plist

def RR(plist,n):
    global chart
    queue = []
    t = 0
    ap = 0
    rp = 0
    done = 0
    start = 0
    global avC
    global avD
    global tt
    global hyperperiod 
    global util
    #calculate average execution time
    for p in plist:
        avC+=p.burst
        avD+=p.deadline
    avC/=n
    avD/=n
    print "Average Burst:",avC
    print "Average Deadline:",avD

    for p in plist:
        util += float(p.burst)/float(p.period)
        hyperperiod.append(p.period)
    hyperperiod = lcm (hyperperiod)
    print "hyperperiod:\t{}".format(hyperperiod)
    print "utilization:\t{}".format(util)
    
    for p in plist:
        if p.burst <= avC:
            p.sc = 1
        if p.deadline <= avD:
            p.pc = 1
        p.cc = tq+p.pc+p.sc
        p.bcb = p.burst - p.cc
        if p.bcb < tq:
            p.csc = p.bcb
        p.q = tq+p.pc+p.sc+p.csc
        print "T:{}\tsc:{}\tpc:{}\tcc:{}\tbcb:{}\tcsc:{}\tits:{}".format(p.pid,p.sc,p.pc,p.cc,p.bcb,p.csc,p.q)
        
        p.inst = hyperperiod/p.period
    
    #for i in range(len(task_types)):
    for p in plist:
        tt[p.pid] = [[0]*hyperperiod,p.color]

    for item in tt:
        print tt[item]
        
    while t < hyperperiod:
        for p in plist:
            if (t - p.instDone * p.period) >= 0:
                p.burst = p.bkpburst
                queue.append(p)
                p.instDone += 1
                ap += 1
                rp += 1
        
        if rp < 1:
            chart.append(0)
            t += 1
            continue
        
        if start:
            queue = shiftCL(queue)
        
        #pick the first task from queue and put it on cpu
        on_cpu = queue[0]
            
        if on_cpu.burst > 0 :
            if on_cpu.burst > on_cpu.q:
                for i in range(t, t+on_cpu.q):
                    chart.append(on_cpu.pid)
                    tt[on_cpu.pid][0][i] = 1
                t+=on_cpu.q
                on_cpu.burst -= on_cpu.q
            else:
                for i in range(t,t+on_cpu.burst):
                    chart.append(on_cpu.pid)
                    tt[on_cpu.pid][0][i] = 1
                t+=on_cpu.burst
                on_cpu.burst = 0
                done+=1
                rp -= 1                
            start=1
        else:
            queue.remove(on_cpu)

if __name__ == '__main__':
    taskfile = open('taskfile.txt','r')
    tasklines = taskfile.readlines()
    task_types = []
    
    try:
        for line in tasklines:
            line = line.split('\t')
            name = line[0]
            color = line[4][:-1]
            c = int(line[1])
            d = int(line[2])
            p = int(line[3])
            task_types.append(Process(pid=name, AT=0, BT=c,deadline=d,period=p,color=color))
    except Exception as exc:
        print "Invalid task file structure. Error: ", exc

    RR(task_types,len(task_types))
    
    for i in range(len(chart)):
        if(i and (chart[i]!=chart[i-1])):
            print "\n"
        print "t: {}\t{}".format(i, chart[i])

    print chart
    for item in tt:
        print tt[item]




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
                
            if col==500:
                plt.fill_between(x1, y1, y2=y2, color='yellow')
                plt.text(avg(x1[0], x1[1]), avg(y1[0], y2[0]), name, 
                                            horizontalalignment='center',
                                            verticalalignment='center')
                
        #mark deadlines and periods
        clock_step = 1

        for task in task_types:
            for i in xrange(0,hyperperiod+1,clock_step):
                if (i % task.period == task.deadline) and (i > 0):
                    ax.annotate("",xy=(i,int(task.pid[1])-1),xycoords= 'data',xytext=(i,int(task.pid[1])),textcoords='data',
                        arrowprops=dict(arrowstyle='simple'))
                if (i % task.period == 0):
                    ax.annotate("",xy=(i,int(task.pid[1])),xycoords= 'data',xytext=(i,int(task.pid[1])-1),textcoords='data',
                        arrowprops=dict(arrowstyle='fancy'))

    plt.xticks(np.arange(0,hyperperiod+1,2))
    plt.yticks(np.arange(0,len(task_types)+1))
    plt.xlim(0,hyperperiod)
    plt.ylim(0,len(task_types)+3)
    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
     
    textStr = ""
    for task in task_types:
        textStr += "{}:({},{},{})  ".format(task.pid,task.bkpburst,task.deadline,task.period)
 
    textStr += "U: {:.2f}\n".format(util)
    textStr += "Missed Deadlines: {}".format(missedDeadlines)
 
    # place a text box in upper left in axes coords
    ax.text(0.05, 0.95, textStr, transform=ax.transAxes, fontsize=8,
            verticalalignment='top', bbox=props)
    
    plt.show()
    #plt.savefig('foo.png', bbox_inches='tight',dpi=500)    