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
- [x] Job Configuring
- [x] Hold Jobs in a db
- [x] Formatting/setup
- [ ] Initialization, talk to cluster.
- [ ] master/workers 

### Shared File System
#### Basically K8S node/pod configurement (PVC: persistent volume claims etc)
- [ ] K8S builtin setup...

### Distributed Data Service
#### Fault tolerance handling, can be Zookeeper or the K8S Built in features
- [ ] K8S builting setup...





# -> UI      :  Deployment
# -> Auth:  StatefulService
# -> Mngr: StatefulSet
# -> Workers: Jobs or Replica Sets or Services