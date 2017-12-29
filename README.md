# A Simple Distributed Database Based on Gossip

> Ruiguang Li
> 李睿光 U201514899

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
