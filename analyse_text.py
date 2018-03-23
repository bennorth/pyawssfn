class TextTooShortError(Exception):
    pass


def get_summary(text):
    if len(text) == 0:
        raise TextTooShortError
    return {'head': text[0]}
