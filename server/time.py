import time

start = time.time()
print(start)
for i in range(10000000):
    pass

print(time.time() - start)
