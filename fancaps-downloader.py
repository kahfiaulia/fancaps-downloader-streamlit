import os
import streamlit as st
import requests
import zipfile
import io

from scraper.crawler import Crawler
from stqdm.stqdm import stqdm

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

st.title('Fancaps Downloader')
st.markdown(
    f'''Thanks to m-patino for the crawling code. His repo: <a href="https://github.com/m-patino/fancaps-downloader" target="_self">fancaps-downloader by m-patino</a>''',
    unsafe_allow_html=True
)
tutor = '''URL support:

https://fancaps.net/{tv|anime}/showimages.php?...: Url of season page
https://fancaps.net/{tv|anime}/episodeimages.php?...: Url of episode page
https://fancaps.net/movies/MovieImages.php?...: Url of movie page
'''
st.markdown(tutor)

def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

@st.cache_data
def crawl_and_download(url):
    crawler = Crawler()
    links_global = crawler.crawl(url)
    zip_buffer = io.BytesIO()

    main_folder = []
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        for item in links_global:
            if not main_folder:
                main_folder_name = item['subfolder'].split('/')[0]
                main_folder.append(main_folder_name)
            subfolder = item['subfolder']
            links = item['links']

            for url in stqdm(links):
                image_name = os.path.basename(url)
                
                try:
                    response = requests_retry_session().get(url, timeout=10)
                    response.raise_for_status()
                    image_path = f"{subfolder}/{image_name}"
                    zipf.writestr(image_path, response.content)
                except requests.exceptions.RequestException as e:
                    st.warning(f"Failed to download {url}: {e}")

    zip_buffer.seek(0)
    return zip_buffer, main_folder

form = st.form(key='url_form')
url_global = form.text_input(label='Enter URL')
submit = form.form_submit_button(label='Submit')

if submit:
    zip_buffer, main_folder = crawl_and_download(url_global)

    st.download_button(
        label="Download Images ZIP",
        data=zip_buffer,
        file_name=f"{main_folder[0]}.zip",
        mime="application/zip"
    )