# A Simple Distributed Database Based on Gossip

> Ruiguang Li

I implement a simple distributed database based on gossip protocol.

## 1 Usage
*Details of implementation will be talked in next part*

1. Launch Load Balance Server first:
```bash
$ python LoadBalanceServer.py
```

2. Then launch several Database Replica:
```bash
$ python DatabaseNode.py ip_address port
```

for example:
```bash
$ python DatabaseNode.py 127.0.0.1 10001
```
*Note that the Load Balance Server uses port 10000, so don't use it here.*

The output includes:
- state: current state of this replica
- neighbors: neighbor replicas' information
- table: the table stored on this replica

3. Launch the client:
```bash
$ python Client.py
```

A simulated command interpretor is shown here, with mark '>' indicating each new line.
This simple interpretor supports two command: insert and delete
```sql
> insert name age
> delete name
```

The database contains a simple table with only two attribute: name and age. By using the insert and delete command, corresponding record will be inserted to or deleted from the table. Table on each Database Replica is shown by output of DatabaseNode.py.

## 2 Details
### 2.1 Architecture
![architecture](./arch.png)

This simple system consists of several clients, one load balance server and several database replica, which supports multi-client at the same time.

### 2.2 Client
Here I implement a simple client just as a simple example. The client provides simple REPL interface, which supports two basic command used in database: insert and delete.

A simple table is used here with two attributes: name and age.

| Name | age | 
| - | -: | 
| Tom | 18 |
| Jane | 20 | 
| ... | ... | 

#### Command
- *insert* should be followed by two arguments: 
```sql
insert name age
```
for example
```sql
insert Tom 18
```
will insert the record <'Tom','18'> into the table. 
Here name serves as the key value in that table. So when insert same name more than one time the table will keep the last one.

- *delete* should be followed by one arguments: 
```sql
delete name
```
for example
```sql
delete Tom
```
will delete the record <'Tom','18'> from the table. As mentioned in *insert*, because the table will only keep the last one of the records with same name, there will not be duplicate name in the table.

The command received from the interpretor will be directly sent to the Load Balance Server. There would be no problem if multi-clients send commands at the same time or one client sends commands in a very fast speed, which will be discussed in the following parts.

### 2.3 Load Balance Server
Here I don't implement a real load balance algorithm for a simple demo. The program pick one replica randomly at a time.

#### Details
1. The server maintains a message queue, receiving all the commands sent by clients. 
2. It owns a *SelfState* index indicating a seperate state itself. Every time when it receives a command from client, a pair <*SelfState*,*Command*> will be pushed in the queue and then *SelfState* increases by one. 
3. It keeps listening for the states of all the database replicas, *ReplicaState*, and sends next command from the message queue to the picked replica to gossip **only when all the states of replicas reach a consensus and *SelfState* equals to *ReplicaState***, which is a synchronous **mechanism**.

Because gossip needs time to finish passing message to all replicas, this **mechanism** forces the replicas to gossip messages in order strictly. The *SelfState* and *ReplicaState* are seperate variables and change seperately. When they come to the same value, it means that the replicas have finished to gossip the last message exactly and ready for next one in message queue.

4. Besides commands from clients, the load balance server will also deal with messages from Database Replicas.
- Message asking for necessary information when a new replica is launched. Send back replica addresses as the neighbors of the new replica for gossip.
- Message of the state of replicas in a specific frequency. Update *ReplicaState*.

### 2.4 Database Replica Node
The database replicas synchronize the state and reach consensus by **gossip** protocol.

#### Gossip
The gossip protocol implemented here includes two behaviors:
- pull and push: It is used when a new replica is launched. 
    1. Get neighbors from load balance server.
    2. Send pull request to a neighbor asking for current state and database.
    3. Receive current state and database.
    4. push new message.
- push: push new message to a neighbor.
    New message includes:
    1. Command sent from load balance server.
    2. New replica address when a new replica node is launched. 

#### State
The replica node is implemented in a State Machine style. Every time a new message is received from other nodes, the state of this replica needs to update. The state is indicated by a variable seperately in each replica node. When a replica needs to send a new message, it wraps the message as <*state+1, message*> to gossip.

There will be three possible cases of the **index** of message and the **state** of a replica:
1. index < state: It means that the replica receives an old message. Ignore it.
2. index = state: It means that the replica receives duplicate message. Ignore it.
3. index = state+1: It means that the replica receives a new message. Extract valid data from the message and gossip to next neighbor.
The mechanism mentioned in 2.3 guarantees that cases of index>state+1 will never happen, because load balance server will not send new message to replicas until they reach consensus, which means that there will not be more than one new message gossip between replicas.
