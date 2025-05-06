# def windowTopLeftToCentered(top_left_coords):
#   w, h = (910, 485)
#   top_left_x, top_left_y = top_left_coords
#   centered_x = top_left_x - (w / 2)
#   centered_y = (h / 2) - top_left_y
#   return (centered_x, centered_y)

# def windowCenteredToTopLeft(centered_coords):
#   w, h = (910, 485)
#   centered_x, centered_y = centered_coords
#   top_left_x = centered_x + (w / 2)
#   top_left_y = (h / 2) - centered_y
#   return (top_left_x, top_left_y)


# a = (453, 243)
# b = windowTopLeftToCentered(a)
# c = windowCenteredToTopLeft(b)

# print(a)
# print(b)
# print(c)

# f = ["lksld", "98238urf", "lasjdf98", "skdj9e2", "92839ufsj", "aisd9f8u92f", "jlsjd982"]

# def mod(num, modulus):
#   return num - (num // modulus) * modulus

# def splice(array: list, index = 0, apply_mod=False):
#   l = len(array)
#   if l <= 0: return []
#   if index >= l:
#     if not apply_mod: return []
#     index = mod(index, l)
#   if index < 0:
#     if not apply_mod: return []
#     index = mod(index, l)
#   a = array[:index]
#   b = array[index+1:]
#   return a + b


# i = -7

# print(f)
# # print(f[5])
# g = f
# a = splice(f, i)
# b = splice(g, i, True)

# print(a)
# print(b)