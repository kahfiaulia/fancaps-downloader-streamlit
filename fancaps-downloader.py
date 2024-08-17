import os
import streamlit as st
import aiohttp
import asyncio
import zipfile
import io

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

async def download_image(session, url, subfolder, zipf, retries=3, delay=2):
    image_name = os.path.basename(url)
    image_path = f"{subfolder}/{image_name}"

    for attempt in range(retries):
        try:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                zipf.writestr(image_path, await response.read())
                return
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            st.warning(f"Attempt {attempt+1} failed for {url}: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                st.error(f"Failed to download {url} after {retries} attempts.")
                return

async def download_images_async(links_global, start_idx, end_idx, zip_name):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        async with aiohttp.ClientSession() as session:
            tasks = []
            semaphore = asyncio.Semaphore(5)
            
            async def bounded_download(url, subfolder):
                async with semaphore:
                    await download_image(session, url, subfolder, zipf)

            for idx in range(start_idx, end_idx):
                item = links_global[idx]
                subfolder = item['subfolder']
                links = item['links']

                tasks.extend(bounded_download(url, subfolder) for url in links)

            total_tasks = len(tasks)
            progress_bar = st.progress(0)
            completed_tasks = 0

            for task in asyncio.as_completed(tasks):
                try:
                    await task
                    completed_tasks += 1
                    progress_bar.progress(completed_tasks / total_tasks)
                except Exception as e:
                    st.error(f"Error in task: {e}")

            st.write(f"Completed processing subfolders: {start_idx} to {end_idx}")

    zip_buffer.seek(0)
    st.session_state[f'zip_buffer_{zip_name}'] = zip_buffer.getvalue()
    st.session_state[f'zip_file_name_{zip_name}'] = zip_name

def main():
    form = st.form(key='url_form')
    url_global = form.text_input(label='Enter URL')
    submit = form.form_submit_button(label='Submit')

    if submit:
        st.info("Starting the crawling process...")
        crawler = Crawler()
        links_global = crawler.crawl(url_global)

        if not links_global:
            st.warning("No links found.")
        else:
            num_subfolders = len(links_global)
            mid_point = num_subfolders // 2
            main_folder_name = links_global[0]['subfolder'].split('/')[0]

            if 'zip_buffer_first_half' not in st.session_state:
                st.write("Creating ZIP file for the first half...")
                try:
                    asyncio.run(download_images_async(links_global, 0, mid_point, f"{main_folder_name}_part_1.zip"))
                except Exception as e:
                    st.error(f"An error occurred: {e}")

            if 'zip_buffer_first_half' in st.session_state:
                st.download_button(
                    label=f"Download First Half ({st.session_state['zip_file_name_first_half']})",
                    data=st.session_state['zip_buffer_first_half'],
                    file_name=st.session_state['zip_file_name_first_half'],
                    mime="application/zip"
                )

                if 'zip_buffer_second_half' not in st.session_state:
                    st.write("Creating ZIP file for the second half...")
                    try:
                        asyncio.run(download_images_async(links_global, mid_point, num_subfolders, f"{main_folder_name}_part_2.zip"))
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

                if 'zip_buffer_second_half' in st.session_state:
                    st.download_button(
                        label=f"Download Second Half ({st.session_state['zip_file_name_second_half']})",
                        data=st.session_state['zip_buffer_second_half'],
                        file_name=st.session_state['zip_file_name_second_half'],
                        mime="application/zip"
                    )

if __name__ == "__main__":
    main()