import re
import requests
from calendar import month_abbr
from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup
from six import u
import json
from typing import List, Dict, Union
from collections import defaultdict

abbr_to_num = {name: num for num, name in enumerate(month_abbr) if num}


def __get_web_page(url):
    resp = requests.get(url, cookies={'over18': '1'}, verify=True)
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text


def __get_urls(page):
    # get one page articles urls
    articles = []
    soup = BeautifulSoup(page, "html.parser")
    divs = soup.find_all('div', 'r-ent')
    for d in divs:
        # 取得文章連結
        if d.find('a'):  # 有超連結，表示文章存在，未被刪除
            if not d.find('a').string:
                continue
            href = d.find('a')['href']
            articles.append("https://www.ptt.cc" + href)
    return articles


def __line_con(content):
    target = ""
    for lst in content.split(" "):
        if len(lst) >= 39:
            target += lst
        else:
            target += lst + " "
    return target


def __movie_url(start, end):
    # get ptt movie board index start to end
    # all articles url in this range
    # [url1,url2....]
    articles_url = []
    while True:
        url = 'https://www.ptt.cc/bbs/movie/index{0}.html'.format(start)
        page = __get_web_page(url)
        articles_url += __get_urls(page)
        if start == end:
            break
        else:
            sleep(0.1)
        start += 1
        print("URL : {0}/{1} finished!".format(start, end))
    return articles_url


def article_info(url: str) -> Union[Dict, None]:
    # noinspection SpellCheckingInspection
    print(url)
    resp = requests.get(url, cookies={'over18': '1'}, verify=True)
    if resp.status_code != 200:
        print('invalid url:', resp.url)
        return None

    article_id = re.sub('\.html', '', resp.url.split('/')[-1])
    soup = BeautifulSoup(resp.text, "html.parser")
    main_content = soup.find(id="main-content")
    metas = main_content.select('div.article-metaline')
    author = ''
    title = ''
    date = ''
    if metas:
        author = metas[0].select('span.article-meta-value')[0].string\
            if metas[0].select('span.article-meta-value')[0] else author
        title = metas[1].select('span.article-meta-value')[0].string\
            if metas[1].select('span.article-meta-value')[0] else title
        date = metas[2].select('span.article-meta-value')[0].string\
            if metas[2].select('span.article-meta-value')[0] else date
        # remove meta nodes
        for meta in metas:
            meta.extract()
        for meta in main_content.select('div.article-metaline-right'):
            meta.extract()

    # remove and keep push nodes
    pushes = main_content.find_all('div', class_='push')
    for push in pushes:
        push.extract()

    # 移除 '※ 發信站:' (starts with u'\u203b'), '◆ From:' (starts with u'\u25c6'), 空行及多餘空白
    # 保留英數字, 中文及中文標點, 網址, 部分特殊符號
    filtered = [v for v in main_content.stripped_strings if v[0] not in [u'※', u'◆'] and v[:2] not in [u'--']]
    expr = re.compile(
        u(r'[^\u4e00-\u9fa5\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\s\w:/-_.?~%()]')
    )
    for i in range(len(filtered)):
        filtered[i] = re.sub(expr, '', filtered[i])

    filtered = [_f for _f in filtered if _f]  # remove empty strings
    filtered = [x for x in filtered if article_id not in x]  # remove last line containing the url of the article
    content = ' '.join(filtered)
    content = re.sub(r'(\s)+', ' ', content)
    label = re.sub('[\[\]［］【】]', ' ', title).split()[0]

    # data process
    date = date.split()
    time = date[3].split(":")
    month = abbr_to_num[date[1]]
    date = datetime(int(date[-1]), month, int(date[2]), int(time[0]), int(time[1]), int(time[2])).isoformat()

    dic = {
        "_id": article_id,
        "author": author,
        "label": label,
        "title": title,
        "url": url,
        "date_added": date,
        "content": __line_con(content)}
    return dic
# end article_info()


def json_write(filename: str, data) -> None:
    with open(filename, "w", encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)


def json_read(filename: str):
    with open(filename, encoding='utf-8') as json_data:
        d = json.load(json_data)
        return d


def download(start=1, end=1) -> None:
    # page start to end
    # get article and download to json file
    # {"article id": {"article content": content, "article title": title, ...}}
    articles = []
    urls = __movie_url(start, end)
    for url in urls:
        # noinspection PyBroadException
        try:
            article = article_info(url)
            if article:
                articles.append(article)
        except Exception:
            continue
        print("{0}/{1} finished!".format(urls.index(url) + 1, len(urls)))
        sleep(0.2)
    json_write(str(start) + str(end) + ".txt", articles)
    write_log(end)


# movie board search : off-line version
def search(j_file, query: str) -> List[Dict]:
    target = []
    for article in j_file:
        print(article["title"])
        print(query)
        if article["title"].find(query) != -1:
            target.append(article)
    return target


def write_log(page: int) -> None:
    with open("log.txt", "w", encoding='utf-8') as outfile:
        outfile.write("Last download page : " + str(page))


def read_log() -> str:
    with open("log.txt", "r", encoding='utf-8') as outfile:
        last = outfile.read().split()[4]
    return last


def read_label() -> Dict:
    labels = defaultdict(int)
    with open("label.txt", 'r', encoding='utf-8') as table:
        for line in table:
            labels[line.split()[0]] = int(line.split()[1])
    return labels
