
import curses
import os
import time

class FA:
    def __init__(self):
        self.is_DFA = False
        self.states = []
        self.inputs = []
        self.rule = [] #[q0,input,q1]
        self.rule_total = [] #[q0][input]->[q1]
        self.initial = None
        self.accepts = []
        self.e_closures = []


    def make_rule_total(self):
        self.rule_total = [["None"] * len(self.inputs) for i in range(len(self.states))]
        for i in self.rule:
            if self.rule_total[self.states.index(i[0])][self.inputs.index(i[1])] == "None":
                self.rule_total[self.states.index(i[0])][self.inputs.index(i[1])] = [i[2]]
            else:
                self.rule_total[self.states.index(i[0])][self.inputs.index(i[1])].append(i[2])


    def make_e_closure(self):
        for state in self.states:
            states = [state]
            i = 0
            while i < len(states):
                e_closure = self.rule_total[self.states.index(states[i])][self.inputs.index("_")]

                if e_closure != "None":
                    for s in e_closure:
                        if states.count(s) == 0:
                            states.append(s)
                i+=1
            self.e_closures.append(states)


    def e_NFA_travle(self, L):
        current_states = [self.initial]
        next_states = []
        flag = 0

        i = 0
        while i < len(current_states):
            state = current_states[i]
            e_closure = self.e_closures[self.states.index(state)]
            for s in e_closure:
                if current_states.count(s) == 0:
                    current_states.append(s)
            i+=1
        current_states.sort(key=lambda x: int(x))
        while len(L)>0:
            next_states = []
            flag = 0
            for current_state in current_states:
                states = self.rule_total[self.states.index(current_state)][self.inputs.index(L[0])]
                if states != 'None':
                    flag = 1
                    for s in states:
                        if next_states.count(s) == 0:
                            next_states.append(s)
            if flag == 0:
                print("아니오")
                return
            L = L[1:]

            current_states = []
            for state in next_states:
                e_closure = self.e_closures[self.states.index(state)]
                for s in e_closure:
                    if current_states.count(s) == 0:
                        current_states.append(s)
            current_states.sort(key=lambda x: int(x))
        for current_state in current_states:
            if len(L) == 0 and self.accepts.count(current_state) == 1:
                print("네")
                return
        print("아니오")


    def to_DFA(self):
        dfa = FA()
        #dfa.inputs = self.inputs[:]
        dfa.inputs = list(set(self.inputs) - set(["_"]))
        
        init = self.e_closures[self.states.index(self.initial)]

        dfa.states_dict = {}
        dfa.states_dict["0"] = init
        dfa.states.append("0")
        dfa.initial = "0"

        i = 0
        while i < len(dfa.states):
            for input in dfa.inputs:
                states = []
                for state in dfa.states_dict[dfa.states[i]]:
                    temp_states = self.rule_total[self.states.index(state)][self.inputs.index(input)]
                    if temp_states != "None":
                        for temp_state in temp_states:
                            closure = self.e_closures[self.states.index(temp_state)]
                            for s in closure:
                                if states.count(s) == 0:
                                    states.append(s)
                states.sort(key = lambda x: int(x))


                if states in dfa.states_dict.values():
                    next_state = list(dfa.states_dict.keys())[list(dfa.states_dict.values()).index(states)]
                else:
                    next_state = str(len(dfa.states))
                    dfa.states_dict[next_state] = states[:]
                    dfa.states.append(next_state)

                if dfa.rule.count([dfa.states[i], input, next_state]) == 0:
                    dfa.rule.append([dfa.states[i], input, next_state])
                    for s in dfa.states_dict[next_state]:
                        if self.accepts.count(s) == 1 and dfa.accepts.count(next_state) == 0:
                            dfa.accepts.append(next_state)
                            break
            i += 1
        dfa.make_rule_total()
        dfa.is_DFA = True

        return dfa


    def DFA_travle(self, L):
        current_state = self.initial
        flag = 0
        while len(L) > 0:
            if self.inputs.count(L[0]) == 1:
                temp = [self.states.index(current_state), self.inputs.index(L[0])]
                if self.rule_total[temp[0]][temp[1]] != "None":
                    current_state = self.rule_total[temp[0]][temp[1]][0]
                    L = L[1:]
                    flag = 1
            if flag == 0:
                print("아니오")
                return
        if len(L) == 0 and self.accepts.count(current_state) == 1:
            print("네")
        else:
            print("아니오")


    def to_m_DFA(self):
        if not self.is_DFA:
            return (self.to_DFA()).to_m_DFA()
        mdfa = FA()
        mdfa.inputs = self.inputs[:]
        mdfa.states_dict = {}
        
        equivalent = [list(set(self.states)-set(self.accepts)), self.accepts]

        while True:
            l = len(equivalent) # checks for changes of the equivalent
            flag = 0
            for input in self.inputs:
                for states in equivalent:
                    temp_states = []
                    for i in range(len(equivalent)):
                        temp_states.append(["None"])
                    for state in states:
                        temp = self.rule_total[self.states.index(state)][self.inputs.index(input)]
                        if temp != "None":
                            temp = temp[0]
                        for i in range(len(equivalent)):
                            if equivalent[i].count(temp) == 1:
                                temp_states[i].append(state)
                    next_states = []
                    for s in temp_states:
                        if len(s) > 1:
                            next_states.append(s[1:])

                    if len(next_states) > 1:
                        flag = 1
                        break

                if flag == 1:
                    break


            if flag == 1:
                equivalent.remove(states)
                equivalent.extend(next_states)
                continue
            
            if l == len(equivalent):
                break
            

        equivalent.sort(key=lambda x: int(x[0][:]))

        num = 0
        for i in range(len(equivalent)):
            name = "q" + str(num)
            mdfa.states_dict[name] = equivalent[i]
            mdfa.states.append(name)
            for j in range(len(equivalent[i])):
                if self.initial == equivalent[i][j]:
                    mdfa.initial = name
                if self.accepts.count(equivalent[i][j]) == 1 and mdfa.accepts.count(name) == 0:
                    mdfa.accepts.append(name)
            num += 1

        mdfa.rule_total = [["None"] * len(mdfa.inputs) for i in range(len(mdfa.states))]
        for i in range(len(mdfa.states)):
            for j in range(len(mdfa.inputs)):
                for k in range(len(mdfa.states)):
                    if mdfa.states_dict[mdfa.states[k]].count(self.rule_total[self.states.index(mdfa.states_dict[mdfa.states[i]][0])][j][0]) == 1:
                        mdfa.rule_total[i][j] = [mdfa.states[k]]
                        break

        print("states :", mdfa.states)
        print("dict :", mdfa.states_dict)
        print("inputs :", mdfa.inputs)
        print("initial :", mdfa.initial)
        print("accepts :", mdfa.accepts)
        print("rules :", mdfa.rule_total)
        
        return mdfa


    def chosung_wooseon(self, input_string):
        if self.jongsung:
            if self.jongsung + self.daeum in self.jongset and input_string in self.choset:
                self.jongsung = self.jongsung + self.daeum
                self.daeum = input_string
            elif input_string in self.jungset:
                print("jong", self.chosung, self.jungsung, self.jongsung, self.daeum)
                temp = self.daeum
                self.daeum = ""
                self.completed = self.completed + str(self.make_hangul())
                self.chosung = temp
                self.jungsung = input_string
                self.jongsung = ""
        elif self.daeum:
            print("dauem", self.chosung, self.jungsung, self.jongsung, self.daeum)
            if self.daeum in self.jongset and input_string in self.choset:
                self.jongsung = self.daeum
                self.daeum = input_string
            elif input_string in self.jungset:
                temp = self.daeum
                self.daeum = ""
                self.completed = self.completed + str(self.make_hangul())
                self.chosung = temp
                self.jungsung = input_string
                self.jongsung = ""
                pass
        elif self.jungsung:
            if input_string in self.choset:
                self.daeum = input_string
            elif self.jungsung + input_string in self.jungset:
                self.jungsung = self.jungsung + input_string
        elif self.chosung:
            if input_string in self.jungset:
                self.jungsung = input_string
            elif self.chosung + input_string in self.choset:
                self.chosung = self.chosung + input_string
        else:
            if input_string in self.choset:
                self.chosung = input_string

        
    def hangulmoa(self):
        win = curses.initscr()
        curses.cbreak()

        win.nodelay(True)

        clear = lambda: os.system('clear')

        s = ""

        self.chosung = ""
        self.jungsung = ""
        self.jongsung = ""
        self.daeum = ""
        self.completed = ""
        current_state = self.initial
        self.choset = ["r", "R", "s", "e", "E", "f", "a", "q", "Q", "t", "T", "d", "w", "W", "c", "z", "x", "v", "g"]
        self.jungset = ["k", "o", "i", "O", "j", "p", "u", "P", "h", "hk", "ho", "hl", "y", "n", "nj", "np", "nl", "b", "m", "ml", "l"]
        self.jongset = ["", "r", "R", "rt", "s", "sw", "sg", "e", "f", "fr", "fa", "fq", "ft", "fx", "fv", "fg", "a", "q", "qt", "t", "T", "d", "w", "c", "z", "x", "v", "g"]
        
        clear()
        while True:
            key = win.getch()
            if key != -1:
                clear()
                print("current_state", current_state)
                if chr(key) == "!":
                    self.chosung = ""
                    self.jungsung = ""
                    self.jongsung = ""
                    self.daeum = ""
                    self.completed = ""
                    current_state = self.initial
                    self.hangulprint()
                else:
                    current_string = self.chosung+self.jungsung+self.jongsung+self.daeum
                    if chr(key) == " ":
                        if self.completed:
                            self.completed = self.completed + str(self.make_hangul()) + " "
                        else:
                            self.completed = str(self.make_hangul())
                        current_state = self.initial
                        self.chosung = ""
                        self.jungsung = ""
                        self.jongsung = ""
                        self.daeum = ""   
                        self.hangulprint()
                    elif key == 127: # delete
                        if self.daeum:
                            self.daeum = self.daeum[:-1]
                            current_state = self.steps(current_string[:-1])
                        elif self.jongsung:
                            self.jongsung = self.jongsung[:-1]
                            current_state = self.steps(current_string[:-1])
                        elif self.jungsung:
                            self.jungsung = self.jungsung[:-1]
                            current_state = self.steps(current_string[:-1])
                        elif self.chosung:
                            self.chosung = self.chosung[:-1]
                            current_state = self.steps(current_string[:-1])
                        elif self.completed:
                            self.completed = self.completed[:-1]
                            current_state = self.initial
                        self.hangulprint()
                    elif chr(key) in self.inputs:
                        if self.rule_total[self.states.index(current_state)][self.inputs.index(chr(key))][0] == "q1":
                            if self.completed:
                                self.completed = self.completed + str(self.make_hangul())
                            else:
                                self.completed = str(self.make_hangul())
                            if chr(key) in self.choset:
                                current_state = self.rule_total[self.states.index(self.initial)][self.inputs.index(chr(key))][0]
                                self.chosung = ""
                                self.jungsung = ""
                                self.jongsung = ""
                                self.daeum = ""   
                                self.chosung_wooseon(str(chr(key)))
                            elif chr(key) in self.jungset:
                                self.chosung = ""
                                self.jungsung = ""
                                self.jongsung = ""
                                self.daeum = ""   
                                if self.completed:
                                    self.completed = self.completed + str(chr(self.jungset.index(chr(key)) + 0x1161))
                                else:
                                    self.completed = str(chr(self.jungset.index(chr(key)) + 0x314F))
                                current_state = self.initial
                        else:
                            current_state = self.rule_total[self.states.index(current_state)][self.inputs.index(chr(key))][0]
                            self.chosung_wooseon(str(chr(key)))
                        self.hangulprint()
                        


            time.sleep(0.01)

        
    def make_hangul(self):
        if self.jongsung:
            if self.daeum:
                return str(chr(self.choset.index(self.chosung) * 588 + self.jungset.index(self.jungsung) * 28 + self.jongset.index(self.jongsung) + 44032)) + str(chr(self.choset.index(self.daeum) + 0x1100))
            else:
                return str(chr(self.choset.index(self.chosung) * 588 + self.jungset.index(self.jungsung) * 28 + self.jongset.index(self.jongsung) + 44032))
        elif self.daeum:
            return str(chr(self.choset.index(self.chosung) * 588 + self.jungset.index(self.jungsung) * 28 + 44032)) + str(chr(self.choset.index(self.daeum) + 0x1100))
        elif self.jungsung:
            return chr(self.choset.index(self.chosung) * 588 + self.jungset.index(self.jungsung) * 28 + 44032)
        elif self.chosung:
            return chr(self.choset.index(self.chosung) + 0x1100)
        else:
            return ""



    def steps(self, current_string):
        current_state = self.initial
        while len(current_string) > 0:
            if self.inputs.count(current_string[0]) == 1:
                temp = [self.states.index(current_state), self.inputs.index(current_string[0])]
                if self.rule_total[temp[0]][temp[1]][0] != "q1":
                    current_state = self.rule_total[temp[0]][temp[1]][0]
                    current_string = current_string[1:]
                else:
                    return None
                    

        if len(current_string) == 0:
            return current_state


    def hangulprint(self):
        print(self.completed + str(self.make_hangul()))

















