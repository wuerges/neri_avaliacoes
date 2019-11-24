
def distancia(str1, str2):
    cache = [[-1 for x in range(len(str2)+1)] for y in range(len(str1)+1)]

    cache[len(str1)][len(str2)] = 0

    for j in range(len(str2)-1, -1, -1):
        pen = 20 if str2[j].isdigit() else 1
        cache[len(str1)][j] = pen + cache[len(str1)][j+1]
    # for j, _ in enumerate(str2):
    #     cache[len(str1)][j] = len(str2) - j

    for i in range(len(str1)-1, -1, -1):
        pen = 20 if str1[i].isdigit() else 1
        cache[i][len(str2)] = pen + cache[i+1][len(str2)]

    # for i, _ in enumerate(str1):
        # cache[i][len(str2)] = len(str1) - i

    for i in range(len(str1)-1, -1, -1):
        for j in range(len(str2)-1, -1, -1):
            if str1[i] == str2[j]:
                cache[i][j] = cache[i+1][j+1]
            else:
                opt1 = (20 if str2[j].isdigit() else 1) + cache[i][j+1]
                opt2 = (20 if str1[i].isdigit() else 1) + cache[i+1][j]
                cache[i][j] = min(opt1, opt2)
            

    return cache[0][0]
