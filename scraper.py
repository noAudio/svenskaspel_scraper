from typing import List
import pyppeteer
from pyppeteer.browser import Browser
from pyppeteer.page import Page, ElementHandle


class Scraper:
    link: str = 'https://spela.svenskaspel.se/odds/sports/ishockey/sverige-hockeyallsvenskan'

    def __init__(self, link: str) -> None:
        # Set link to one provided by user
        # if available
        if link != '':
            self.link = link

    async def browserSetup(self) -> None:
        # TODO: Set to headless
        self.browser: Browser = await pyppeteer.launch(headless=False)
        self.page: Page = await self.browser.newPage()

    async def browserDisposal(self) -> None:
        await self.browser.close()

    async def getData(self) -> None:
        await self.browserSetup()
        await self.page.goto(url=self.link)
        title: str = await self.page.title()
        print('-> ', title)
        acceptCookieButton: ElementHandle | None = await self.page.querySelector('#onetrust-accept-btn-handler')
        if acceptCookieButton:
            await acceptCookieButton.click()
        self.listingElements: List[ElementHandle] = await self.page.querySelectorAll('#eventsWrapper-Center_LeagueViewResponsiveBlock_15984 > sb-comp > div > sb-lazy-render > div')
        print(len(self.listingElements))
        await self.browserDisposal()
