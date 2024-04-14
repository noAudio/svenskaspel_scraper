import asyncio

from scraper import Scraper


async def main() -> None:
    scraper: Scraper = Scraper('')
    await scraper.getData()

    if scraper.matches['svenskaspel']['match']:
        import xmltodict
        xmldata = xmltodict.unparse(scraper.matches, pretty=True)

        with open('betting.xml', 'w') as xmlFile:
            xmlFile.write(xmldata)


if __name__ == '__main__':
    import os
    os.environ['PYPPETEER_CHROMIUM_REVISION'] = '1263111'
    os.environ['PYPPETEER_HOME'] = '/tmp/'

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
