from nlp import get_JIEBA
from g_api import crawler
import g_api


def nlp(film_name, query_num=10):
    ans = []

    x = g_api.g_api(film_name, query_num//10)

    for i in x:
        print('nlp progress:', x.index(i)/len(x)*100, '%')
        test = crawler.article_inf(i)
        if test:
            ans.append(get_JIEBA.get_jieba(crawler.__line_con__(test["content"]), film_name))

    return ans


# film_name = "聲之形"
# nlp(film_name)
