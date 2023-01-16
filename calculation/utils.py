import math


def poly_function_maker(coeffs):
    if isinstance(coeffs, str):
        coeffs = list(map(float, coeffs.split()))
    def poly(x):
        val = 0
        for i in range(len(coeffs)):
            # print(coeffs[i], len(coeffs) - i - 1)
            val += x**(len(coeffs) - i - 1) * coeffs[i]
        return val
    return coeffs, poly
