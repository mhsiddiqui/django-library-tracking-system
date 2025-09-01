import random
rand_list = [random.randint(1, 20) for _ in range(20)]

list_comprehension_below_10 = [n for n in rand_list if n < 10]

filter_below_10 = filter(lambda x: x < 10, rand_list)