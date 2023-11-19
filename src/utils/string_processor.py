from multimethod import multimethod


def serialize(text: str) -> list[str]:
    l: list[str] = []
    start: int = 0
    while start < len(text):
        word: str = ''
        while start < len(text) and not text[start].isalnum():
            start += 1
        if start < len(text):
            end: int = start
            if text[start].isdecimal():
                while end + 1 < len(text) and text[end + 1].isdecimal():
                    end += 1
            elif text[start].islower():
                while end + 1 < len(text) and text[end + 1].islower():
                    end += 1
            elif text[start].isupper():
                if end + 1 < len(text):
                    char = text[end + 1]
                    if char.isupper():
                        end += 1
                        while end + 1 < len(text) and text[end + 1].isupper():
                            end += 1
                        if end + 1 < len(text) and text[end + 1].islower():
                            end -= 1
                    elif char.islower():
                        end += 1
                        while end + 1 < len(text) and text[end + 1].islower():
                            end += 1
            else:
                print('what now?!')
            word = text[start:end + 1]
            start = end + 1
        if word != '':
            l.append(word.lower())
    return l


@multimethod
def do_lcs(term1: list[str], term2: list[str], start1: int, end1: int, start2: int, end2: int, neighborhood: int, min: int, lcs_m: list[int], lcs_n: list[int]):
    matches_m: list[int] = []
    for _ in term1:
        matches_m.append(-1)
    matches_n: list[int] = []
    for _ in term2:
        matches_n.append(-1)
    do_lcs(term1, term2, start1, end1, start2, end2, neighborhood, min, matches_m, matches_n)
    for i in range(0, len(matches_m)):
        j: int = matches_m[i]
        if matches_m[i] > -1:
            lcs_m.append(i)
            lcs_n.append(j)


def serialize_to_chars(s: str) -> list[int]:
    l: list[int] = []
    for i in range(0, len(s)):
        l.append(ord(s[i]))
    return l


def compute_char_lcs(term1: list[int], term2: list[int]) -> float:
    len_m: int = len(term1)
    len_n: int = len(term2)
    d: list[list[int]] = [[0 for _ in range(len_n + 1)] for _ in range(len_m + 1)]
    code_m: list[int] = [0 for _ in range(len_m + 1)]
    code_n: list[int] = [0 for _ in range(len_n + 1)]
    p: list[list[str]] = [['' for _ in range(len_n + 1)] for _ in range(len_m + 1)]
    for i in range(1, len_m + 1):
        code_m[i] = term1[i - 1]
    for i in range(1, len_n + 1):
        code_n[i] = term2[i - 1]
    for i in range(1, len_m + 1):
        for j in range(1, len_n + 1):
            if code_m[i] == code_n[j]:
                d[i][j] = d[i - 1][j - 1] + 1
                p[i][j] = 'LU'
            elif d[i - 1][j] >= d[i][j - 1]:
                d[i][j] = d[i - 1][j]
                p[i][j] = 'U'
            else:
                d[i][j] = d[i][j - 1]
                p[i][j] = 'L'
    matches: int = d[len_m][len_n]
    return matches * 2.0 / (len_m + len_n)


@multimethod
def do_lcs(sequence1: list[str], sequence2: list[str], neighborhood: int, min_neighborhood: int, lcs_m: list[int], lcs_n: list[int]):
    """
    :param sequence1: input sequence 1
    :param sequence2: input sequence 2
    :param neighborhood: the number of surrounding matched lines
    :param min_neighborhood: should be 0
    :param lcs_m: indices of matches in sequence 1
    :param lcs_n: incdices of matches in sequence 2
    """
    item_indices: dict[str, int] = {}
    index(sequence1, item_indices)
    index(sequence2, item_indices)
    matches_m: list[int] = [-1] * len(sequence1)
    matches_n: list[int] = [-1] * len(sequence2)
    do_lcs(sequence1, sequence2, 0, len(sequence1) - 1, 0, len(sequence2) - 1, neighborhood, min_neighborhood, matches_m, matches_n)
    for i in range(0, len(matches_m)):
        j: int = matches_m[i]
        if j > -1:
            lcs_m.append(i)
            lcs_n.append(j)


def index(sequence: list[str], item_indices: dict[str, int]):
    for i in range(0, len(sequence)):
        item: str = sequence[i]
        item_index: int = len(item_indices)
        if item in item_indices:
            item_index = item_indices[item]
        else:
            item_indices[item] = item_index
        sequence[i] = str(item_index)


