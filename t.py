import math

x = -2e6

def A(x, n):
  n = n - 1
  i = 0
  y = 0.0

  while y < x:
    p = i % 3
    if p == 0:
      n = n + 1
      y = 1 * math.pow(10, n)
    elif p == 1: y = 2 * math.pow(10, n)
    else: y = 5 * math.pow(10, n)
    i = i + 1
  return y

def B(x, n):
  n = n + 2
  i = 0
  y = 1.0
  l = [0, 0]

  while y > x:
    p = i % 3
    if p == 0:
      n = n - 1
      y = 5 * math.pow(10, n)
    elif p == 1: 
      y = 2 * math.pow(10, n)
    else: 
      y = 1 * math.pow(10, n)
    l[1] = l[0]
    l[0] = y
    i = i + 1
  if y == x: return y
  else: return l[1]

def C(x):
  sgn = 1
  if x < 0: sgn = -1
  pow_int = int("{:.1e}".format(x).split("e")[1])

  res = 0
  if pow_int >= 0: res = A(abs(x), pow_int)
  else: res = B(abs(x), pow_int)

  return sgn * res

print(C(x))