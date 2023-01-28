import requests
from bs4 import BeautifulSoup
import sys

# Initial Vars

list_languages = ['Arabic', 'German', 'English', 'Spanish', 'French', 'Hebrew', 'Japanese',
                  'Dutch', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Turkish']
translate_all = False


def url_ok(url_arg):
    response = requests.head(url_arg)
    return response.status_code == 200


def html2list(soupvar, tag, classname):
    find = soupvar.find_all(tag, {'class': classname})
    result = list()
    for i in find:
        result.append(i.text.lower().replace("\n", "").replace("\r", "").lstrip())
    return result


def adjust_examples(temp_list):
    res = [item.split('  ') for item in temp_list]
    res = [item for l in res for item in l]
    temp_list = [x for x in res if x != '']
    return temp_list


def fill_output_list(langlist, dst, msg, item, times):
    output = []
    if times > len(item):
        times = len(item)
    output.append(f'\n- {langlist[dst-1]} '.upper() + msg.upper() + ':')
    for i in range(0, times):
        if isinstance(item, list):
            output.append(item[i])
        elif isinstance(item, dict):
            output.append(f"{list(item.keys())[i]}\n{list(item.values())[i]}")  # Because dict_keys is not scriptable
        else:
            break
    return output


def list2dict(lst):
    res_dct = {lst[i-1]: lst[i] for i in range(1, len(lst), 2)}
    return res_dct


def define_direction(languages, src, dst):
    return languages[src-1].lower() + "-" + languages[dst-1].lower()


def translate(listlang, src, dst, word):
    translation_direction = define_direction(listlang, src, dst)
    url = f'https://context.reverso.net/translation/{translation_direction}/{word}'
    # print(url)
    if url_ok:
        # print('200 OK') # Not necessary at this stage
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        except requests.exceptions.ConnectionError:
            print("Something wrong with your internet connection")
        if not r:
            print(f"Sorry, unable to find {word.lower()}")
            exit()
        soup = BeautifulSoup(r.content, 'html.parser')
        word_list = html2list(soup, 'span', 'display-term')
        example_list = html2list(soup, 'div', 'example')
        example_list = adjust_examples(example_list)
        example_dict = list2dict(example_list)
        return word_list, example_dict


# USER INPUTS - previous stage (5/7)
# user inputs source language, destination language and word to translate
# src_lang, dst_lang, word = user_inputs(list_languages)

# ARGS INPUTS - current stage update (6/7)
# source language, destination language and word to translate are passed as arguments
args = sys.argv
if len(args) < 3:
    print("""
    Multiple Language Translator
    
    TRANSLATOR [source language] [destination language] [word]
    
    Use "all" in destination language for multiple language translation""")
    exit()

src_lang, dst_lang, word = args[1:]  # ignore first arg, name of the script

if src_lang.capitalize() not in list_languages:
    print(f"Sorry, the program doesn't support {src_lang}")
    exit()
elif dst_lang.capitalize() not in list_languages and (dst_lang != "All".lower()):
    print(f"Sorry, the program doesn't support {dst_lang}")
    exit()

src_lang = int(list_languages.index(src_lang.capitalize())) + 1
if dst_lang == "all":
    dst_lang = 0
    translate_all = True
else:
    print(dst_lang)
    dst_lang = int(list_languages.index(dst_lang.capitalize())) + 1

# CONNECTION TRANSLATION
f = open(f'{word}.txt', 'w')
if not translate_all:
    word_list, example_dict = translate(list_languages, src_lang, dst_lang, word)
    for i in range(1, 3):
        print(*fill_output_list(list_languages, dst_lang, "Translations", word_list, 5), sep="\n")
        print(*fill_output_list(list_languages, dst_lang, "Examples", example_dict, 5), sep="\n")
        sys.stdout = f
else:
    for i in range(1, len(list_languages) + 1):
        if i != src_lang:
            word_list, example_dict = translate(list_languages, src_lang, i, word)
            print(*fill_output_list(list_languages, i, "Translations", word_list, 3), sep="\n")
            print(*fill_output_list(list_languages, i, "Examples", example_dict, 3), sep="\n")
            # Save original output
            original_stdout = sys.stdout
            sys.stdout = f
            print(*fill_output_list(list_languages, i, "Translations", word_list, 3), sep="\n")
            print(*fill_output_list(list_languages, i, "Examples", example_dict, 3), sep="\n")
            # Reset the standard output
            sys.stdout = original_stdout
f.close()


