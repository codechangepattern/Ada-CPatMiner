def longest_common_subsequence(s0, s1):
    lengths = [[0 for _ in range(len(s1) + 1)] for _ in range(len(s0) + 1)]
    for i in range(len(s0)):
        for j in range(len(s1)):
            if s0[i] == s1[j]:
                lengths[i + 1][j + 1] = lengths[i][j] + 1
            else:
                lengths[i + 1][j + 1] = max(lengths[i + 1][j], lengths[i][j + 1])

    return extract_indexes(lengths, len(s0), len(s1))


def hunks(s0, s1):
    lcs = longest_common_subsequence(s0, s1)
    hunks = []
    inf0 = -1
    inf1 = -1
    last0 = -1
    last1 = -1
    for i in range(len(lcs)):
        match = lcs[i]
        if inf0 == -1 or inf1 == -1:
            inf0 = match[0]
            inf1 = match[1]
        elif last0 + 1 != match[0] or last1 + 1 != match[1]:
            hunks.append([inf0, last0 + 1, inf1, last1 + 1])
            inf0 = match[0]
            inf1 = match[1]
        elif i == len(lcs) - 1:
            hunks.append([inf0, match[0] + 1, inf1, match[1] + 1])
            break
        last0 = match[0]
        last1 = match[1]
    return hunks


def longest_common_sequence(s1, s2):
    start = 0
    max = 0
    for i in range(len(s1)):
        for j in range(len(s2)):
            x = 0
            while s1[i + x] == s2[j + x]:
                x += 1
                if ((i + x) >= len(s1)) or ((j + x) >= len(s2)):
                    break
            if x > max:
                max = x
                start = i
    return s1[start:(start + max)]


def longest_common_subsequence_with_type_and_label(s0, s1):
    lengths = [[0 for _ in range(len(s1) + 1)] for _ in range(len(s0) + 1)]
    for i in range(len(s0)):
        for j in range(len(s1)):
            if s0[i].has_same_type_and_label(s1[j]):
                lengths[i + 1][j + 1] = lengths[i][j] + 1
            else:
                lengths[i + 1][j + 1] = max(lengths[i + 1][j], lengths[i][j + 1])

    return extract_indexes(lengths, len(s0), len(s1))


def longest_common_subsequence_with_type(s0, s1):
    lengths = [[0 for _ in range(len(s1) + 1)] for _ in range(len(s0) + 1)]
    for i in range(len(s0)):
        for j in range(len(s1)):
            if s0[i].has_same_type(s1[j]):
                lengths[i + 1][j + 1] = lengths[i][j] + 1
            else:
                lengths[i + 1][j + 1] = max(lengths[i + 1][j], lengths[i][j + 1])

    return extract_indexes(lengths, len(s0), len(s1))


def longest_common_subsequence_with_isomorphism(s0, s1):
    lengths = [[0 for _ in range(len(s1) + 1)] for _ in range(len(s0) + 1)]
    for i in range(len(s0)):
        for j in range(len(s1)):
            if s0[i].is_isomorphic_to(s1[j]):
                lengths[i + 1][j + 1] = lengths[i][j] + 1
            else:
                lengths[i + 1][j + 1] = max(lengths[i + 1][j], lengths[i][j + 1])

    return extract_indexes(lengths, len(s0), len(s1))


def longest_common_subsequence_with_isostructure(s0, s1):
    lengths = [[0 for _ in range(len(s1) + 1)] for _ in range(len(s0) + 1)]
    for i in range(len(s0)):
        for j in range(len(s1)):
            if s0[i].is_iso_structural_to(s1[j]):
                lengths[i + 1][j + 1] = lengths[i][j] + 1
            else:
                lengths[i + 1][j + 1] = max(lengths[i + 1][j], lengths[i][j + 1])

    return extract_indexes(lengths, len(s0), len(s1))


def extract_indexes(lengths, length1, length2):
    indexes = []
    x = length1
    y = length2
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x - 1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y - 1]:
            y -= 1
        else:
            indexes.append([x - 1, y - 1])
            x -= 1
            y -= 1
    indexes.reverse()
    return indexes
