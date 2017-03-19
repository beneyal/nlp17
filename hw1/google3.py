import requests
import nltk
import re
from bs4 import BeautifulSoup
import os
import codecs
import justext

# Normalize tabs into spaces, remove lines that are too short.
def cleanShortLines(raw, cutOff):
    raw = re.sub("[\t, ]+"," ", raw)
    raw = raw.split("\n")
    raw = filter(lambda t: len(t) > cutOff, raw)
    return "\n".join(raw)

# Filter "boilerplate" from html string: ads, jscript code, html tags.
# Only keep clean text.
def cleanHtml(html):
    # raw = nltk.clean_html(html) // was removed in nltk 3.0
    # If you do not install justext, use beautifulsoup:
    # soup = BeautifulSoup(html)
    # raw = soup.get_text()
    # This will do a better job once you install justext
    paragraphs = justext.justext(html, justext.get_stoplist('English'))
    return "\n".join([p.text for p in paragraphs if not p.is_boilerplate])


def getGoogleResults(search):
    search = search.replace(" ", "%20")
    url = 'http://www.google.com/search?q='+search
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent' : user_agent}
    req = requests.get(url, headers=headers)	
    html = req.text
    soup = BeautifulSoup(html, "lxml")
    html =  soup.prettify().split("\n")
    # Skip a few headers...
    html = html[167 :]
    html = "\n".join(html)
    links =re.findall(r"url\?q=(.+)&amp;s", html)
    return links

def fetch(url, tokenizer=nltk.word_tokenize):
    try:
        html = requests.get(url).text
    except:
        return None
    raw = cleanHtml(html)
    lessraw = cleanShortLines(raw, 50)
    tokens = tokenizer(lessraw)
    return (html, (raw, lessraw, tokens))

def google(search, tokenizer=nltk.word_tokenize):
    links = getGoogleResults(search)
    URLtoHTMLtoTEXT = {}
    for url in links:
        page = fetch(url, tokenizer)
        if page is not None: URLtoHTMLtoTEXT[url] = page
    return URLtoHTMLtoTEXT

def EnsureDir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def PrintFile(text, fileName):
    EnsureDir("Data/")
    f = codecs.open(os.path.join("Data", fileName), "w", encoding="utf-8")
    f.write(text)
    f.write("\n")
    f.close()

def AnalyzeResults(results):
    for (index, key) in enumerate(results.keys()):
        value = results[key]
        (text, textWithoutShortlines, tokens) = value[1]
        if tokens:
            PrintFile("\n".join(tokens), "Tokens-%s.txt" % (index))
            PrintFile(text, "Raw-%s.txt" % (index))


if __name__ == "__main__":
    d = google("polar bears")
    AnalyzeResults(d)