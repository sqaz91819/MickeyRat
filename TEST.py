from nlp import GOGOGO
from datetime import datetime
from inspect import currentframe, getframeinfo
from Logger import log


if __name__ == '__main__':
    start = datetime.now()
    log(getframeinfo(currentframe()), 'fetching from nlp started')
    result = GOGOGO.interface('模仿遊戲')
    log(getframeinfo(currentframe()), 'fetching from nlp finished, spent', datetime.now() - start)
    log(getframeinfo(currentframe()), 'got', len(result), 'articles')
    log(getframeinfo(currentframe()), 'first two are:\n', result[:2])

exit()
