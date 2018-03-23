class TextTooShortError(Exception):
    pass


def get_summary(text):
    if len(text) == 0:
        raise TextTooShortError
    return {'head': text[0]}


def augment_summary(text, summary):
    aug_summary = dict(summary)
    aug_summary['n_characters'] = len(text)
    return aug_summary


def get_n_vowels(text):
    return sum(text.count(v) for v in 'aeiou')


def get_n_spaces(text):
    return text.count(' ')


def format_result(summary, infos):
    """
    Expect inputs of:

    summary --- dict with 'head' and 'n_characters' as keys
    infos --- list of two elements, each a number
    """
    return (f'text starts with {summary["head"]},'
            f' has {summary["n_characters"]} chars,'
            f' {infos[0]} vowels, and'
            f' {infos[1]} spaces')
