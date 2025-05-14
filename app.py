from flask import Flask, request, send_file, render_template, render_template_string
import os
import csv
import tempfile
import io

# Import or copy logic from your existing scripts
# For this example, we assume the following functions are available:
# - fetch_and_clean_comments(video_code, output_file)
# - tag_sentences(input_file, output_file)
# - compute_code_mix_ratio_for_file(tagged_file, output_csv)

# You will need to adapt your existing .py files into importable functions or copy their logic here.

app = Flask(__name__)

HTML_FORM = '''
<!doctype html>
<title>YouTube Code-Mix Ratio</title>
<h2>Enter YouTube Video Code</h2>
<form method=post enctype=multipart/form-data>
  <input type=text name=video_code required>
  <input type=submit value=Process>
</form>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None
    if request.method == 'POST':
        video_code = request.form['video_code']
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                cleaned_comments = os.path.join(tmpdir, 'cleaned_comments.txt')
                tagged_comments = os.path.join(tmpdir, 'tagged_comments.txt')
                output_csv = os.path.join(tmpdir, 'output.csv')

                fetch_and_clean_comments(video_code, cleaned_comments)
                tag_sentences(cleaned_comments, tagged_comments)
                compute_code_mix_ratio_for_file(tagged_comments, output_csv)

                # Read the CSV into memory before the tempdir is deleted
                with open(output_csv, 'rb') as f:
                    csv_bytes = io.BytesIO(f.read())
                csv_bytes.seek(0)
                return send_file(csv_bytes, as_attachment=True, download_name=f'{video_code}_codemix.csv', mimetype='text/csv')
        except Exception as e:
            error = str(e)
    return render_template('index.html', error=error)

# --- Below, adapt your existing logic into functions ---
def fetch_and_clean_comments(video_code, output_file):
    # Adapted from process_comments.py
    from googleapiclient.discovery import build
    import string
    import emoji
    
    DEVELOPER_KEY = "AIzaSyD3emiSTH3PqUQnqYZdiCh33DZE72lpfEw"  # <-- Replace with your API key
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
        while fetched < max_results:
            request = youtube.commentThreads().list(
                part=part,
                videoId=video_id,
                textFormat="plainText",
                maxResults=min(1000, max_results - fetched),
                pageToken=next_page_token
            )
            response = request.execute()
            for item in response["items"]:
                comment_text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                comments.append(comment_text)
                fetched += 1
                if fetched >= max_results:
                    break
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        return comments
    def process_and_save_comments(comments, output_file):
        cleaned_comments = [clean_comment(c) for c in comments]
        cleaned_comments = [c for c in cleaned_comments if c.strip()]
        with open(output_file, 'w', encoding='utf-8') as f:
            idx = 1
            for comment in cleaned_comments:
                comment_no_numbers = ''.join([ch for ch in comment if not ch.isdigit()])
                comment_no_numbers = comment_no_numbers.strip()
                if comment_no_numbers:
                    single_line = ' '.join(comment_no_numbers.splitlines())
                    single_line = ' '.join(single_line.split())
                    f.write(f"{idx}\t{single_line}\n")
                    idx += 1
    comments = get_comments(video_code)
    process_and_save_comments(comments, output_file)

def tag_sentences(input_file, output_file):
    # Adapted from tags_using_codeswitch_library.py
    from codeswitch.codeswitch import LanguageIdentification
    lid = LanguageIdentification('hin-eng')
    def merge_subwords(tokens):
        merged = []
        current_word = ''
        current_tag = ''
        for token in tokens:
            word = token.get('word', '')
            entity = token.get('entity', '').upper()
            lang = 'HI' if entity == 'HIN' else 'EN'
            if word.startswith('##'):
                current_word += word[2:]
            else:
                if current_word:
                    merged.append(f"{current_word}/{current_tag}")
                current_word = word
                current_tag = lang
        if current_word:
            merged.append(f"{current_word}/{current_tag}")
        return merged
    with open(input_file, 'r', encoding='utf-8') as fin, open(output_file, 'w', encoding='utf-8') as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            if not line[0].isdigit():
                fout.write(line + '\n')
                continue
            try:
                idx, sentence = line.split('\t', 1)
            except ValueError:
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    idx, sentence = parts
                else:
                    fout.write(line + '\n')
                    continue
            result = lid.identify(sentence)
            if isinstance(result, list):
                merged_output = merge_subwords(result)
                fout.write(f"{idx}\t{' '.join(merged_output)}\n")
            else:
                fout.write(f"{idx}\tERROR\n")

def compute_code_mix_ratio_for_file(tagged_file, output_csv):
    # Adapted from compute_code_mix_ratio.py
    def compute_code_mix_ratio(tagged_line):
        tokens = tagged_line.strip().split()
        if not tokens:
            return 0.0
        hi_count = sum(1 for t in tokens if t.endswith('/HI'))
        en_count = sum(1 for t in tokens if t.endswith('/EN'))
        total = hi_count + en_count
        if total == 0:
            return 0.0
        return min(hi_count, en_count) / total

    with open(tagged_file, 'r', encoding='utf-8') as fin, open(output_csv, 'w', encoding='utf-8', newline='') as fout:
        writer = csv.writer(fout)
        writer.writerow(['idx', 'tagged_sentence', 'code_mix_ratio'])
        for line in fin:
            line = line.strip()
            if not line or not line[0].isdigit():
                continue
            try:
                idx, tagged = line.split('\t', 1)
            except ValueError:
                continue
            ratio = compute_code_mix_ratio(tagged)
            writer.writerow([idx, tagged, f"{ratio:.2f}"])

if __name__ == '__main__':
    app.run(debug=True)
