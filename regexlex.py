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
    r'([A-Za-z0-9_]+)'
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
((r+R+s+e+E+f+a+q+Q+t+T+d+w+W+c+z+x+v+g).(k+o+i+O+j+p+u+P+h+h.k+h.o+h.l+y+n+n.j+n.p+n.l+b+m+m.l+l).(_+r+R+r.t+s+s.w+s.g+e+f+f.r+f.a+f.q+f.t+f.x+f.v+f.g+a+q+q.t+t+T+d+w+c+z+x+v+g))*
'''
#((1+2+2.a+4+5+5.a+7+8+7.a+7.a.a+1.a+2.a.a+5.a.a+8.a+1.b+2.a.b+5.a.b+7.b+7.a.b)(3+3.9+3.a+3.a.9+3.3+3.3.9+3.3.a+3.3.a.9+6+6.3+6.3.9+6.9+6.a+6.6+6.6.3+6.6.3.9+6.6.9+6.6.a+0+0.9+9)(_+1+1.7+2+2.7.a+2.8.a+2.a+4+4.1+4.5+4.5.a+4.7+4.2.a.a+4.5.a.a+4.8.a+5+5.a+5.a.7+7+8+7.a+7.a.a+1.a+2.a.a+5.a.a+8.a+1.b+7.b))*
#(0+(1.((0.1)*.(0.0)*.0)*.1)*)*+_
lexer.input(data)


class Node:
    def __init__(self, children = None, val = None):
        self.children = children
        self.val = val


'''
Grammar
primary -> phi | eps | symbol | ( expression )
factor -> primary | factor*
term -> factor | term . factor
expression -> term | expression + term
'''
'''
regex -> postfix -> nfa
'''

# ---------------------------------------------
# regular expression to postfix
# ---------------------------------------------

class Stack:
    def __init__(self):
        self.symbol_stack = []
        self.postfix_stack = []
        self.precedence = {'LPAREN':0, 'UNION':1, 'CONCAT':2, 'CLOSURE':3}
    

    def read(self, token):
        if token.type == "SYMBOL":
            self.postfix_stack.append(token.value)
        elif token.type == "RPAREN":
            while True:
                if self.symbol_stack[-1] == "LPAREN":
                    self.symbol_stack.pop()
                    break
                self.postfix_stack.append(self.symbol_stack.pop())
        elif token.type == "LPAREN":
            if self.symbol_stack and self.precedence[self.symbol_stack[-1]] == 3:
                self.postfix_stack.append(self.symbol_stack.pop())
            self.symbol_stack.append(token.type)
        else:
            while self.symbol_stack \
                    and self.precedence[self.symbol_stack[-1]] >= self.precedence[token.type]:
                self.postfix_stack.append(self.symbol_stack.pop())
            self.symbol_stack.append(token.type)
    

    def clear_symbol_stack(self):
        while self.symbol_stack:
            self.postfix_stack.append(self.symbol_stack.pop())


stack = Stack()

while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)
    stack.read(tok)

stack.clear_symbol_stack()

print("symbol_stack ", stack.symbol_stack)
print("postfix_stack ", stack.postfix_stack)

postfix = []
postfix[:] = stack.postfix_stack[:]

binary = ["UNION", "CONCAT"]
unary = ["CLOSURE"]
symbols = list(set(postfix) - set(binary) - set(unary))
del stack


# ---------------------------------------------
# postfix to tree
# ---------------------------------------------

class Node:
    def __init__(self, val, children = []):
        self.val = val
        if val in symbols:
            self.type = "SYMBOL"
        else:
            self.type = val
        self.children = children


    # test
    def pref(self):
        if self:
            print(self.val, self.children)
            for i in self.children:
                pref(i)


def post2tree(postfix, unary, binary):
    stack = []

    for i in postfix:
        if i in unary:
            children = [stack.pop()]
            node = Node(i, children)
        elif i in binary:
            children = list(reversed([stack.pop(), stack.pop()]))
            node = Node(i, children)
        else:
            node = Node(i)
        stack.append(node)
    return stack[-1]


root = post2tree(postfix, unary, binary)
# pref(root)


# ---------------------------------------------
# tree to nfa
# ---------------------------------------------

from fa import *

def tree2nfa(root):
    nfa = FA()
    nfa.states.append('0')
    nfa.initial = '0'
    nfa.inputs = symbols[:]

    def make_nfa(node, final = None):
        current_state = str(len(nfa.states)-1)
        if node.type == "UNION":
            nfa.states.append(str(len(nfa.states)))
            final = nfa.states[-1]
            for c in node.children:
                nfa.states.append(str(len(nfa.states)))
                nfa.rule.append([current_state, "_", nfa.states[-1]])
                make_nfa(c, final)
                nfa.rule.append([nfa.rule[-1][-1], "_", final])
        elif node.type == "CONCAT":
            make_nfa(node.children[0])
            current_state = nfa.rule[-1][-1]
            nfa.states.append(str(len(nfa.states)))
            next_state = nfa.states[-1]
            nfa.rule.append([current_state, "_", next_state])
            make_nfa(node.children[1])
        elif node.type == "CLOSURE":
            nfa.states.append(str(len(nfa.states)))
            final = nfa.states[-1]
            nfa.rule.append([current_state, "_", final])
            nfa.states.append(str(len(nfa.states)))
            next_state = nfa.states[-1]
            nfa.rule.append([current_state, "_", next_state])
            make_nfa(node.children[0])
            nfa.rule.append([nfa.rule[-1][-1], "_", next_state])
            nfa.rule.append([nfa.rule[-2][-1], "_", final])
        else:
            nfa.states.append(str(len(nfa.states)))
            nfa.rule.append([current_state, node.val, nfa.states[-1]])


    make_nfa(root)
    print(nfa.states)
    nfa.make_rule_total()
    nfa.make_e_closure()
    nfa.accepts.append(nfa.rule[-1][2])
    print(len(nfa.states), len(nfa.rule), len(nfa.inputs))

    return nfa


nfa = tree2nfa(root)
print(nfa.accepts)
dfa = nfa.to_DFA()
mdfa = dfa.to_m_DFA()
print(mdfa)
