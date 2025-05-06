
# import time, random
# t = []

# def mod(num, modulus):
#   return num - (num // modulus) * modulus

# def splice(list, index = 0, apply_mod=False):
#   if index >= len(list):
#     if not apply_mod: return []
#     index = mod(index, len(list))
#   if index < 0:
#     if not apply_mod: return []
#     index = mod(index, len(list))
#   a = list[:index]
#   b = list[index+1:]
#   return a + b

# l = 1000000

# a = time.perf_counter()
# for i in range(l):
#   t.append(int(random.randint(1,9)))
# b = time.perf_counter()
# print(f"Time taken to generate list of {l} elements: %.5fsec(s)" % (b - a))

# print(len(t))

# index = int(random.randint(0, l-1))
# print(index)

# a = time.perf_counter()
# splice(t, index)
# b = time.perf_counter()
# print(f"Time taken to splice index {index} from list of {l} elements: %.5fsec(s)" % (b - a))




# f = ["a", 0, 2, "e"]

# for obj in f: print(obj)

import turtle as tt

ts = tt.Screen()
ts.setup(1000, 500);

# ts.onclick(tt.bye, "space")

ts.mainloop()
