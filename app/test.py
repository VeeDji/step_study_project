len_db = [(1, 10), (2, 5), (3, 14)]

len_index = list(map(lambda pair: pair[0], filter(lambda pair: pair[1] < 10, len_db)))

print(len_index)