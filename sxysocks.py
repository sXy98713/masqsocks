import asyncio
import ast
from cipher import Cipher
BUFFER_SIZE = 65535
is_remote = True


def print_exception(e):
    print("Exception in code:")
    print(e)



class Connection:
    def __init__(self, reader, writer):
        #self._cipher = None
        self.header = b'GET /blog.html HTTP/1.1\r\nAccept:image/gif.image/jpeg,*/*\r\nAccept-Language:zh-cn\r\nConnection:Keep-Alive\r\nHost:localhost\r\nUser-Agent:Mozila/4.0(compatible;MSIE5.01;Window NT5.0)\r\nAccept-Encoding:gzip,deflate\r\nContent-Length:'
        self._reader = reader
        self._writer = writer

    async def readfromclient(self):
        data = await self._reader.read(BUFFER_SIZE)
        #print(data)

        return data
    

    async def write(self, data):
        self._writer.write(data)
        await self._writer.drain()

    async def close(self):
        self._writer.close()

    async def readfromremote(self):
        #bytes -> str
        #print(bs)
        #
        n = 0
        while (n < 7):
            line = await self._reader.readuntil(b'\r\n')
            n = n + 1
        line  = await self._reader.readuntil(b'\r\n\r\n')
        if line.split(b':')[0] == b'Content-Length':
            b_length = (line.split(b':')[1])[0: -4]
            length = int.from_bytes(b_length, byteorder = 'little')
            #print("from remote:")
            #print(length)
            msg = await self._reader.readexactly(length)
        #解密
        #self._cipher.decode(bytearray(data))
            return msg
        else:
            return None

    def encode(self, data):
        #加密
        #self._cipher.encode(data)
        #加头
        #print(str(len(data)))
        b_len = len(data).to_bytes((len(data).bit_length() + 7) // 8, byteorder='little')
        #print(b_len)
        msg = self.header + b_len + b'\r\n\r\n' + data
        #str -> bytes:
        return msg

    
async def copy_to(src: Connection, dst: Connection, remote2local: bool):
    try:
        while True:
            if remote2local:
                #去头解密后直接转发
                bs = await src.readfromremote()
                if not bs:
                #   print("copy done")
                   return          
                await dst.write(bs)
            else:
                bs = await src.readfromclient()
                #加密加头后转发
                #print("from client:")
                #print(len(bs))
                data = dst.encode(bs)
                await dst.write(data)
    except Exception as e:
        print(e)