@multimethod
def do_lcs(term1: list[str], term2: list[str], start_m: int, end_m: int, start_n: int, end_n: int, neighborhood: int,
           min: int, lcs_m: list[int], lcs_n: list[int]):
    len_m: int = end_m - start_m + 1
    len_n: int = end_n - start_n + 1

    d: list[list[int]] = [[0 for _ in range(len_n + 1)] for _ in range(len_m + 1)]
    p: list[list[str]] = [['' for _ in range(len_n + 1)] for _ in range(len_m + 1)]
    code_m: list[str] = ['' for _ in range(len_m + 1)]
    code_n: list[str] = ['' for _ in range(len_n + 1)]

    for i in range(1, len_m + 1):
        code_m[i] = term1[start_m + i - 1]
    for i in range(1, len_n + 1):
        code_n[i] = term2[start_n + i - 1]
    i_neighbors: list[str] = []
    for i in range(0, neighborhood):
        if len(term1) > start_m - 1 + i >= neighborhood:
            buffer: str = ''
            for j in range(0, neighborhood):
                buffer += term1[start_m - 1 + i - neighborhood + j] + ' '
            i_neighbors.append(buffer)
        else:
            i_neighbors.append('')
    for i in range(1, len_m + 1):
        if neighborhood > 0:
            del i_neighbors[0]
            if len_m - i >= neighborhood:
                pre: str = i_neighbors[neighborhood - 1]
                if start_m + i - 1 + neighborhood < len(term1):
                    buffer: str = ''
                    for j in range(i, i + neighborhood + 1):
                        buffer += term1[start_m + j - 1] + ' '
                    i_neighbors.append(buffer)
                else:
                    i_neighbors.append(
                        pre[len(term1[start_m + i - 2]) + 1:-1] + term1[start_m + i - 1 + neighborhood] + ' ')
            else:
                i_neighbors.append('')
        j_neighbors: list[str] = []
        for j in range(0, neighborhood + 1):
            if len(term2) > start_n - 1 + j >= neighborhood:
                buffer: str = ''
                for k in range(0, neighborhood + 1):
                    buffer += term2[start_n - 1 + j - neighborhood + k] + ' '
                j_neighbors.append(buffer)
            else:
                j_neighbors.append('')
        for j in range(1, len_n + 1):
            if neighborhood > 0:
                del j_neighbors[0]
                if start_n + j - 1 + neighborhood < len(term2):
                    pre: str = j_neighbors[neighborhood - 1]
                    if pre == '':
                        buffer: str = ''
                        for k in range(j, j + neighborhood + 1):
                            buffer += term2[start_n + k - 1] + ' '
                        j_neighbors.append(buffer)
                    else:
                        if len(term2[start_n + j - 2]) < 0:
                            print('WTF')
                        j_neighbors.append(
                            pre[len(term2[start_n + j - 2]) + 1:-1] + term2[start_n + j - 1 + neighborhood] + ' ')
                else:
                    j_neighbors.append('')
            is_matched: bool = False
            if code_m[i] == code_n[j]:
                if neighborhood == 0:
                    is_matched = True
                else:
                    for k in range(0, neighborhood + 1):
                        if i_neighbors[k] != '' and i_neighbors[k] == j_neighbors[k]:
                            is_matched = True
                            break
            if is_matched:
                d[i][j] = d[i - 1][j - 1] + 1
                p[i][j] = 'LU'
            elif d[i - 1][j] >= d[i][j - 1]:
                d[i][j] = d[i - 1][j]
                p[i][j] = 'U'
            else:
                d[i][j] = d[i][j - 1]
                p[i][j] = 'L'
    i: int = len_m
    j: int = len_n
    pre_m: int = len_m + 1
    pre_n: int = len_n + 1
    while i > 0 and j > 0:
        if p[i][j] == 'LU':
            lcs_m[start_m + i - 1] = start_n + j - 1
            lcs_n[start_n + j - 1] = start_m + i - 1
            if neighborhood > 0 and neighborhood >= 2 * min:
                if i < pre_m - 1 and j < pre_n - 1:
                    do_lcs(term1, term2, start_m + i, start_m + pre_m - 2, start_n + pre_n - 2, (neighborhood - 1) // 2,
                           min, lcs_m, lcs_n)
                pre_m = i
                pre_n = j
            i -= 1
            j -= 1
        elif p[i][j] == 'U':
            i -= 1
        else:
            j -= 1
    if neighborhood > 0 and neighborhood >= 2 * min and pre_m > 1 and pre_n > 1:
        do_lcs(term1, term2, start_m, start_m + pre_m - 2, start_n, start_n + pre_n - 2, (neighborhood - 1) // 2, min,
               lcs_m, lcs_n)
