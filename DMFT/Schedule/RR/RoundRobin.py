import fractions

def _lcm(a,b): return abs(a * b) / fractions.gcd(a,b) if a and b else 0

def lcm(a):
    return reduce(_lcm, a)

chart = []

avC=0 #average execution time
avD=0 #average deadline

tq = 4

class Process:
    def __init__(self,pid,AT,BT,deadline,period,color):
        self.pid = pid
        self.arrival = AT
        self.burst = BT
        self.period = period
        self.deadline = deadline
        self.color = color
        self.sc = 0 #shortness component
        self.pc = 0 #priority component
        self.cc = 0 #computed component
        self.csc = 0 #context switch component
        self.bcb = 0 #balanced cpu birst
        self.q = tq #intelligent time slice
        
        
def shiftCL(plist):
    temp = plist[0]
    for i in range(len(plist)-1):
        plist[i] = plist[i+1]
    plist[len(plist)-1] = temp
    return plist

def RR(plist,n):
    global chart
    queue = []
    hyperperiod = []
    time = 0
    ap = 0
    rp = 0
    done = 0
    start = 0
    global avC
    global avD
    #calculate average execution time
    for p in plist:
        avC+=p.burst
        avD+=p.deadline
    avC/=n
    avD/=n
    print "Average Burst:",avC
    print "Average Deadline:",avD

    util = 0
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
        
    
    while done < n:
        for i in range(ap,n):
            if time >= plist[i].arrival:
                queue.append(plist[i])
                ap += 1
                rp += 1
        
        if rp < 1:
            chart.append(0)
            time += 1
            continue
        
        if start:
            queue = shiftCL(queue)
            
        if queue[0].burst > 0 :
            if queue[0].burst > queue[0].q:
                for _ in range(time, time+queue[0].q):
                    chart.append(queue[0].pid)
                time+=queue[0].q
                queue[0].burst -= queue[0].q
            else:
                for _ in range(time,time+queue[0].burst):
                    chart.append(queue[0].pid)
                time+=queue[0].burst
                queue[0].burst = 0
                done+=1
                rp -= 1                
            start=1

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
