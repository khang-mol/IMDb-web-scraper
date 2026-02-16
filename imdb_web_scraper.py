from bs4 import BeautifulSoup
from requests_html import HTMLSession

class IMDB_data:
    def __init__(self, url: str) -> None:
        self.url_topleveldomain = "https://www.imdb.com"
        self.url = self.url_topleveldomain + url if 'https' not in url else url
        self.session = HTMLSession()
        self.seasons_hrefs = []
        self.soup = None
        self.episode_ratings_full_series = []

    def get_soup(self):
        page_raw = self.session.get(url=self.url)
        self.soup = BeautifulSoup(page_raw.text, features="html.parser")
    
    def change_link_to_all_episodes(self) -> None:
        self.get_soup()
        episodes_header = self.soup.find(name='div', attrs={'data-testid': "episodes-header"})
        self.url = self.url_topleveldomain + episodes_header.find(name='a').attrs.get('href', 'Not found')

    def get_seasons_hrefs(self) -> list[str]:
        """Gets links for all seasons of a series."""
        seasons_div = self.soup.find(name='div', attrs={'class': "ipc-tabs ipc-tabs--base ipc-tabs--align-left ipc-tabs--display-chip ipc-tabs--inherit"})
        seasons_ul = seasons_div.find(name='ul', attrs={'role': "tablist"})
        seasons_all = seasons_ul.find_all(name='a')

        for season in seasons_all:
            href = season.attrs.get('href', 'Not found')
            self.seasons_hrefs.append(self.url_topleveldomain + href)

        return self.seasons_hrefs

    def get_episode_ratings(self) -> list[float]:
        rating_div = self.soup.find_all(name='div', attrs={'class': "sc-17ce9e4b-0 ddMjUi sc-64257d69-3 cwmoYC"})
        ratings = []
        for episode_rating in rating_div:
            rating = episode_rating.find(name='span').find(name='span', attrs={'class': "ipc-rating-star--rating"}).get_text()
            ratings.append(float(rating))

        return ratings

    def append_episode_ratings(self) -> list:
        self.get_soup()
        episode_ratings = self.get_episode_ratings()
        self.episode_ratings_full_series.append(episode_ratings)

    def get_episode_ratings_full_series(self) -> list:
        if 'episodes' not in self.url:
            self.change_link_to_all_episodes()
        self.append_episode_ratings()
        seasons_hrefs = self.get_seasons_hrefs()
        start = 1 if 'season' not in self.url else 0
        for url in seasons_hrefs[start:]:
            self.url = url
            self.append_episode_ratings()

        return self.episode_ratings_full_series



if __name__ == "__main__":
    session = HTMLSession()
    url = "https://www.imdb.com/title/tt0903747/?ref_=nv_sr_srsg_0_tt_8_nm_0_in_0_q_breaking"
    series = IMDB_data(url=url)
    episode_ratings_full_series = series.get_episode_ratings_full_series()
    print(episode_ratings_full_series)