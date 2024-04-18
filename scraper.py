from time import sleep
from typing import Dict, List
import pyppeteer
from pyppeteer.browser import Browser
from pyppeteer.page import Page, ElementHandle
from pyppeteer.frame_manager import Frame
from pyppeteer.execution_context import JSHandle


class Scraper:
    link: str = ''
    matches: Dict[str, Dict[str, List[Dict[str, Dict[str, str]]]]] = {
        'svenskaspel': {
            'match': [],
        }
    }

    def __init__(self, link: str) -> None:
        self.link = link

    async def browserSetup(self) -> None:
        self.browser: Browser = await pyppeteer.launch(headless=True)
        self.page: Page = await self.browser.newPage()

    async def browserDisposal(self) -> None:
        print('→ Closing browser.')
        await self.browser.close()

    async def getGameDetails(self) -> None:
        if self.link == '':
            # break execution when a link
            # isn't given
            print('→ A link was not provided, aborting.')
            return

        await self.browserSetup()
        print('→ Successfully launched browser.')
        await self.page.goto(url='https://spela.svenskaspel.se/odds/live-betting')

        acceptCookieButton: ElementHandle | None = await self.page.querySelector('#onetrust-accept-btn-handler')
        if acceptCookieButton:
            print('→ Closing cookie consent modal.')
            await acceptCookieButton.click()
            await self.page.waitForNavigation()

        # Target iframe holding the data
        iframe: ElementHandle | None = await self.page.querySelector('iframe.sbtech')
        contentFrame: Frame | None = None
        if iframe:
            contentFrame = await iframe.contentFrame()

        if contentFrame:
            # switch to hockey tab
            await contentFrame.waitForSelector('.rj-carousel-item', {'timeout': 60000})
            jsEval = """
                const xpathExpression = '//*[@id="sports-carouselLeft_LiveNowBettingResponsiveBlock_15977"]/sb-comp/div/div/div[2]/div[3]';
                const element = document.evaluate(xpathExpression, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (element) {
                    element.click();
                }
                """
            await contentFrame.evaluate(jsEval)

            # find game on page
            await contentFrame.waitForSelector('.rj-ev-list__ev-card__event-info', {'timeout': 60000})
            gameElements: List[ElementHandle] = await contentFrame.querySelectorAll('.rj-ev-list__ev-card__event-info')
            desiredElement: ElementHandle | None = None
            gameID: str = self.link.split('#')[-1]
            for elem in gameElements:
                href: str = await contentFrame.evaluate('(element) => element.getAttribute("href")', elem)
                href = href.split('#')[-1]
                if href == gameID:
                    desiredElement = elem
            if desiredElement:
                await contentFrame.evaluate('(element) => element.click()', desiredElement)
                await self.page.waitForNavigation()
            else:
                print('→ Unable to find the page for the provided link.')
                return

            sleep(5)
            gameScoreElement: ElementHandle | None = None
            # target first score element
            gameScoreElement: ElementHandle | None = await contentFrame.querySelector(
                '.rj-market')

            hometeam: str = ''
            awayteam: str = ''
            odds1: str = ''
            oddsx: str = ''
            odds2: str = ''

            if gameScoreElement:
                # get team names
                teamNames: List[str] = []
                teamNameElements: List[ElementHandle] = await gameScoreElement.querySelectorAll('.rj-market__button-title')
                for elem in teamNameElements:
                    textJsonValue: JSHandle = await elem.getProperty('textContent')
                    text: str = await textJsonValue.jsonValue()
                    teamNames.append(text)
                if len(teamNames) == 3:
                    hometeam = teamNames[0]
                    awayteam = teamNames[2]
                    print(f'→ Found "{hometeam}" vs "{awayteam}"')

                # get odds
                odds: List[str] = []
                oddsElements: List[ElementHandle] = await gameScoreElement.querySelectorAll('.rj-market__button-odds')
                for elem in oddsElements:
                    textJsonValue: JSHandle = await elem.getProperty('textContent')
                    text: str = await textJsonValue.jsonValue()
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

        else:
            print('→ No stats were found.')
            await self.page.screenshot({'path': 'screenshot.png'})

        await self.browserDisposal()

    # WARN: Deprecated
    async def getData(self) -> None:
        await self.browserSetup()
        print('→ Successfully launched browser.')
        await self.page.goto(url=self.link)

        acceptCookieButton: ElementHandle | None = await self.page.querySelector('#onetrust-accept-btn-handler')
        if acceptCookieButton:
            print('→ Closing cookie consent modal.')
            await acceptCookieButton.click()

        # Target iframe holding the data
        iframe: ElementHandle | None = await self.page.querySelector('iframe.sbtech')
        contentFrame: Frame | None = None
        if iframe:
            contentFrame = await iframe.contentFrame()

        if contentFrame:
            await contentFrame.waitForSelector('.rj-ev-list__ev-card', {'timeout': 60000})
            self.listingElements: List[ElementHandle] = await contentFrame.querySelectorAll('.rj-ev-list__ev-card')
            print('→ Found data iframe element.')
        if self.listingElements.__len__() > 0:
            print(f'→ Found {len(self.listingElements)} matches.')
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
                        text: str = await textJsonValue.jsonValue()
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
        else:
            print('→ No matches were found.')
            await self.page.screenshot({'path': 'screenshot.png'})

        await self.browserDisposal()
