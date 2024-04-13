import asyncio

from scraper import Scraper


async def main() -> None:
    # TODO: Prompt user
    # TODO: Display filename when scraping is done
    scraper: Scraper = Scraper('')
    await scraper.getData()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
