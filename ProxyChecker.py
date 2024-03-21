import aiohttp
import asyncio
import json

async def test_proxy(session, proxy, test_url='http://www.example.com', timeout=5):
    try:
        async with session.get(test_url, proxy=f"http://{proxy}", timeout=timeout) as response:
            if response.status == 200:
                return proxy
    except:
        return None

async def fetch_and_verify_proxies(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            proxy_list = (await response.text()).splitlines()

    tasks = [test_proxy(session, proxy) for proxy in proxy_list]
    working_proxies = [proxy for proxy in await asyncio.gather(*tasks) if proxy]

    with open('proxies.json', 'w') as f:
        json.dump(working_proxies, f, indent=4)

    print("Working proxies saved to proxies.json")

# URL of the free proxy list
def check_proxy():
    proxy_list_url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies"
    asyncio.run(fetch_and_verify_proxies(proxy_list_url))
