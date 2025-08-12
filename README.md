# YouTube Code-Mix Ratio Web App

This Flask web application allows you to input a YouTube video code and download a CSV file containing tagged sentences from the video comments, along with their corresponding code-mix ratios (Hindi/English).

## Features
- Fetches comments from a YouTube video using the YouTube Data API v3
- Cleans and processes comments
- Tags each word in the comments as Hindi or English using the codeswitch library
- Computes the code-mix ratio for each sentence
- Provides a downloadable CSV file with results

## Setup Instructions

### 1. Clone the repository or copy the project files

### 2. Create and activate a Virtual environment
```
python -m venv env1
source env1/bin/activate
```


### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Set up your YouTube Data API key
- Open `app.py` and replace the value of `DEVELOPER_KEY` with your own [YouTube Data API v3 key](https://console.cloud.google.com/apis/dashboard).

### 4. Download codeswitch models (first run)
- The codeswitch library will automatically download the required models the first time you run the app.

### 5. Run the Flask app
```
python app.py
```

### 6. Open in your browser
Go to [http://127.0.0.1:5000/](http://127.0.0.1:3000/) and enter a YouTube video code to process.

## File Structure
- `app.py` - Main Flask application
- `process_comments.py`, `tags_using_codeswitch_library.py`, `compute_code_mix_ratio.py` - Logic integrated into the app
- `templates/index.html` - HTML template for the web interface
- `static/style.css` - CSS for the web interface

## Notes
- Make sure you have a valid YouTube Data API key with quota.
- The app requires internet access to fetch YouTube comments and download codeswitch models.
- For large videos, processing may take some time.
