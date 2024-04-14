from typing import Dict, List
import pyppeteer
from pyppeteer.browser import Browser
from pyppeteer.page import Page, ElementHandle
from pyppeteer.frame_manager import Frame
from pyppeteer.execution_context import JSHandle


class Scraper:
    link: str = 'https://spela.svenskaspel.se/odds/sports/ishockey/sverige-hockeyallsvenskan'
    matches: Dict[str, Dict[str, List[Dict[str, Dict[str, str]]]]] = {
        'svenskaspel': {
            'match': [],
        }
    }

    def __init__(self, link: str) -> None:
        # Set link to one provided by user
        # if available
        if link != '':
            self.link = link

    async def browserSetup(self) -> None:
        self.browser: Browser = await pyppeteer.launch(headless=True)
        self.page: Page = await self.browser.newPage()

    async def browserDisposal(self) -> None:
        await self.browser.close()

    async def getData(self) -> None:
        await self.browserSetup()
        await self.page.goto(url=self.link)

        acceptCookieButton: ElementHandle | None = await self.page.querySelector('#onetrust-accept-btn-handler')
        if acceptCookieButton:
            await acceptCookieButton.click()

        # Target iframe holding the data
        iframe: ElementHandle | None = await self.page.querySelector('iframe.sbtech')
        contentFrame: Frame | None = None
        if iframe:
            contentFrame = await iframe.contentFrame()

        if contentFrame:
            self.listingElements: List[ElementHandle] = await contentFrame.querySelectorAll('.rj-ev-list__ev-card')
        if self.listingElements.__len__() > 0:
            for match in self.listingElements:
                hometeamElement: ElementHandle | None = await match.querySelector('.rj-ev-list__ev-card__team-1-name')
                hometeam: str = ''
                if hometeamElement:
                    hometeamJsonValue: JSHandle = await hometeamElement.getProperty('textContent')
                    hometeam = await hometeamJsonValue.jsonValue()

                awayteamElement: ElementHandle | None = await match.querySelector('.rj-ev-list__ev-card__team-2-name')
                awayteam: str = ''
                if awayteamElement:
                    awayteamJsonValue: JSHandle = await awayteamElement.getProperty('textContent')
                    awayteam = await awayteamJsonValue.jsonValue()

                oddsElements: List[ElementHandle] = await match.querySelectorAll('.rj-ev-list__bet-btn__odd')
                odds1: str = ''
                oddsx: str = ''
                odds2: str = ''
                odds: List[str] = []
                if len(oddsElements) == 3:
                    for elem in oddsElements:
                        textJsonValue: JSHandle = await elem.getProperty('textContent')
                        text = await textJsonValue.jsonValue()
                        odds.append(text)
                if len(odds) == 3:
                    odds1 = odds[0]
                    oddsx = odds[1]
                    odds2 = odds[2]

                self.matches['svenskaspel']['match'].append({
                    'teams': {
                        'hometeam': hometeam,
                        'awayteam': awayteam,
                    },
                    'odds': {
                        'odds1': odds1,
                        'oddsx': oddsx,
                        'odds2': odds2,
                    },
                })

        await self.browserDisposal()
