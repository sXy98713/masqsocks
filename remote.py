from sxysocks import Connection, copy_to
import asyncio
import socket


async def start_remote(reader, writer):
    try:
        local = Connection(reader, writer)
        dst = await handleConn(local)
        task = [copy_to(local, dst, True), copy_to(dst, local, False)]
        await asyncio.wait(task)
    except Exception as e:
        print(e)


async def handleConn(remoter: Connection):
    #解析socks协议
    data = await remoter.readfromlocal()
    print("from local:")
    print(data)
    if not data or data[0] != 0x05:
        await remoter.close()
        return
    else:
        await remoter.write(remoter.encode(b'\x05\x00'))
        buf = await remoter.readfromlocal()
        #print(data)
        #print(buf)
        print(len(buf))
        if len(buf) < 7:
            await remoter.close()
            return
        if buf[1] != 0x01:
            #Only support CONNECT
            await remoter.close()
            return
        dstip = None
        dstport = buf[-2:]
        dstport = int(dstport.hex(), 16)
        if buf[3] == 0x01:
            #IPV4
            dstip = socket.inet_ntop(socket.AF_INET, buf[4: 4 + 4])
        elif buf[3] == 0x03:
            #域名(地址第一个字节为域名长度)
            hostlen = int.from_bytes(buf[4], byteorder = 'little')
            host = buf[5:5 + hostlen]
            dstip = socket.gethostbyname(host)
        else:
            #IPV6
            dstip = buf[4: 4 + 16]
        #addr = {dstip, dstport)
        #print("connect to {addr}")
        await remoter.write(remoter.encode(b'\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00'))
        dst_reader, dst_writer = await asyncio.open_connection(dstip, dstport)
        dst = Connection(dst_reader, dst_writer)
        return dst

async def main():
    port = 8008
    remote_server = await asyncio.start_server(start_remote, '172.17.148.114',port)
    addr = remote_server.sockets[0].getsockname()
    print(f'Serving on {addr}')
    async with remote_server:
        await remote_server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
