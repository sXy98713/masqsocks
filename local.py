import asyncio

from sxysocks import Connection
from sxysocks import copy_to

async def start_local(reader, writer):
    try:
        
        local_server = Connection(reader, writer)
        
        remote_reader, remote_writer = await asyncio.open_connection('39.97.110.59',8008)
        remote_server = Connection(remote_reader, remote_writer)
        task = [copy_to(local_server, remote_server, False), copy_to(remote_server, local_server, True)]
        await asyncio.wait(task)
    except Exception as e:
        print(e)


async def main():
    port = 8008
    print(port)
    local_server = await asyncio.start_server(start_local, '127.0.0.1',port)
    addr = local_server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with local_server:
        await local_server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())



    
