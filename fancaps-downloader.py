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
                st.write(f"Downloaded: {image_path}")
                return  # Exit if the download succeeds
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            st.warning(f"Attempt {attempt+1} failed for {url}: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)  # Wait before retrying
    else:
        st.error(f"Failed to download {url} after {retries} attempts.")
        return

async def download_images_async(links_group, main_folder_name, part_number):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        async with aiohttp.ClientSession() as session:
            total_tasks = sum(len(item['links']) for item in links_group)
            progress_bar = st.progress(0)
            completed_tasks = 0
            for item in links_group:
                subfolder = item['subfolder']
                links = item['links']

                st.write(f"Processing subfolder: **{subfolder}**")

                tasks = [
                    download_image(session, url, subfolder, zipf)
                    for url in links
                ]

                for task in asyncio.as_completed(tasks):
                    await task
                    completed_tasks += 1
                    progress_bar.progress(completed_tasks / total_tasks)

                st.write(f"Completed processing subfolder: **{subfolder}**")

    zip_buffer.seek(0)
    zip_file_name = f"{main_folder_name}_part_{part_number}.zip"
    st.download_button(
        label=f"Download {zip_file_name}",
        data=zip_buffer,
        file_name=zip_file_name,
        mime="application/zip"
    )
    st.success(f"{zip_file_name} is ready for download.")

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
            main_folder_name = links_global[0]['subfolder'].split('/')[0]

            total_subfolders = len(links_global)
            if total_subfolders >= 6:
                subfolder_groups = [links_global[i:i+3] for i in range(0, total_subfolders, 3)]
                for idx, group in enumerate(subfolder_groups, start=1):
                    st.write(f"Creating ZIP file part {idx}...")
                    asyncio.run(download_images_async(group, main_folder_name, idx))
            else:
                st.write("Creating a single ZIP file...")
                asyncio.run(download_images_async(links_global, main_folder_name, 1))

        st.success("All processes completed.")

if __name__ == "__main__":
    main()