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
    
    def crawl_in_batches(self, url, batch_size):
        urlSupport = UrlSupport()
        urlType = urlSupport.getType(url)

        if urlType == 'season':
            crawler = season_crawler.SeasonCrawler()  # SeasonCrawler instance
            all_pic_links = crawler.crawl(url)
            total_batches = (len(all_pic_links) + batch_size - 1) // batch_size
            return [all_pic_links[i*batch_size:(i+1)*batch_size] for i in range(total_batches)]
        else:
            raise ValueError(f"Batch processing is only supported for 'season' type URLs.")