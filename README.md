# Project 2024 katanemimena K8S map reduce

Submition day 28/6/2024.

# How to use on Okeanos cluster
Just call the init system.py. The script will just apply all the needed manifests. Docker images are pulled from my dockerhub registry:
kyri56xcaesar/katanemimena:<image> (managerakis, mapper, reducer, uiservice, authservice)

then use client.py..


User: admin, password: password
User: guest, password: password


Overall difference with master is the kube namespace. Here it is set to 'dpyravlos'. The code was quite sloppy in this manner, in order to change the namespace inside, you need to dig a bit...
AND the client script is adjusted to lookup cluster node ips correctly...




