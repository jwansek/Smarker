# assessment A
# student id: 4

def gcd(x,y):
    if x > y:
        small = y
    else:
        small = x
    for i in range(1, small+1):
        if((x % i == 0) and (y % i == 0)):
            g = i
              
    return g

# calling function with parameters and printing it out
print(gcd(8,12))
