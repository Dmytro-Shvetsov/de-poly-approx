import math


def poly_function_maker(input_string):
    coeffs = list(map(float, input_string.split()))
    def poly(x):
        val = 0
        for i in range(len(coeffs)):
            # print(coeffs[i], len(coeffs) - i - 1)
            val += x**(len(coeffs) - i - 1) * coeffs[i]
        return val
    return coeffs, poly
