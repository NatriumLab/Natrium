import natrium.lakeHandler as lh
import asyncio

async def main():
    print(await lh.test.create().save())

asyncio.run(main())