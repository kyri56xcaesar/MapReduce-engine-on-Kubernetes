# Project 2024 katanemimena K8S map reduce


## HOW TO USE so far.


run: minikube start --vm-driver=docker 
    or make sure it is running: minikube status

run: python or python3 init_system.py

use: client.py 


user: guest password
admin: admin password

*Warning* On windows for some reason requests aren't pulled through the kube proxy, *Solution*: port forward the UI and AUTH endpoints like:
On 2 seperate terminals:
    - kubectl port-forward service/authservice 30001:1337
    - kubectl port-forward service/uiservice 30002:1338

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
- [x] Job Configuring
- [ ] Hold Jobs in a db, Propably will use ETCD for this
- [x] Formatting/setup
- [x] Initialization, talk to cluster.
- [x] Instantiate images on kubernetes and then apply logic to dynamically change inp/out
- [x] master/workers 
- [x] decide/reasses kind of manifests
- [x] automate process
- [ ] provide access for Job status view

### Shared File System
#### (PV & PVCs: persistent volume and persistent volume claims)
- [x] Kubernetes PV and PVCs. ON Manager

### Distributed Data Service
#### Fault tolerance! etcd Shall be used and  configured
- [x] etcd documentation reading
- [ ] etcd installation
- [ ] etcd configuration
- [ ] etcd testing
 




# -> UI      :  Deployment
# -> Auth:  StatefulService
# -> Mngr: StatefulSet
# -> Workers: Jobs 
