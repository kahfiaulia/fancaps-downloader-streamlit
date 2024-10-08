import streamlit as st

from scraper.url_support import UrlSupport
from scraper.crawlers import episode_crawler, season_crawler, movie_crawler
from scraper.utils.colors import Colors

class Crawler:
    def crawl(self, url):
        Colors.print(f"{url} crawling started:",Colors.YELLOW)

        urlSupport = UrlSupport()
        urlType = urlSupport.getType(url)
        if urlType == 'season':
            st.write(f"\t\"{urlType}\" url detected")
            crawler = season_crawler.SeasonCrawler()
            output = crawler.crawl(url)
        elif urlType == 'episode':
            st.write(f"\t\"{urlType}\" url detected")
            crawler = episode_crawler.EpisodeCrawler()
            output = [crawler.crawl(url)]
        elif urlType == 'movie':
            st.write(f"\t\"{urlType}\" url detected")
            crawler = movie_crawler.MovieCrawler()
            output = [crawler.crawl(url)]
        else:
            return []

        st.write(f"{url} crawling finished.")
        return output