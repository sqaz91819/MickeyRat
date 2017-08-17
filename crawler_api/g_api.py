import pprint
from os import path

from googleapiclient.discovery import build

# For CSE users, the API provides 100 search queries per day for free.
# If you need more, you may sign up for billing in the API Console.
# Additional requests cost $5 per 1000 queries, up to 10k queries per day.


def read_key(filename):
    with open(filename, 'r') as file:
        key = file.read()
    return key


def g_api(m_name, q_count):
    url_list = []
    total = 0
    developer_key = read_key(path.join('crawler_api', 'developer_key.txt'))
    service = build("customsearch", "v1",
                    developerKey=developer_key)
    cx = read_key(path.join('crawler_api', 'cx.txt'))
    for i in range(1, q_count):
        res = service.cse().list(
            q=m_name,
            cx=cx,
            start=(i-1)*10 + 1
        ).execute()

        for item in res['items']:
            if "新聞" in item['title'] or "情報" in item['title']:
                continue
            # pprint.pprint(item['title'])
            # pprint.pprint(item['link'])
            url_list.append(item['link'])
            total += 1
        # end for
    # end for
    print(total)
    return url_list
# end g_api()
# g_api("聲之形", 10)
