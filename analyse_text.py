class TextTooShortError(Exception):
    pass


def get_summary(text):
    return {'head': text[0]}
