import aiohttp
import asyncio
from datetime import datetime, timezone

class GBFPLC():
    def __init__(self):
        self.client = None
        self.ID = 0
        self.VER = None
        self.UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'

    def get_timestamp(self):
        return int(datetime.now(timezone.utc).replace(tzinfo=None).timestamp() * 1000)

    async def request(self):
        headers : dict[str, str] = {'Connection':'keep-alive', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en', 'Host': 'game.granbluefantasy.jp', 'Origin': 'https://game.granbluefantasy.jp', 'Referer': 'https://game.granbluefantasy.jp/', 'User-Agent':self.UA}
        response = await self.client.get("https://game.granbluefantasy.jp", headers=headers)
        async with response:
            if response.status == 200:
                return str(await response.read())
            else:
                raise Exception("HTTP Error " + str(response.status))

    async def query(self, path, payload=None):
        url = "https://game.granbluefantasy.jp" + path
        ts = self.get_timestamp()
        params = {}
        params["_"] = str(ts)
        params["t"] = str(ts+300) # second timestamp is always a bit further. No idea if a random number would be better
        params["uid"] = str(self.ID)
        headers : dict[str, str] = {'Connection':'keep-alive', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en', 'Host': 'game.granbluefantasy.jp', 'Origin': 'https://game.granbluefantasy.jp', 'Referer': 'https://game.granbluefantasy.jp/', 'User-Agent':self.UA, 'X-Requested-With':'XMLHttpRequest', 'X-VERSION':self.VER}
        if payload is None:
            response = await self.client.get(url, params=params, headers=headers)
        else:
            response = await self.client.post(url, params=params, headers=headers, json=payload)
        async with response:
            if response.status != 200:
                raise Exception("HTTP Error " + str(response.status))
            else:
                return True

    async def run(self):
        async with aiohttp.ClientSession() as self.client:
            try:
                page = await self.request()
                self.VER = page.split('/assets/')[1].split('/', 1)[0]
                await self.query("/tutorial/content/index/1")
                await self.query("/tutorial/content/termsofuse")
                await self.query("/tutorial/content/index/2/1")
                await self.query("/tutorial/save_sex", payload={"special_token": None, "sex": 0})
                page = await self.request()
                self.ID = int((page.split('"userId":')[1].split(',', 1)[0]).strip())
                print("GBF Playerbase:", self.ID - 1)
            except Exception as e:
                print(e)
                print("An exception occured")
                print("GBF might be unavailable or the script is outdated")

if __name__ == "__main__":
    asyncio.run(GBFPLC().run())