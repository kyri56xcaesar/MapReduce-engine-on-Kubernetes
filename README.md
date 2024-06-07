# Project 2024 katanemimena K8S map reduce

## To-do

### User Interface Service ✓
- [x] Basic functionality
- [x] Sessions
- [x] Database
- [ ] Admin Panel
- [ ] Job posting

#### Authentication attached to UI
- [x] Basic functionality attached

### Manager Service
#### Workers are spawned and monitored by the Manager Service
- [x] API set
- [ ] Authorization control... (admin/user token)
- [x] Job Configuring
- [x] Hold Jobs in a db
- [ ] Job Submitting
- [ ] Initialization, talk to cluster.

### Shared File System
#### Basically K8S node/pod configurement (PVC: persistent volume claims etc)
- [ ] exploring...

### Distributed Data Service
#### Fault tolerance handling, can be Zookeeper or the K8S Built in features
- [ ] exploring...
