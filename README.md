# Project 2024 katanemimena K8S map reduce

## To-do

### User Interface

#### Auth Service
- [x] Separated from UI service
- [x] Authentication
- [x] Database
- [x] Token (JWT) issuing
- [x] Generate RSA keys
- [x] Expose public key
- [x] Implement admin commands

#### UI Service
- [x] Redesigned completely
- [x] Command interface
- [x] Get public key from Auth service
- [x] Token verification with RSA256
- [x] Privilege verification
- [ ] Implement roles in JWT payload

#### Client script
- [x] Redesigned accordingly
- [x] Implemented as a CLI tool
- [x] Accepts modes/options
- [ ] Implement job submit/view

#### General
- [ ] Organize/clean code
- [ ] Testing/Fuzzing
- [ ] Set up in pods

### Manager Service
#### Workers are spawned and monitored by the Manager Service
- [x] API set
- [ ] Authorization control... (admin/user token)
- [x] Job Configuring
- [x] Hold Jobs in a db
- [x] Formatting/setup
- [ ] Initialization, talk to cluster.
- [ ] Job Submitting

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
