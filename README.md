# A Simple Distributed Database Based on Gossip

> Ruiguang Li

I implement a simple distributed database based on gossip protocol.

## Usage
*Details of source files will be talked in next part*

1. Launch Load Balance Server first:
```bash
$ python LoadBalanceServer.py
```

2. Then launch several Database Node Server:
```bash
$ python DatabaseNode.py ip_address port
```

for example:
```bash
$ python DatabaseNode.py 127.0.0.1 10001
```
*Note that the Load Balance Server uses port 10000, so don't use it here.*

The output includes:
- state: current state of this node server
- neighbors: neighbor nodes information
- table: the table stored on this server

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

The database contains a simple table with only two attribute: name and age. By using the insert and delete command, corresponding record will be inserted to or deleted from the table. Table on each Database Node is shown by output of DatabaseNode.py.