def all_equal(list):
    return all(i == list[0] for i in list)

def average(list):
    if len(list) == 0:
        return 0
    return sum(list) / len(list)