import os
import streamlit as st
import requests
import zipfile
import io

from scraper.crawler import Crawler
from stqdm.stqdm import stqdm


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

def create_zip_files(links_global, main_folder_name):
    zip_buffers = []
    subfolder_groups = [links_global[i:i+3] for i in range(0, len(links_global), 3)]
    
    for i, group in enumerate(subfolder_groups):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            for item in group:
                subfolder = item['subfolder']
                links = item['links']

                for url in stqdm(links):
                    image_name = os.path.basename(url)
                    response = requests.get(url)
                    response.raise_for_status()
                    image_path = f"{subfolder}/{image_name}"
                    zipf.writestr(image_path, response.content)
        
        zip_buffer.seek(0)
        zip_buffers.append((f"{main_folder_name}_part_{i+1}.zip", zip_buffer))
        st.write(f"{main_folder_name}_part_{i+1}.zip ready")

    return zip_buffers

form = st.form(key='url_form')
url_global = form.text_input(label='Enter URL')
submit = form.form_submit_button(label='Submit')

main_folder = []

if submit:
    # Crawl
    crawler = Crawler()
    links_global = crawler.crawl(url_global)
    
    if links_global:
        main_folder_name = links_global[0]['subfolder'].split('/')[0]
        main_folder.append(main_folder_name)
        
        if len(links_global) >= 6:
            zip_files = create_zip_files(links_global, main_folder_name)
            
            for file_name, zip_buffer in zip_files:
                st.download_button(
                    label=f"Download {file_name}",
                    data=zip_buffer,
                    file_name=file_name,
                    mime="application/zip"
                )
        else:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                for item in links_global:
                    subfolder = item['subfolder']
                    links = item['links']

                    for url in stqdm(links):
                        image_name = os.path.basename(url)
                        response = requests.get(url)
                        response.raise_for_status()
                        image_path = f"{subfolder}/{image_name}"
                        zipf.writestr(image_path, response.content)
                
                st.write(f"{subfolder} done.")

            zip_buffer.seek(0)

            st.download_button(
                label="Download Images ZIP",
                data=zip_buffer,
                file_name=f"{main_folder[0]}.zip",
                mime="application/zip"
            )