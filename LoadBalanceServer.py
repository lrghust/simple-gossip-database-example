import socket,pickle,random,time

# set socket
skt=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
LBServer=('127.0.0.1',10000)
skt.bind(LBServer)

# all databases' addr,states
db=[]
states=[]
nodeState=0 # the identical state
selfState=0 # the state of LBServer itself
def consensus(states):
    global nodeState
    if len(states)==0:
        return True
    if len(states)==1:
        nodeState=states[0]
        return True
    for i in range(len(states)-1):
        if states[i]!=states[i+1]:
            return False
    nodeState=states[0]
    return True
# message queue
queue=[]
# event loop
skt.setblocking(0)
while True:
    try:
        data,addr=skt.recvfrom(1024)
    except socket.error,e:
        pass
    else:
        mark,content=pickle.loads(data)
        if mark=='state': # sychonize states
            states[db.index(addr)]=content
            print states,nodeState,selfState
        elif mark=='NODE': # add new node
            print 'database',addr,': on'
            skt.sendto(pickle.dumps(db),addr) # send other DBNode addr to this new db
            db.append(addr)
            states.append(0)
            selfState+=1
        else: # database operation
            queue.append((data,addr,selfState))
            selfState+=1

    # wait until all node become identical and the same as self state
    if not consensus(states) or len(queue)==0 or queue[0][2]!=nodeState:
        continue

    # deal with message
    data,addr,_=queue.pop(0)
    mark,content=pickle.loads(data)
    print mark,content
    if mark in ['insert','delete']:
        dbAddr=random.choice(db) # here just random choose a DBNode as an easy example instead of doing load balance
        skt.sendto(pickle.dumps((-1,(mark,content))),dbAddr)
