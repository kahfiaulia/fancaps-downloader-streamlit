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

async def download_images_async(links_global, main_folder_name, start_idx, end_idx):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        async with aiohttp.ClientSession() as session:
            total_tasks = sum(len(item['links']) for item in links_global[start_idx:end_idx])
            progress_bar = st.progress(0)
            completed_tasks = 0

            semaphore = asyncio.Semaphore(5)

            async def bounded_download(url, subfolder):
                async with semaphore:
                    await download_image(session, url, subfolder, zipf)

            tasks = []
            for item in links_global[start_idx:end_idx]:
                subfolder = item['subfolder']
                links = item['links']

                tasks.extend(bounded_download(url, subfolder) for url in links)

            for task in asyncio.as_completed(tasks):
                try:
                    await task
                    completed_tasks += 1
                    progress_bar.progress(completed_tasks / total_tasks)
                except Exception as e:
                    st.error(f"Error in task: {e}")

            st.write(f"Completed processing subfolders from {start_idx} to {end_idx}.")

    zip_buffer.seek(0)
    zip_file_name = f"{main_folder_name}_{start_idx}_{end_idx}.zip"
    return zip_buffer.getvalue(), zip_file_name

def main():
    form = st.form(key='url_form')
    url_global = form.text_input(label='Enter URL')
    half_option = form.radio("Select which half to process:", ["First Half", "Second Half"])
    submit = form.form_submit_button(label='Submit')

    if submit:
        st.info("Starting the crawling process...")
        crawler = Crawler()
        all_batches = crawler.crawl(url_global)

        if not all_batches:
            st.warning("No links found.")
        else:
            num_batches = len(all_batches)
            mid_point = num_batches // 2

            if half_option == "First Half":
                start_batch, end_batch = 0, mid_point
            elif half_option == "Second Half":
                start_batch, end_batch = mid_point, num_batches

            # Flatten the selected batches into a single list
            selected_batches = [item for sublist in all_batches[start_batch:end_batch] for item in sublist]

            if selected_batches:
                main_folder_name = selected_batches[0]['subfolder'].split('/')[0]
                st.write(f"Creating ZIP file for the {half_option.lower()}...")

                try:
                    zip_data, zip_file_name = asyncio.run(download_images_async(selected_batches, main_folder_name, 0, len(selected_batches)))
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