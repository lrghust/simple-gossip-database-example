import socket,pickle

# set socket
skt=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
LBServer=('127.0.0.1',10000)

# send simple database command, insert and delete only, just a simple example
# insert name age
# delete name
while True:
    line=raw_input('> ')
    if line == 'q':
        break

    cmd=line.split()
    if cmd[0]=='insert':
        if len(cmd)!=3:
            print 'error: insert need 2 arguments(name age).'
            continue
        msg=(cmd[0],(cmd[1],cmd[2]))

    elif cmd[0]=='delete':
        if len(cmd)!=2:
            print 'error: delete need 1 argument(name).'
            continue
        msg=tuple(cmd)

    else:
        print 'error: support insert and delete only'
        continue
    skt.sendto(pickle.dumps(msg),LBServer)
