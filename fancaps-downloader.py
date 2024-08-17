import os
import streamlit as st
import aiohttp
import asyncio
import zipfile
import io
import tempfile
from scraper.crawler import Crawler


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

async def download_image(session, url, subfolder, temp_file_path, retries=3, delay=2):
    image_name = os.path.basename(url)
    image_path = f"{subfolder}/{image_name}"

    for attempt in range(retries):
        try:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                with open(temp_file_path, 'wb') as temp_file:
                    temp_file.write(await response.read())
                return temp_file_path
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            st.warning(f"Attempt {attempt+1} failed for {url}: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                st.error(f"Failed to download {url} after {retries} attempts.")
                return None

async def download_images_async(links_global, main_folder_name):
    tasks = []
    semaphore = asyncio.Semaphore(5)
    
    async def bounded_download(url, subfolder, temp_file_path):
        async with semaphore:
            return await download_image(session, url, subfolder, temp_file_path)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        async with aiohttp.ClientSession() as session:
            for item in links_global:
                subfolder = item['subfolder']
                links = item['links']
                
                for link in links:
                    temp_file_path = os.path.join(temp_dir, os.path.basename(link))
                    tasks.append(bounded_download(link, subfolder, temp_file_path))
            
            completed_files = await asyncio.gather(*tasks)
    
        # Create the ZIP file with the downloaded images
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            for temp_file in completed_files:
                if temp_file:
                    arcname = os.path.basename(temp_file)
                    zipf.write(temp_file, arcname)
        
        zip_buffer.seek(0)
        zip_file_name = f"{main_folder_name}.zip"
        return zip_buffer.getvalue(), zip_file_name

def main():
    form = st.form(key='url_form')
    url_global = form.text_input(label='Enter URL')
    submit = form.form_submit_button(label='Submit')

    if submit:
        st.info("Starting the crawling process...")
        crawler = Crawler()
        all_batches = crawler.crawl(url_global)

        if not all_batches:
            st.warning("No links found.")
        else:
            selected_batches = [item for sublist in all_batches for item in sublist]

            if selected_batches:
                main_folder_name = selected_batches[0]['subfolder'].split('/')[0]
                st.write("Creating ZIP file...")

                try:
                    zip_data, zip_file_name = asyncio.run(download_images_async(selected_batches, main_folder_name))
                    st.session_state['zip_buffer'] = zip_data
                    st.session_state['zip_file_name'] = zip_file_name
                except Exception as e:
                    st.error(f"An error occurred: {e}")

        if 'zip_buffer' in st.session_state:
            st.download_button(
                label=f"Download {st.session_state['zip_file_name']}",
                data=st.session_state['zip_buffer'],
                file_name=st.session_state['zip_file_name'],
                mime="application/zip"
            )
            st.success("ZIP file is ready for download.")
        else:
            st.warning("No ZIP file available.")

if __name__ == "__main__":
    main()