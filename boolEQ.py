#!/usr/bin/python
"""
Author: William Gillespie
Course: COSC 321
Date: 2015-04-18
This program accepts two inputs that are boolean expressions, prints out the
    truth tables for those functions, and prints out whether those functions
    are equal.
The two inputs must have the same set of variables.  Parentheses are permitted.
The NOT is denoted by the # after the variable or parenthesized expression.
The AND is denoted by two variables next to each other (or a variable next to
    a parenthesis, or two parenthesized expressions next to each other).
The OR is denoted by +.
Here is an example:
    A#B#+(AC)#  ----> (not A) and (not B) or (not (A and B))
"""
import re  # import the regular expression library


def eval_func(expr):
    """
    This function returns true or false depending on what the expression evals to.
    It is a recursive function that evals boolean expressions in string format.
    It uses the information of the values for keys in the dictionary to return
    the correct answer.  The dictionary it uses is the symbol_table dictionary,
    which contains the current values of the keys.  This method is called by iterate().
    The function iterate iterates over all the possible combinations that the
    symbol_table dictionary could store and calls this function for every possible
    combination.
    :param expr: The boolean expression to evaluate.  Type: string
    :return:  True if the expression is true, false if it is false
    """

    expr_ls = list(expr)  # expression list
    # check if incoming expression is surrounded fully by parens
    # if so, eval it, if not, let the below code handle it.
    if expr_ls[0] == '(' and expr_ls[-1] == ')':
        middle_expr = expr_ls[1:-1]
        parenStack = []
        highestLevelParenthesizedExpressionFound = True
        for local_char in middle_expr:
            if local_char == '(':
                parenStack.append(local_char)
            elif local_char == ')':
                if len(parenStack) == 0:
                    highestLevelParenthesizedExpressionFound = False
                else:
                    parenStack.pop()

        if highestLevelParenthesizedExpressionFound:
            expr = "".join(middle_expr)
            return eval_func(expr)
    # end of checking if expression is surrounded by parens

    # find the top level or, if there is one.  If so, eval the expressions
    # separated by the or
    or_paren_stack = []
    index_at_which_to_slice = 0
    top_level_or_was_found = False
    for item in expr_ls:
        if item == "(":
            or_paren_stack.append(item)
        elif item == ")":
            or_paren_stack.pop()
        elif item == '+' and len(or_paren_stack) == 0:
            top_level_or_was_found = True
        index_at_which_to_slice += 0 if top_level_or_was_found else 1
    # if the top level or was found, eval each of the surrounding expressions
    if top_level_or_was_found:
        part1 = expr[:index_at_which_to_slice]
        part2 = expr[index_at_which_to_slice+1:]
        return eval_func(part1) or eval_func(part2)
    # end of code to check if there was a top level or
    # if code passes this part, we can assume there is no or at the top level.

    # find parens group for and anding of parens expr and a variable
    # I can assume that there will be and anding of two things.
    # This complicated block of code figures out whether to and a variable and
    # another variable, or a variable and a parenthesized expression.
    and_stack = []
    parens_found_to_left = False
    letter_was_found_at_top_level = False
    index_where_stack_became_zero_first = 0
    index_at_which_to_slice = 0
    for item in expr_ls:
        if item == '(':
            and_stack.append(item)
            parens_found_to_left = True
        elif item == ')':
            and_stack.pop()
            if len(and_stack) == 0 and index_where_stack_became_zero_first == 0:
                index_where_stack_became_zero_first = index_at_which_to_slice
        # In this elif, we know there will be an anding of a letter (variable) and an
        # expression in parenthesis
        elif item.isalpha() and len(and_stack) == 0 and re.search("\(.*\)", expr):
            letter_was_found_at_top_level = True
            if parens_found_to_left:  # var found right of the parens ()
                part1 = expr[:index_at_which_to_slice]
                part2 = expr[index_at_which_to_slice:]
                return eval_func(part1) and eval_func(part2)
            else:  # if the var is left of the parens
                if expr[index_at_which_to_slice+1] == '#':  # the var is "not var"
                    part1 = expr[:index_at_which_to_slice+2]
                    part2 = expr[index_at_which_to_slice+2:]
                    return eval_func(part1) and eval_func(part2)
                else:  # the var is a plain old var with no "not"
                    part1 = expr[:index_at_which_to_slice+1]
                    part2 = expr[index_at_which_to_slice+1:]
                    return eval_func(part1) and eval_func(part2)
        index_at_which_to_slice += 1
    # if there was no var found at top level, we are anding two paren exprs: (A+B)(B+C)
    # or we are anding two parens, one or both notted, (A+B)#(B+C)#
    # or we are notting a group in parens (A+B)#
    # I can assume it will not be a singe paren group : (A+B)
    if not letter_was_found_at_top_level and parens_found_to_left:
        if expr[index_where_stack_became_zero_first+1] == '#':
            part1 = expr[:index_where_stack_became_zero_first+1]
            if len(expr) == index_where_stack_became_zero_first+2:
                return not eval_func(part1)
            else:
                part2 = expr[index_where_stack_became_zero_first+1:]
                return not eval_func(part1) and eval_func(part2)
        else:  # if there are two paren groups: (A+B)(B+C)
            part1 = expr[:index_where_stack_became_zero_first+1]
            part2 = expr[index_where_stack_became_zero_first+1:]
            return eval_func(part1) and eval_func(part2)
    # end of code to see if there was and anding of a variable and
    # a parenthesized expression.

    # code to check for if we need to and a variable and something else,
    # or not a variable and and it with something else.
    if expr[0].isalpha() and len(expr) > 1:
        if expr[1] == '#':
            if len(expr[2:]) == 0:
                return not eval_func(expr[0])
            else:
                return not eval_func(expr[0]) and eval_func(expr[2:])
        else:
            return eval_func(expr[0]) and eval_func(expr[1:])
    # end of code to check for an anding of a variable and something else,
    # or not a variable and and it with something else.

    # BASE CASE: This is the base case where we finally get to return
    # the value for a given key in the symbol table.
    if len(expr) == 1:
        return symbol_table[expr]
