from nlp import GOGOGO


if __name__ == '__main__':
    result = GOGOGO.InterFace('模仿遊戲')
    print('got', len(result), 'articles')
    print('first two are:\n', result[:2])

exit()
