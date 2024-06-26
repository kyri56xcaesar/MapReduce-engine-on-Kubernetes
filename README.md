# Project 2024 katanemimena K8S map reduce


## HOW TO use locally.


1. run: minikube start --vm-driver=docker 
    or make sure it is running: minikube status

this will accomodate built the images directly to minikube
https://minikube.sigs.k8s.io/docs/handbook/pushing/#Windows

make sure to run the init system from a terminal on eval docker env
- linux: eval $(minikube docker-env)
- windows: & minikube -p minikube docker-env --shell powershell | Invoke-Expression



2. run: python or python3 init_system.py

use: client.py 


Testing Credentials:
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
- [x] Implement job submit/view

#### General
- [x] Organize/clean code
- [x] Testing/Fuzzing
- [ ] Automate Unit tests...
- [x] Set up in pods

### Manager Service
#### Workers are spawned and monitored by the Manager Service
- [x] API set
- [x] Job Configuring
- [x] Hold Jobs in a db, Propably will use ETCD for this
- [x] Formatting/setup
- [x] Initialization, talk to cluster.
- [x] Instantiate images on kubernetes and then apply logic to dynamically change inp/out
- [x] master/workers 
- [x] decide/reasses kind of manifests
- [x] automate process
- [x] provide access for Job status view
- [ ] provide access for results view..
- [ ] setup FTP server or sth for input/output of datafiles
- [ ] Optimize code
- [ ] Optimize process

### Shared File System
#### (PV & PVCs: persistent volume and persistent volume claims)
- [x] Kubernetes PV and PVCs. ON Manager

### Distributed Data Service
#### Fault tolerance! etcd Shall be used and  configured
- [x] etcd documentation reading
- [x] etcd installation
- [x] etcd configuration
- [x] etcd testing

etcd parematers of resource/limits should be adjusted per system...


# DEMO  vid#
https://youtu.be/pKnTrdCvqPk