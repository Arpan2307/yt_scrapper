# Script to compute code-mix ratio for each sentence in a tagged file
# Input: sampleinp.txt_tagged2 (format: idx\tword1/TAG word2/TAG ...)
# Output: sampleinp.txt_codemix_ratio (format: idx\tcode_mix_ratio)

tagged_file = 'cleaned_comments_from_api.txt_tagged'
output_file = 'cleaned_comments_from_api.txt_tagged_codemix_ratio'

def compute_code_mix_ratio(tagged_line):
    # Expects a string like: 'word1/HI word2/EN ...'
    tokens = tagged_line.strip().split()
    if not tokens:
        return 0.0
    hi_count = sum(1 for t in tokens if t.endswith('/HI'))
    en_count = sum(1 for t in tokens if t.endswith('/EN'))
    total = hi_count + en_count
    if total == 0:
        return 0.0
    # Code-mix ratio: min(hi_count, en_count) / total
    return min(hi_count, en_count) / total

with open(tagged_file, 'r', encoding='utf-8') as fin, open(output_file, 'w', encoding='utf-8') as fout:
    for line in fin:
        line = line.strip()
        if not line or not line[0].isdigit():
            continue
        try:
            idx, tagged = line.split('\t', 1)
        except ValueError:
            continue
        ratio = compute_code_mix_ratio(tagged)
        fout.write(f"{idx}\t{ratio:.2f}\n")