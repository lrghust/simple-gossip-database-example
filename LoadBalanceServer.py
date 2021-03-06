import socket,pickle,random,time
import numpy as np

# set socket
skt=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
LBServer=('127.0.0.1',10000)
skt.bind(LBServer)

# all databases' addr,states
db=[]
states=[]
statestime=[]
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
skt.settimeout(1)
while True:
    try:
        data,addr=skt.recvfrom(1024)
    except socket.error,e:
        pass
    else:
        mark,content=pickle.loads(data)
        if mark=='state': # sychonize states
            curtime=time.time()
            states[db.index(addr)]=content
            statestime[db.index(addr)]=curtime
            print 'states',states,'nodeState',nodeState,'selfState',selfState
            crashinds=np.where(curtime-np.array(statestime)>len(states)+1)[0] # timeout
            if crashinds.shape[0]!=0:
                queue.append((pickle.dumps(('crash',[db[ind] for ind in crashinds])),None,selfState))
                selfState+=1
                states=np.delete(states,crashinds).tolist()
                statestime=np.delete(statestime,crashinds).tolist()
                db=[db[ind] for ind in range(len(db)) if ind not in crashinds]
        else: # database operation
            queue.append((data,addr,selfState))
            selfState+=1
            if mark=='NODE': # new replica node will create two operation
                queue.append((pickle.dumps(('ADD',None)),addr,selfState-1))

    # wait until all node become identical and the same as self state
    if not consensus(states) or len(queue)==0 or queue[0][2]!=nodeState:
        continue

    # deal with message
    data,addr,_=queue.pop(0)
    mark,content=pickle.loads(data)
    print mark,content
    if db:
        dbAddr=random.choice(db) # here just random choose a DBNode as an easy example instead of doing load balance
        while len(db)>1:
            dbAddr2=random.choice(db) # here just random choose a DBNode as an easy example instead of doing load balance
            if dbAddr!=dbAddr2:
                break
    if mark in ['insert','delete']:
        skt.sendto(pickle.dumps((-1,(mark,content))),dbAddr)
        if len(db)>1:
            skt.sendto(pickle.dumps((-1,(mark,content))),dbAddr2) # in case one of the node is crashed, send twice
    elif mark=='NODE': # add new node
        skt.sendto(pickle.dumps(db),addr) # send other DBNode addr to this new db
        db.append(addr)
        states.append(0)
        statestime.append(time.time())
        print 'database',addr,': on'
    elif mark=='ADD': # gossip new node addr
        skt.sendto(pickle.dumps((-1,addr)),dbAddr)
        if len(db)>1:
            skt.sendto(pickle.dumps((-1,addr)),dbAddr2)
    elif mark=='crash': # gossip node crash
        skt.sendto(pickle.dumps((-1,(mark,content))),dbAddr)
        if len(db)>1:
            skt.sendto(pickle.dumps((-1,(mark,content))),dbAddr2)
