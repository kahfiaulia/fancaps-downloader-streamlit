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
            all_pic_links = crawler.crawl(url)
            num_subfolders = len(all_pic_links)
            batch_size = num_subfolders // 2
            if batch_size == 0:
                batch_size = 1  # Ensure batch size is at least 1
            total_batches = (num_subfolders + batch_size - 1) // batch_size
            output = [all_pic_links[i*batch_size:(i+1)*batch_size] for i in range(total_batches)]
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