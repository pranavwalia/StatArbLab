from sympy import false, true

'''
Checks if a sequence is restricted to the domain of elements
'''
def isSequenceOf(sequence: list, elements: list) -> bool:
    for i in sequence:
        if not i in elements:
            return False
    return True
