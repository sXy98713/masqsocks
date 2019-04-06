from sxysocks import Connection, copy_to
import asyncio
import socket

async def start_remote(reader, writer):
    remoter = Connection(reader, writer)
    await handleConn(remoter)



async def handleConn(remoter: Connection):
    #解析socks协议
    buf = remoter.read()
    data = remoter.decode(buf)
    if not data or data[0] != 0x05:
        remoter.close()
        return
    else:
        await remoter.write(remoter.encode(bytearray(0x05,0x00)))
        buf = await remoter.read()
        if len(buf) < 7:
            remoter.close()
            return
        if buf[1] != 0x01:
            remoter.close()
            return
        dstip = None
        dstport = buf[-2:]
        dstport = int(dstport.hex(), 16)

        if(buf[3] == 0x01):
            dstip = socket.inet_ntop(socket.AF_INET, buf[4: 4 + 4])
        else:
            #暂不支持
            remoter.close()
            return
        await remoter.write(bytearray(0x05, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00))
        dst_reader, dst_writer = asyncio.open_connection(dstip, dstport)
        dst = Connection(dst_reader, dst_writer)
        await asyncio.gather(
            copy_to(remoter, dst, True),
            copy_to(dst, remoter, False)
        )

def main():
    port = 9713
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(start_remote, '127.0.0.1',port)
    server = loop.run_until_complete(coro)
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
        

