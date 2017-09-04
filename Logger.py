from datetime import datetime


def log(frameinfo, *text) -> None:
    try:
        log.verbose
    except (NameError, AttributeError):
        log.verbose = True
    if log.verbose:
        print(datetime.now(), frameinfo.filename, frameinfo.lineno, *text)
