from nlp import get_JIEBA
from g_api import crawler
from g_api import g_api


def nlp(film_name, query_num=10):
    ans = []

    x = g_api.g_api(film_name, query_num // 10)

    for i in x:
        print('nlp progress:', x.index(i) / len(x) * 100, '%')
        test = crawler.article_info(i)
        if test:
            ans.append(get_JIEBA.get_jieba(test["content"], film_name))

    return ans


# film_name = "聲之形"
# nlp(film_name)
