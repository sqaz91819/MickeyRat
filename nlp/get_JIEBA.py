# encoding=utf-8
import jieba
import jieba.posseg as pseg


def get_jieba(string, new_word=""):
    jieba.load_userdict("dict.txt")

    # for wo in newWord:
    jieba.suggest_freq(new_word, True)

    # file = open(file_name, 'rb').read()

    words = pseg.cut(string)

    words_frequency = {}

    with open("1-10000.txt", encoding='utf8') as f:
        for line in f:
            (key, v1, v2) = line.split()
            words_frequency[v1] = key

    answer = []

    for word, flag in words:
        if word in words_frequency:
            answer.append([word, int(words_frequency[word]), flag])
        else:
            answer.append([word, 0, flag])

    return answer


'''''
    f = open('result_of_jieba.txt', 'w')
    for i in answer:
        st = str(i[0]) + str(i[1])
        f.writelines(st)
    f.close()

    return answer
'''

# print(get_jieba("Film_critic.txt"))
# t = "昨天很榮幸能去看聲之形 所以一定要來發一下心得 先說結論 我覺得聲之形是部不輸給你的名字的電影"
# print(get_jieba(t,"聲之形"))
