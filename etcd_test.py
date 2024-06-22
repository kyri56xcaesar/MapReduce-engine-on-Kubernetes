import etcd3
import asyncio

async def get_value_from_etcd():
    client = etcd3.client(host='localhost', port=2379)
    value, metadata = await client.get('greeting')
    print(f'Key: my_key, Value: {value.decode("utf-8")}')

loop = asyncio.get_event_loop()
loop.run_until_complete(get_value_from_etcd())