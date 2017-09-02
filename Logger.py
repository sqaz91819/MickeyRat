from datetime import datetime


def log(frameinfo, *text) -> None:
    print(datetime.now(), frameinfo.filename, frameinfo.lineno, *text)
