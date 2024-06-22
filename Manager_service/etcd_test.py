import etcd3

etcd = etcd3.client(host='10.244.0.55', port=2379)

etcd.get('foo')
etcd.put('bar', 'doot')

print(etcd.get('greeting'))