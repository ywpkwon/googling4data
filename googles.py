#-*- coding: utf-8 -*-

from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import urllib
import html2text
import re
import json
import pprint
from http.cookiejar import CookieJar
import markdown2

# def visible(element):
#     if element.parent.name in ['style', 'script', '[document]', 'head', 'title']: return False
#     # text = str(element.encode('utf-8')).strip()
#     text = str(element).strip()

#     if re.match('<!--.*-->', text): return False
#     elif text in ['\n', '']: return False
#     return True

def extract_text_url(url):
    text = []
    req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"})

    # html = urllib.request.urlopen(req)
    # There were errors for some URLs. Advised to enable caching using Cookie Jar as below. 

    cj = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    response = opener.open(req)
    html = response.read().decode('utf8', errors='ignore')
    response.close()

    # Get html string
    soup = BeautifulSoup(html, "lxml")
    # return soup.get_text()                  # this is one way of extracting text, but seemed not good.
    htmltext = soup.encode('utf-8').decode('utf-8','ignore')

    # The html2text converts html to text with links and images in markdown grammar.
    # We don't want to keep links and images al all. 
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    return h.handle(htmltext)
    
    # texts = soup.findAll(text=True)
    # visible_texts = filter(visible, texts)
    # return u' '.join(visible_texts).encode('utf-8')
    # # for p in paragraphs:
    # #     print p.string 
    # #     print "--"
    # # return str(visible_texts) 

def google_query(search_term, api_key, cse_id, npages=1, num=10):
    service = build("customsearch", "v1", developerKey=api_key)

    total_results = []
    request_num = 10
    for i in range(npages):
        res = service.cse().list(q=search_term, cx=cse_id, start=i*num+1, num=num).execute()
        total_results += res['items']
    return total_results


def google_keyword2str(keyword, npages=1):

    # For security reason, we do not include api keys.
    # Load from 'key.json'.
    with open('key.json') as s: key = json.load(s)

    # Cast Google query.
    only_keys = ['displayLink', 'link', 'title','formattedUrl']
    results = google_query(keyword, key['api_key'], key['cse_id'], npages)
    results = [{ key: result[key] for key in only_keys } for result in results]

    report = dict()
    report['nRetrieved'] = len(results)

    # Extract texts.
    # print("writing text..")
    texts = []; errored_url = []
    for i, r in enumerate(results):
        url = r['link'] 
        # print(r['title'].encode('utf-8').decode('ascii','ignore'))
        print('---- '+ url)
        try:
            text = extract_text_url(url)
            texts += text + " "
        except:
            errored_url.append(url)
            print('---- error!')
        print('%d pages extracted: %d letters so far.' % (i, len(texts)))

    report = dict()
    report['keyword'] = keyword
    report['retrieved'] = results
    report['nRetrieved'] = len(results)
    report['nErrored'] = len(errored_url)
    report['ErroredURL'] = errored_url


    print("** %d retrieved with %d errors." % (report['nRetrieved'], report['nErrored']))
    return texts, report

if __name__ == '__main__':
    
    # url= "http://www.nytimes.com/2016/12/20/technology/daily-report-an-autonomous-car-future-needs-better-maps.html"
    # retrieved_strs = [extract_text_url(url)]
    # quit()

    # Example of googling a list of keywords.
    keywords = ['autonomous car', 'autonomous car innovation']
    npages = 10  # number of pages. each page has 10 web links of googling.

    for keyword in keywords:
        retrieved_strs, report = google_keyword2str(keyword, npages)
        
        jsonname = keyword + ".json"
        txtname = keyword + ".txt"
        with open(jsonname, "w") as jf: json.dump(report, jf)
        with open(txtname, "w", encoding="utf-8") as ofile:
            for s in retrieved_strs: ofile.write(s)

    # 





