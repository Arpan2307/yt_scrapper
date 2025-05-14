from codeswitch.codeswitch import LanguageIdentification
import numpy as np

lid = LanguageIdentification('hin-eng')

input_file = 'cleaned_comments_from_api.txt'
output_file = 'cleaned_comments_from_api.txt_tagged'

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
        # Write comment lines as is
        if not line[0].isdigit():
            fout.write(line + '\n')
            continue
        # Split line number and sentence
        try:
            idx, sentence = line.split('\t', 1)
        except ValueError:
            # If not tab-separated, try space
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