
chart = []
class Process:
    def __init__(self,pid,AT,BT,deadline,period,color):
        self.pid = pid
        self.arrival = AT
        self.burst = BT
        self.period = period
        self.deadline = deadline
        self.color = color
        
def shiftCL(plist):
    temp = plist[0]
    for i in range(len(plist)-1):
        plist[i] = plist[i+1]
    plist[len(plist)-1] = temp
    return plist

def RR(tq,plist,n):
    global chart
    queue = []
    time = 0
    ap = 0
    rp = 0
    done = 0
    q = tq
    start = 0
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
            if queue[0].burst > q:
                for _ in range(time, time+q):
                    chart.append(queue[0].pid)
                time+=q
                queue[0].burst -= q
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

    RR(4,task_types,len(task_types))
    
    for i in range(len(chart)):
        if(i and (chart[i]!=chart[i-1])):
            print "\n"
        print "t: {}\t{}".format(i, chart[i])
