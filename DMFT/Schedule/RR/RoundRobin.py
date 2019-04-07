
chart = []
class Process:
    def __init__(self,pid,AT,BT):
        self.pid = pid
        self.arrival = AT
        self.burst = BT

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

plist=[]
plist.append(Process(1,0,25))
plist.append(Process(2,0,5))
plist.append(Process(3,0,15))
plist.append(Process(4,0,8))
plist.append(Process(5,0,10))

RR(4,plist,len(plist))

for i in range(len(chart)):
    if(i and (chart[i]!=chart[i-1])):
        print "\n"
    print "t: {}\tT{}".format(i, chart[i])
    