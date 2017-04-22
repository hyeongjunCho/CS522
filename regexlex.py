# ply-3.10

# regexlex.py
# string, (, ), *, +, .

import ply.lex as lex

# List of token names.
tokens = (
        'SYMBOL',
        'UNION',
        'CLOSURE',
        'CONCAT',
        'LPAREN',
        'RPAREN',
        )

t_UNION = r'\+'
t_CLOSURE = r'\*'
t_CONCAT = r'\.'
t_LPAREN = r'\('
t_RPAREN = r'\)'


def t_SYMBOL(t):
    r'([A-Za-z]+)'
    t.value = t.value
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

t_ignore = ' \t'


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()
data = '''
( abc * + aa ) . b
'''
lexer.input(data)


'''
while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok.type, tok.value, tok.lineno, tok.lexpos)
'''


class Node:
    def __init__(self, children = None, val = None):
        self.children = children
        self.val = val


'''
Grammar
primary -> pi | eps | symbol | ( expression )
factor -> primary | factor*
term -> factor | term . factor
expression -> term | expression + term
'''
class Stack:
    def __init__(self):
        self.symbol_stack = []
        self.tree = Node()
    

    def push(self, token):
        self.symbol_stack.append({type: token.type, value: token.value})


    def reduce(self, token = None):
        if token:
            pass
        else:
            pass


stack = Stack()
while True:
    tok = lexer.token()
    if not tok:
        break
    stack.reduce(tok)
    stack.push(tok)


stack.reduce()












