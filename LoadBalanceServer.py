import socket,pickle,random,time

# set socket
skt=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
LBServer=('127.0.0.1',10000)
skt.bind(LBServer)

# all databases' addr,states
db=[]
states=[]
def consensus(states):
    if len(states)<=1:
        return True
    for i in range(len(states)-1):
        if states[i]!=states[i+1]:
            return False
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
        if mark=='state':
            states[db.index(addr)]=content
        else:
            queue.append((data,addr))
    if not consensus(states) or len(queue)==0: # wait until all node become identical
        continue

    # deal with message
    data,addr=queue.pop(0)
    mark,content=pickle.loads(data)
    if mark=='NODE':
        print 'database',addr,': on'
        skt.sendto(pickle.dumps(db),addr) # send other DBNode addr to this new db
        db.append(addr)
        states.append(0)
    elif mark in ['insert','delete']:
        dbAddr=random.choice(db) # here just random choose a DBNode as an easy example instead of doing load balance
        skt.sendto(pickle.dumps((-1,(mark,content))),dbAddr)
