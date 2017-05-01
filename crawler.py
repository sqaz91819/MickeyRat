import re
import requests
from bs4 import BeautifulSoup
from six import u
import pprint
import json


def __get_web_page__(url):
    resp = requests.get(url, cookies={'over18': '1'}, verify=True)
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        return resp.text


def __get_urls__(page):
    # get one page articles urls
    articles = []
    soup = BeautifulSoup(page, "html.parser")
    divs = soup.find_all('div', 'r-ent')
    for d in divs:
        # 取得文章連結
        if d.find('a'):  # 有超連結，表示文章存在，未被刪除
            if "雷" not in d.find('a').string.split("]")[0]:
                continue
            href = d.find('a')['href']
            articles.append("https://www.ptt.cc" + href)
    return articles


def __line_con__(content):
    target = ""
    for lst in content.split(" "):
        if len(lst) >= 39:
            target += lst
        else:
            target += lst + " "
    return target


def movie_url(start, end):
    # get ptt movie board index start to end
    # all articles url in this range
    # [url1,url2....]
    articles_url = []
    while True:
        url = 'https://www.ptt.cc/bbs/movie/index{0}.html'.format(start)
        page = __get_web_page__(url)
        articles_url += __get_urls__(page)
        if start == end:
            break
        start += 1
    return articles_url


def article_info(url):
    resp = requests.get(url, cookies={'over18': '1'}, verify=True)
    if resp.status_code != 200:
        print('invalid url:', resp.url)
        return None

    article_id = re.sub('\.html', '', resp.url.split('/')[-1])
    soup = BeautifulSoup(resp.text, "html.parser")
    main_content = soup.find(id="main-content")
    metas = main_content.select('div.article-metaline')
    title = ''
    if metas:
        title = metas[1].select('span.article-meta-value')[0].string if metas[1].select('span.article-meta-value')[0] else title
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
    return {"title": title, "content": __line_con__(content), "url": url}
# end article_info()


def json_write(filename, file):
    with open(filename, "w", encoding='utf-8') as outfile:
        json.dump(file, outfile, ensure_ascii=False)


def json_read(filename):
    with open(filename, encoding='utf-8') as json_data:
        d = json.load(json_data)
        return d


def download(start, end):
    # page start to end
    # get article and download to json file
    # {"article id": {"article content": content, "article title": title, ...}}
    dic = {}
    urls = movie_url(start, end)
    print("url finished!")
    for url in urls:
        dic[re.sub('\.html', '', url.split('/')[-1])] = article_info(url)
        print("{0}/{1} finished!".format(urls.index(url) + 1, len(urls)))
    json_write(str(start) + str(end) + ".txt", dic)
    return dic


# movie board search : off-line version
def search(j_file, query):
    target = {}
    for article in j_file:
        print(j_file[article]["title"])
        print(query)
        if j_file[article]["title"].find(query) != -1:
            target.update({article: j_file[article]})
    return target

# test = article_info("https://www.ptt.cc/bbs/movie/M.1493212539.A.A9E.html")
# print(len(test["content"].split(" ")[2]))
# print(test["content"])
# print(__line_con__(test["content"]))

# pprint.pprint(article_info("https://www.ptt.cc/bbs/movie/M.1493212539.A.A9E.html"))
# pprint.pprint(download(5311, 5311))
# test = download(5311, 5311)
# pprint.pprint(search(test, "目擊者"))
