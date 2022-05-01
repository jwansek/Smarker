def gcd(m,n):
    if m< n:
        (m,n) = (n,m)
    if(m%n) == 0:
        return n
    else:
        return (gcd(n, m % n)) # recursion taking place

# calling function with parameters and printing it out
print(gcd(8,12))
