# the newest!
# assessment 1

def gcd(m,n) -> int:
    """Calculates the greatest common denominator between two numbers.

    Args:
        x (int): Number One
        y (int): Number Two

    Returns:
        int: The GCD of the two numbers
    """
    if m< n:
        (m,n) = (n,m)
    if(m%n) == 0:
        return n
    else:
        return (gcd(n, m % n)) # recursion taking place

# gcd
print(gcd(8,12))
