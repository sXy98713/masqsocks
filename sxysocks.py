import asyncio
from cipher import Cipher
BUFFER_SIZE = 4096
is_remote = True


def print_exception(e):
    print("Exception in code:")
    print(e)



class Connection:
    def __init__(self, reader, writer):
        #self._cipher = None
        self.header = {
            'Host': 'www.super-ping.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Accept': 'text/html, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36',
            'DNT': '1',
            'Referer': 'http://www.super-ping.com/?ping=www.google.com&locale=sc',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,ja;q=0.6'
        }
        self._reader = reader
        self._writer = writer


    async def read(self):
        data = await self._reader.read(BUFFER_SIZE)
        return data
    

    async def write(self, data):
        self._writer.write(data)
        await self._writer.drain()

    async def close(self):
        self._writer.close()

    async def decode(self, bs):
        data = bs.decode('utf-8')
        #去HTTP头
        data = data.split("\r\n\r\n")[1]
        #解密
        #self._cipher.decode(bytearray(data))
        return data


    async def encode(self, data):
        #加密
        #self._cipher.encode(data)
        #加头
        return (bytearray(self.header) + data)
    
async def copy_to(src: Connection, dst: Connection, remote2local: bool):
    try:
        while True:
            bs = src.reader.read()
            if not bs:
                print("copy done")
                break
            if remote2local: 
                #去头解密后直接转发
                data = src.decode(bs)
                await dst.write(data)
            else:
                #加密加头后转发
                await dst.write(dst.encode(bs))
    except Exception as e:
        print(e)

