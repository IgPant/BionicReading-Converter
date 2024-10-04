import os
import shutil
from bs4 import BeautifulSoup, NavigableString
import re
import zipfile
import string
import html.parser

special_characters = string.digits + string.punctuation + "—'_\"/[]|\\-)("

def count_characters(word):
    # Count characters in the word, excluding HTML code, signs, numbers, and em dashes
    characters = sum(1 for char in word if char.isalpha() and char not in special_characters)
    return characters

def is_special_tag(current_tag):
    if isinstance(current_tag, NavigableString):
        return False
    return (
        current_tag.name in ['i', 'em', 'u', 'b'] or 
        any(descendant.name in ['i', 'em', 'u', 'b'] for descendant in current_tag.descendants)
    )


def alter_html(input_file: str, output_file: str):
    with open(input_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Add styles to head
    style = soup.new_tag('style')
    style.string = ".b{font-weight: bold;!important}.i{font-style: italic;}.u{text-decoration: underline;}.black {color: #000000;}* {color: #808080}!important"
    soup.head.insert(0, style)

    # Find all paragraphs and apply changes
    for paragraph in soup.find_all('p'):
        new_content = []
        for content in paragraph.contents:
            if isinstance(content, NavigableString):
                text = content.string
                words = re.findall(r'[\s—()[\]/\\-]+|[^\s—()[\]/\\-]+', text)
                for word in words:
                    punct=0
                    if word.startswith(("'", '"')):# and len(word) > 1 and word[1].isalpha():
                        new_content.append(word[0])
                        word = word[1:]
                    #if any(char in ".,;:" for char in word):

                    if word.endswith((".", ",", ";", ":", "!", "?", '"')):
                        punct=word[-1]
                        word = word[:-1]
                            #new_content.append(word[-1])
                    
                    X = count_characters(word)
                    if X == 0:
                        new_content.append(f'<span class="b black">{word}</span>')
                    elif X == 1:
                        new_content.append(f'<span class="b black">{word}</span>')
                    elif X % 2 == 0:
                        new_content.append(f'<span class="b black">{word[:X//2]}</span>{word[X//2:]}')
                    else:
                        new_content.append(f'<span class="b black">{word[:(X//2)+1]}</span>{word[(X//2)+1:]}')
                    if punct!=0:
                        new_content.append(punct)

            else:
                new_content.append(str(content))
        paragraph.clear()
        paragraph.append(BeautifulSoup(''.join(new_content), 'html.parser'))

    # Find all italicized, underlined, and bold tags and add the 'black' class
    for tag in soup.find_all(['i', 'em', 'u', 'b']):
        tag['class'] = tag.get('class', []) + ['b black']

    with open(output_file, 'w', encoding='utf-8') as f:
        output_html = str(soup)
        output_html = output_html.replace('&lt;', '<').replace('&gt;', '>').replace('—', '—')
        f.write(output_html)



def alter_epub(input_epub: str, output_epub: str):
    # Create a temporary directory to extract the epub contents to
    temp_dir = 'temp'
    os.makedirs(temp_dir)

    # Extract the epub contents to the temporary directory
    with zipfile.ZipFile(input_epub, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Find all HTML files in the temporary directory and alter them using the alter_html function
    for subdir, dirs, files in os.walk(temp_dir):
        for file in files:
            filepath = subdir + os.sep + file

            if filepath.endswith(".html"):
                alter_html(filepath, filepath)

    # Create a new epub file with the altered HTML files
    shutil.make_archive(output_epub[:-5], 'zip', temp_dir)
    os.rename(output_epub[:-5] + '.zip', output_epub)

    # Remove the temporary directory
    shutil.rmtree(temp_dir)

alter_epub('heart.epub', 'Heart_of_Darkness_BO.epub')
#alter_epub('estruturas.epub', 'Estruturas_de_Dados_BO.epub')