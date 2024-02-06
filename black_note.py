a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
b = [1, 2]


start = 0
stop = len(a)
step = 3


c = [list(t) for t in zip(*[a[i::3] for i in range(3)])]


d = dict(zip(b, c))
print(c)

print(d)