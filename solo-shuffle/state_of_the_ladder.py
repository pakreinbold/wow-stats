from __future__ import annotations
import time
import datetime as dt
import requests
import scrapy
import pandas as pd

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"  # noqa

specializations = {
    'deathknight': ['frost', 'unholy'],
    'demonhunter': ['havoc'],
    'druid': ['balance', 'feral', 'restoration'],
    'evoker': ['devastation', 'preservation'],
    'hunter': ['beastmastery', 'marksmanship', 'survival'],
    'mage': ['arcane', 'fire', 'frost'],
    'monk': ['mistweaver', 'windwalker'],
    'paladin': ['holy', 'retribution'],
    'priest': ['discipline', 'holy', 'shadow'],
    'rogue': ['assassination', 'outlaw', 'subtlety'],
    'shaman': ['elemental', 'enhancement', 'restoration'],
    'warlock': ['affliction', 'demonology', 'destruction'],
    'warrior': ['arms', 'fury']
}


def make_url(class_: str, spec: str, page: int = 1) -> str:
    """Construct the url of the solo-shuffle leaderboard for the given class, spec, and page number

    Args:
        class_ (str): The WoW class we're interested in.
        spec (str): The class-specialization we're interested in.
        page (int, optional): The leaderboard page we want; each page contains 100
            characters/ranks. Defaults to 1.

    Returns:
        str: The solo-shuffle leaderboard url.
    """
    return (
        "https://worldofwarcraft.com/en-us/game/pvp/leaderboards"
        f"/shuffle/{class_}/{spec}?page={page}"
    )


def get_ratings(class_: str, spec: str, page: int = 1) -> pd.DataFrame:
    """Get a dataframe containing the names and ratings of players on a given solo-shuffle
    leaderboard page.

    Args:
        class_ (str): The WoW class we're interested in.
        spec (str): The class-specialization we're interested in.
        page (int, optional): The leaderboard page we want; each page contains 100
            characters/ranks. Defaults to 1.

    Returns:
        pd.DataFrame: Contains the names and ratings of players on that page of the leaderboard.
            cols: name, rating
    """
    url = make_url(class_, spec, page)
    html = requests.get(
        url, headers={"User-Agent": user_agent, }
    ).content
    selector = scrapy.Selector(text=html)

    row_xpath = '//div[@class="Pane-content"]//div[@class="SortTable-row"]'

    # Everything else is dynamic (and can't be scraped naively)
    names = (
        selector
        .xpath(row_xpath + '//div[@class="SortTable-col SortTable-data"]/@data-value')
        .extract()
    )
    ratings = (
        selector
        .xpath(row_xpath + '//div[@class="List-item"]/text()')
        .extract()
    )
    ratings = [int(rating) for rating in ratings]

    return pd.DataFrame({'name': names, 'rating': ratings})


def get_state_of_ladder(
    filter_classes: list[str] | None = None,
    page_depth: int = 10,
    save: bool = True
) -> pd.DataFrame:
    """Get solo-shuffle ratings for every page of every class-specialization. Saves the results to
    a csv.

    Args:
        filter_classes (list[str] | None, optional): A sub-set of classes we want to consider; if
            None is passed, get state of ladder for all classes. Defaults to None.
        page_depth (int): How many pages of each class to query. Defaults to 10 (max).
        save (bool): Whether or not to save the results; even if True, `filter_classes` must also
            be None, so that we don't save partial states. Defaults to True.

    Returns:
        pd.DataFrame: Contains the names and ratings of players on the leaderboard.
            cols: name, rating, class, spec
    """
    all_ratings = []
    response_times = []
    for class_, specs in specializations.items():
        if (
            (filter_classes is not None)
            and (class_ not in filter_classes)
        ):
            continue
        for spec in specs:
            for page in range(page_depth):
                start = time.time()
                print(f"Requesting data for {class_}-{spec}, page {page}")

                ratings = get_ratings(class_, spec, page + 1)

                ratings['class'] = class_
                ratings['spec'] = spec

                all_ratings.append(
                    ratings
                )
                response_time = time.time() - start
                response_times.append(response_time)
                print(f"Response took {response_time:.3f} s")

    all_ratings = pd.concat(all_ratings)
    print(f"Total time to scrape state of the ladder: {sum(response_times):.2f} s")

    if save and (filter_classes is None):
        print("Saving state of the ladder")
        save_name = f'state_of_the_ladder_{dt.date.today()}.csv'
        all_ratings.to_csv(save_name, index=False)

    return all_ratings


if __name__ == '__main__':
    # get_state_of_ladder(['warrior', 'hunter'], page_depth=2)
    get_state_of_ladder()
