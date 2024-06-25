from venv import logger
import etcd3
from kubernetes import config, client
from tenacity import retry, wait_fixed

namespace = 'default'

def get_etcd_endpoints():
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    service_name = 'etcd'

    try:
        endpoints = v1.read_namespaced_endpoints(name=service_name, namespace=namespace)
        pod_ips = [addr.ip for subset in endpoints.subsets for addr in subset.addresses]
        return pod_ips
    except Exception as e:
        logger.info(f"Error retrieving endpoints: {e}")
        return []

@retry(wait=wait_fixed(2))
def put_with_lock(key, value):
    etcd_endpoints = get_etcd_endpoints()
    
    if etcd_endpoints:
        etcd = etcd3.client(host=etcd_endpoints[0],port = 2379)
        lock = etcd.lock(key,ttl=60)
        lock.acquire()
        etcd.put(key, value)
        lock.release()
    else:
        logger.info("Could not retrieve etcd endpoints")

def put(key, value):
    etcd_endpoints = get_etcd_endpoints()

    if etcd_endpoints:
        etcd = etcd3.client(host=etcd_endpoints[0],port = 2379)
        etcd.put(key, value)
    else:
        logger.info("Could not retrieve etcd endpoints")        
@retry(wait=wait_fixed(2))
def get_with_lock_increment(key):
    etcd_endpoints = get_etcd_endpoints()

    if etcd_endpoints:
        etcd = etcd3.client(host=etcd_endpoints[0],port = 2379)
        lock = etcd.lock(key,ttl=60)
        lock.acquire()
        value, _ = etcd.get(key)
        logger.info(value)
        if value is not None:
            int_val = int(value.decode('utf-8'))
            str_val = str(int_val + 1)
        else:
            str_val = str(1)        
        etcd.put(key,str_val)
        lock.release()
        return value.decode('utf-8') if value else None
    else:
        logger.info("Could not retrieve etcd endpoints")
        return None
    
@retry(wait=wait_fixed(2))
def get_with_lock(key):
    etcd_endpoints = get_etcd_endpoints()

    if etcd_endpoints:
        etcd = etcd3.client(host=etcd_endpoints[0],port = 2379)
        lock = etcd.lock(key,ttl=60)
        lock.acquire()
        value, _ = etcd.get(key)
        lock.release()
        return value.decode('utf-8') if value else None
    else:
        logger.info("Could not retrieve etcd endpoints")
        return None

def get(key):
    etcd_endpoints = get_etcd_endpoints()

    if etcd_endpoints:
        etcd = etcd3.client(host=etcd_endpoints[0],port = 2379)
        value, _ = etcd.get(key)
        return value.decode('utf-8') if value else None
    else:
        logger.info("Could not retrieve etcd endpoints")
        return None

def get_prefix(key):
    etcd_endpoints = get_etcd_endpoints()

    if etcd_endpoints:

        etcd = etcd3.client(host=etcd_endpoints[0],port = 2379)

        values = []

        for value , metadata in etcd.get_prefix(key):
            values.append(value.decode('utf-8'))  # Decode bytes to string

        return values if values else None
    else:
        logger.info("Could not retrieve etcd endpoints")
        return None