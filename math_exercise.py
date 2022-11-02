from random import randint, choice

def create_math_problem(max):
    """Create random arithmetic problem."""
    operators = ['+', '-', 'x']
    num1 = str(randint(1,max))
    num2 = str(randint(1,max))
    operator = choice(operators)

    problem = ' '.join([num1,operator,num2])
    return problem