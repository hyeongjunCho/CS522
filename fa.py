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
        dfa.inputs = self.inputs[:]
        
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
                #print(states)
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
            print("i",i,"len",len(dfa.states_dict))
        dfa.make_rule_total()
        for i in dfa.rule_total:
            for j in i:
                if j != "None" and len(j) > 2:
                    print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", i)
        dfa.is_DFA = True
        print(dfa.states)
        print(dfa.accepts)

        return dfa


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
            #print("l", l, "len", len(equivalent))
            #print("equivalent", equivalent)
            for input in self.inputs:
                for states in equivalent:
                    temp_states = []
                    for i in range(len(equivalent)):
                        temp_states.append(["None"])
                    for state in states:
                        temp = self.rule_total[self.states.index(state)][self.inputs.index(input)]
                        if temp != "None":
                            temp = temp[0]
                            #print("temp", temp)
                        for i in range(len(equivalent)):
                            if equivalent[i].count(temp) == 1:
                                temp_states[i].append(state)
                    next_states = []
                    #print("temp_states", temp_states)
                    for s in temp_states:
                        if len(s) > 1:
                            next_states.append(s[1:])

                    if len(next_states) > 1:
                        flag = 1
                        break

                if flag == 1:
                    break
            print("states", states)
            print("next_states", next_states)


            if flag == 1:
                equivalent.remove(states)
                equivalent.extend(next_states)
                continue
            
            if l == len(equivalent):
                break
            

        print("self.states", self.states)
        print("self.rule_total", self.rule_total)
        print("self.inputs", self.inputs)
        print("self.accepts", self.accepts)
        print("equivalent", equivalent)
        print("len equi", len(equivalent))




















