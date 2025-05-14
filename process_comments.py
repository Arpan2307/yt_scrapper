import pandas as pd
import re
import string
import emoji
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Replace with your YouTube API Key
DEVELOPER_KEY = "AIzaSyD3emiSTH3PqUQnqYZdiCh33DZE72lpfEw"
# Replace with the video ID of the YouTube video
VIDEO_ID = "7JcJo_gAUAM"

def remove_emojis(text):
    return emoji.replace_emoji(text, replace='')

def clean_comment(comment):
    comment = comment.lower()
    comment = comment.translate(str.maketrans('', '', string.punctuation))
    comment = remove_emojis(comment)
    comment = comment.strip()
    return comment

def get_comments(video_id, part="snippet", max_results=1000):
    youtube = build("youtube", "v3", developerKey=DEVELOPER_KEY)
    comments = []
    next_page_token = None
    fetched = 0
    try:
        while fetched < max_results:
            request = youtube.commentThreads().list(
                part=part,
                videoId=video_id,
                textFormat="plainText",
                maxResults=min(100, max_results - fetched),
                pageToken=next_page_token
            )
            response = request.execute()
            for item in response["items"]:
                comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                likes = item["snippet"]["topLevelComment"]["snippet"]["likeCount"]
                comments.append({"comment": comment_text, "num_of_likes": likes})
                fetched += 1
                if fetched >= max_results:
                    break
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        return comments
    except HttpError as error:
        print(f"An HTTP error {error.http_status} occurred:\n {error.content}")
        return None

def process_and_save_comments(comments, output_file):
    cleaned_comments = [clean_comment(c) for c in comments]
    # Remove empty lines and lines that are just whitespace
    cleaned_comments = [c for c in cleaned_comments if c.strip()]
    with open(output_file, 'w', encoding='utf-8') as f:
        idx = 1
        buffer = []
        for comment in cleaned_comments:
            # Remove numbers from the comment text
            comment_no_numbers = ''.join([ch for ch in comment if not ch.isdigit()])
            comment_no_numbers = comment_no_numbers.strip()
            if comment_no_numbers:
                # If the comment contains line breaks, merge into one line
                single_line = ' '.join(comment_no_numbers.splitlines())
                single_line = ' '.join(single_line.split())  # Remove extra spaces
                f.write(f"{idx}\t{single_line}\n")
                idx += 1

def main():
    # Option 1: Fetch from YouTube API
    comments_data = get_comments(VIDEO_ID)
    if comments_data:
        comments = [c['comment'] for c in comments_data]
        process_and_save_comments(comments, 'cleaned_comments_from_api.txt')
        print('Fetched, cleaned, and saved comments from YouTube API.')
   
if __name__ == "__main__":
    main()