# end of the eval_func method


def create_symbol_table(expr):
    """
    This method creates a symbol table from the input of a boolean expression
    :param expr: The boolean expression to be evaluated.  Type: string
    :return:  returns the symbol table dictionary.  Type: dictionary
    """
    temp_symbol_table = {}
    for local_char in expr:
        if local_char.isalpha() and local_char not in temp_symbol_table:
            c = local_char.upper()
            temp_symbol_table[c] = 0  # fill with junk
    return temp_symbol_table


def isCorrectBoolExpression(expr):
    """
    determines whether the expression is correctly formatted.
    This method checks all the ways a boolean function could be formatted, and
    outputs False if it is incorrectly formatted.  Otherwise returns True.
    :param expr: the boolean expression; type: string
    :return:  True if it is correctly formatted, False otherwise; Type bool
    """
    parenStack = []
    charStack = []
    for theChar in expr:
        if theChar.isalpha():
            pass
        elif theChar == '(':
            parenStack.append(theChar)
        elif theChar == ')':
            if len(parenStack) == 0:
                return False
            elif charStack[-1] == '(':
                return False
            elif charStack and charStack[-1] == '+':
                return False
            parenStack.pop()
        elif theChar == '+':
            if len(charStack) == 0:
                return False
            elif charStack[-1] == '+':
                return False
            elif len(parenStack) and charStack[-1] == '(':
                return False
        elif theChar == '#':
            if len(charStack) == 0:
                return False
            elif charStack[-1] == '(':
                return False
        else:
            return False
        charStack.append(theChar)
    if len(parenStack):
        return False
    return True
# end of method isCorrectBoolExpression(expr)

"""
These lists contain snapshots of the dictionaries for a given loop iteration
(corresponding to a combination of values in the truth table)
These Ivars are used in the printing of the truth table.
They are mutated in iterate() and that is why they are above that method.
"""
dict_snapshots = []  # contains the snapshots of the dictionaries in each iteration
                      # to be used for the output of the truth table
