# Fancaps Downloader Streamlit

## Acknowledgements <a name = "acknowledgenents"></a>

This project is made possible thanks to the amazing work done by the [fancaps-downloader](https://github.com/m-patino/fancaps-downloader) repository, created and maintained by [m-patino](https://github.com/m-patino). 

## Getting Started <a name = "getting_started"></a>

### Prerequisites

To run this script you need to have Python 3.x installed, the Beautifulsoup4, stqdm, request, and Streamlit library:

#### python install: 
https://www.python.org/downloads/

#### Requirements install: 
```
pip install -r requirements.txt
```

## Usage <a name = "usage"></a>

### Streamlit run: 
```
streamlit run fancaps-downloader.py
```

### Input:
Input URL in the text box, and press submit button. Then download the zipped file.

### URL Support:
* `https://fancaps.net/{tv|anime}/showimages.php?...`: Url of season page
* `https://fancaps.net/{tv|anime}/episodeimages.php?...`: Url of episode page
* `https://fancaps.net/movies/MovieImages.php?...`: Url of movie page

