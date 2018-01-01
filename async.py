import asyncio
import time

async def main(x):
    t0 = time.time()
    a = sum([i for i in range(x)])
    print("Function took: %.2f ms" % ((time.time() - t0) * 1000))

loop = asyncio.get_event_loop()
loop.run_until_complete(main(100000))

def sum_(x):
    t0 = time.time()
    a = sum([i for i in range(x)])
    print("Function took: %.2f ms" % ((time.time() - t0) * 1000))

sum_(100000)