dict1_eval_results = []
dict2_eval_results = []


def iterate(item, my_list):  # string and list for parameters
    """
    Description: this methods iterates through all of the possible values that
                    the keys in the symbol table can have.  It is equivalent to
                    iterating over all the combinations of a boolean truth table.
    :param item: the key in the symbol table that we are currently iterating through
                    the values of
    :param my_list: the rest of the keys in the symbol table we have yet to iterate
                        through.
    """
    for index in range(0, 2):
        symbol_table[item] = index
        if len(my_list) == 0:  # BASE CASE
            my_copy = dict(symbol_table)
            dict_snapshots.append(my_copy)
            result1 = eval_func(expr1)
            dict1_eval_results.append(result1)
            result2 = eval_func(expr2)
            dict2_eval_results.append(result2)
            if result1 != result2:
                result[0] = False
        else:  # RECURSIVE CASE
            # if there are still symbols to iterate over, we call iterate on the
            # next symbols as first parameter, and the rest of the symbols as the
            # second parameter, if there are any.
            if len(my_list):
                iterate(my_list[0], my_list[1:])
        # if result[0] is false, we return, go up to higher recursive level
        # and eventually get out of the recursive calls.  Outside this method,
        # we will see that the result[0] == False, meaning that the bool exprs
        # are not equal.
# end of iterate()


# -----------start of script-----------
symbol_table = {}
result = [True]
expr1 = ''
expr2 = ''

while True:  # keep looping until user wants to quit.
    expr1 = raw_input("Enter first boolean expression: ")
    expr1 = expr1.translate(None, " ")  # strips out whitespaces
    expr1 = expr1.upper()
    symbol_table = create_symbol_table(expr1)

    expr2 = raw_input("Enter second boolean expression: ")
    expr2 = expr2.translate(None, " ")
    expr2 = expr2.upper()
    second_symbol_table = create_symbol_table(expr2)

    # if both bool expressions are not correctly formatted, tell user to re-enter
    if not (isCorrectBoolExpression(expr1) and isCorrectBoolExpression(expr2)):
        print 'boolean expressions not formatted correctly; please re-enter.'
        continue

    first_set = set(symbol_table)
    second_set = set(second_symbol_table)
    intersection = first_set.intersection(second_set)
    # if the boolean expressions do not have the same symbols, tell user to re-enter
    if len(intersection) != len(first_set):
        print 'you did not input expressions with the same set of variables'
        print 'please do that.'
        continue
    if not (len(expr1) and len(expr2)):  # if the user entered the empty string
        print 'you must enter two boolean expressions'
        continue  # continue because one or both contain nothing
    for character in list(expr2):
        if character.isalpha() and character.upper() not in symbol_table:
            print 'symbols sets are not the same; re-enter expressions'
            continue

    # puts all the keys in the symbol table into a list
    expr_list = [key for key in symbol_table.keys()]

    # iterates over all of the possibilities for the variables,
    # prints the truth table with the results.
    iterate(expr_list[0], expr_list[1:])  # <--NOTE: computations done here

    # prints out the truth tables
    print '------expr 1 truth table------'
    i = 0
    for dictionary in dict_snapshots:
        res1 = '1' if dict1_eval_results[i] else '0'
        print str(dictionary) + "; result: " + res1
        i += 1

    print '------expr 2 truth table------'
    i = 0
    for dictionary in dict_snapshots:
        res2 = '1' if dict2_eval_results[i] else '0'
        print str(dictionary) + "; result: " + res2
        i += 1

    # reset vars for next iteration
    dict_snapshots = []
    dict1_eval_results = []
    dict2_eval_results = []
    symbol_table = {}

    # prints out whether the results are equal or not.
    if result[0]:
        print "boolean expressions are equal"
    else:
        print "boolean expressions are not equal"
    # reset result to True
    result[0] = True
    # ask user if they want to continue
    if raw_input("CONTINUE? Y/N: ").upper() != 'Y':
        break