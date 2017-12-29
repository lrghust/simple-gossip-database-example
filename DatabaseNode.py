import socket,pickle,sys,random,time,os

def gossip(msg,neighbors,pull=False):
    global state
    global database
    if pull:
        if neighbors:
            peer=random.choice(neighbors)
            skt.sendto(pickle.dumps((-2,selfAddr)),peer) # pull request
            data,addr=skt.recvfrom(4096)
            state, database=pickle.loads(data)
    else:
        peer=random.choice(neighbors)
        skt.sendto(pickle.dumps(msg),peer)


# set socket

skt=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
selfAddr=(sys.argv[1],int(sys.argv[2]))
skt.bind(selfAddr)
LBServer=('127.0.0.1',10000)

# tell LBServer i'm on
msg=('NODE',None)
skt.sendto(pickle.dumps(msg),LBServer)

# receive all nodes from LBServer
data,addr=skt.recvfrom(1024)
neighbors=pickle.loads(data)
#import pdb;pdb.set_trace()

# state: synchronized id on all nodes
# database: store form [(name, age),...]
# pull and tell others my addr
state=1
database={}
gossip(None,neighbors,True)

# event loop
skt.setblocking(0) # not blocking
init=True
while True:
    os.system('clear')
    print 'state:'
    print state
    print 'neighbors:'
    print neighbors
    print 'database:'
    print database
    print ''
    skt.sendto(pickle.dumps(('state',state)),LBServer) # tell LBServer cur state

    try:
        data,addr=skt.recvfrom(1024)
    except socket.error,e:
        if not init:
            gossip(valid,neighbors) # gossip last valid msg
        time.sleep(1)
        continue

    ind, msg=pickle.loads(data)
    #print 'ind:',ind,'state:',state,msg
    #import pdb;pdb.set_trace()
    if ind<=state and ind>=0:
        continue

    if ind==-2: # pull request
        skt.sendto(pickle.dumps((state+1,database)),addr)
    # todo: ind>state+1
    state+=1
    valid=(state,msg) # update last valid packet

    if msg[0]=='insert':
        database[msg[1][0]]=msg[1][1]
    elif msg[0]=='delete':
        database.pop(msg[1])
    else:
        neighbors.append(msg)

    gossip(valid,neighbors)
    time.sleep(1)
    init=False
