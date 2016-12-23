from googleapiclient.discovery import build
from urllib import urlopen
from bs4 import BeautifulSoup
import re
import json
import pprint

# my_api_key = "AIzaSyAuTBaPt4sRBOj1Ehkn5LJ4pYM_EtKEyD4"
# my_cse_id = "002953589285845417280:hthneeb_kww"


def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']: return False
    text = str(element.encode('utf-8')).strip()
    if re.match('<!--.*-->', text): return False
    elif text in ['\n', '']: return False
    return True

def extract_text_url(url):
    text = []
    html = urlopen(url)
    soup = BeautifulSoup(html, "lxml")
    texts = soup.findAll(text=True)
    visible_texts = filter(visible, texts)
    return u' '.join(visible_texts).encode('utf-8')
    # for p in paragraphs:
    #     print p.string 
    #     print "--"
    # return text 

def google_query(search_term, api_key, cse_id, pagenum=1, num=10):
    service = build("customsearch", "v1", developerKey=api_key)

    total_results = []
    request_num = 10
    for i in range(pagenum):
        print(i)
        res = service.cse().list(q=search_term, cx=cse_id, start=i*num+1, num=num).execute()
        total_results += res['items']
    return total_results

# For security reason, we do not include api keys.
# Load from 'key.json'.
with open('key.json') as s: key = json.load(s)

# Cast Google query.
keyword = 'autonomous car'
results = google_query(keyword, key['api_key'], key['cse_id'], pagenum=1)
only_keys = ['displayLink', 'link', 'title']
results = [{ key: result[key] for key in only_keys } for result in results]
# for result in results: pprint.pprint(result)

# Extract texts.
print "writing text.."
for i,r in enumerate(results):
    print r['title']
    text = extract_text_url(r['link'])
    fname = "%03d.txt" % i
    with open(fname, "w") as ofile:
        ofile.write(text)