import asyncio
from time import time
from zero import AsyncZeroClient

zero_client = AsyncZeroClient("localhost", 5559)

async def test_benchmark():
    n = 10000
    t1 = time()
    for _ in range(n):
        res = await zero_client.call('t', (1, 2))
    t2 = time()
    print(f"{(t2-t1)/n} s/seq, {n/(t2-t1)} seq/s")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_benchmark())