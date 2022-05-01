def gcd(p,q):
    """Docstring gcd"""
    if p < q:
        (p,q) = (q,p)
    if(p%q) == 0:
        return q
    else:
        return (gcd(q, p % q)) # recursion taking place

# calling function with parameters and printing it out
print(gcd(8,12))
