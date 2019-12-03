import re, sys
from collections import defaultdict

def truncate(n, decimals=10):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

def check2gramConstraint(dict_obj, t1, haslgprob):
    sum_prob = 0
    if haslgprob:
        for t2 in dict_obj[t1]:
            sum_prob += dict_obj[t1][t2][0]
    else:
        for t2 in dict_obj[t1]:
            sum_prob += dict_obj[t1][t2]
    return sum_prob

def check3gramConstraint(dict_obj, t1, t2, haslgprob):
    sum_prob = 0
    if haslgprob:
        for t3 in dict_obj[t1][t2]:
            sum_prob += dict_obj[t1][t2][t3][0]
    else:
        for t3 in dict_obj[t1][t2]:
            sum_prob += dict_obj[t1][t2][t3]
    return sum_prob
    
def checkProb(is2gram, haslgprob, transition_dict, emission_dict):
    if is2gram:
        critical_value = 0.9999999
    else:
        critical_value = 1

    for t1 in transition_dict:
        if is2gram:
            sum_prob = check2gramConstraint(transition_dict, t1, haslgprob)
            if sum_prob < critical_value or sum_prob > 1:
                print("warning: the trans_prob_sum for state " + t1 + " is " + str(truncate(sum_prob)))
                
        else:
            for t2 in transition_dict[t1]:
                sum_prob = check3gramConstraint(transition_dict, t1, t2, haslgprob)
                if sum_prob < critical_value or sum_prob > 1:
                    print("warning: the trans_prob_sum for state " + t1 + " " + t2 + " is " + str(truncate(sum_prob)))
                    
        
    for t1 in emission_dict:
        sum_prob = check2gramConstraint(emission_dict, t1, haslgprob)
        if sum_prob < 0.99 or sum_prob > 1:
            print("warning: the emiss_prob_sum for state " + t1 + " is " + str(truncate(sum_prob)))
            
            
    for t1 in transition_dict:
        if t1 not in emission_dict:
            print("warning: the emiss_prob_sum for state " + t1 + " is 0")
            
        
if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        data = f.readlines()
    data = [re.sub("\s+", "\t", line.replace("\n", "")) for line in data]

    for idx, line in enumerate(data):
        if line == "":
            end_header = idx
            break

    for idx, line in enumerate(data):
        if line == "\\init":
            start_init = idx+1
        elif line == "\\transition":
            end_init = idx-3
            start_transition = idx+1
        elif line == "\\emission":
            end_transition = idx-1
            start_emission = idx+1

    header = data[:end_header]
    init = data[start_init:end_init]
    transition = data[start_transition:end_transition]
    emission = data[start_emission:]

    is2gram = None
    haslgprob = None

    for line in emission:
        try:
            if len(re.findall("\t", line)) == 2:
                haslgprob = False
                break
            elif len(re.findall("\t", line)) == 3:
                haslgprob = True
                break
        except:
            pass

    if haslgprob is None:
        raise TypeError("Check format to only include prob and optional lgprob.")
    elif haslgprob is True:
        for line in transition:
            try:
                if len(re.findall("\t", line)) == 3:
                    is2gram = True
                    break
                elif len(re.findall("\t", line)) == 4:
                    is2gram = False
                    break
            except:
                pass
    else:
        for line in transition:
            try:
                if len(re.findall("\t", line)) == 2:
                    is2gram = True
                    break
                elif len(re.findall("\t", line)) == 3:
                    is2gram = False
                    break
            except:
                pass
            
            
    if is2gram is None:
        raise TypeError("Only supports bigram and trigram. Check format.")

    header_int = []
    for line in header:
        header_int.append(int(line[line.rfind("=")+1:]))

    header_state_num = header_int[0]
    header_sym_num = header_int[1]
    header_init_line_num = header_int[2]
    header_trans_line_num = header_int[3]
    header_emiss_line_num = header_int[4]

    init_line_num = len(init)
    trans_line_num = len(transition)
    emiss_line_num = len(emission)

    trans_state_set = set()
    sym_set = set()
        
    transition_dict = defaultdict(dict)
    if is2gram:
        if haslgprob:
            for line in transition:
                match = re.match("([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)", line)
                t1 = match.group(1)
                t2 = match.group(2)
                prob = float(match.group(3))
                lgprob = float(match.group(4))
                transition_dict[t1][t2] = (prob, lgprob)
                trans_state_set.add(t1)
        else:
            for line in transition:
                match = re.match("([^\t]+)\t([^\t]+)\t([^\t]+)", line)
                t1 = match.group(1)
                t2 = match.group(2)
                prob = float(match.group(3))
                transition_dict[t1][t2] = prob
                trans_state_set.add(t1)
            
    else:
        if haslgprob:
            for line in transition:
                match = re.match("([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)", line)
                t1 = match.group(1)
                t2 = match.group(2)
                t3 = match.group(3)
                prob = float(match.group(4))
                lgprob = float(match.group(5))
                trans_state_set.add(t1)
                try:
                    transition_dict[t1][t2][t3] = (prob, lgprob)
                except:
                    transition_dict[t1][t2] = {}
                    transition_dict[t1][t2][t3] = (prob, lgprob)
        else:
            for line in transition:
                match = re.match("([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)", line)
                t1 = match.group(1)
                t2 = match.group(2)
                t3 = match.group(3)
                prob = float(match.group(4))
                trans_state_set.add(t1)
                try:
                    transition_dict[t1][t2][t3] = prob
                except:
                    transition_dict[t1][t2] = {}
                    transition_dict[t1][t2][t3] = prob
            
    emission_dict = defaultdict(dict)
    if haslgprob:
        for line in emission:
            match = re.match("([^\t]+)\t([^\t]+)\t([^\t]+)\t([^\t]+)", line)
            pos = match.group(1)
            word = match.group(2)
            prob = float(match.group(3))
            lgprob = float(match.group(4))
            emission_dict[pos][word] = (prob, lgprob)
            sym_set.add(word)
            
    else:
        for line in emission:
            match = re.match("([^\t]+)\t([^\t]+)\t([^\t]+)", line)
            pos = match.group(1)
            word = match.group(2)
            prob = float(match.group(3))
            emission_dict[pos][word] = prob
            sym_set.add(word)
            
    state_num = len(trans_state_set)
    sym_num = len(sym_set)

    for state in emission_dict:
        if state not in trans_state_set:
            if state == "EOS":
                state_num = state_num + 1
            else:
                print("warning: state " + state + " not present in transition.")

    if header_state_num == state_num:
        print(data[0])
        
    else:
        print("warning: different numbers of state_num: claimed=" + str(header_state_num) + ", real=" + str(state_num))
        

    if header_sym_num == sym_num:
        print(data[1])
        
    else:
        print("warning: different numbers of sym_num: claimed=" + str(header_sym_num) + ", real=" + str(sym_num))
        

    if header_init_line_num == init_line_num:
        print(data[2])
        
    else:
        print("warning: different numbers of init_line_num: claimed=" + str(header_init_line_num) + ", real=" + str(init_line_num))
        
        
    if header_trans_line_num == trans_line_num:
        print(data[3])
        
    else:
        print("warning: different numbers of trans_line_num: claimed=" + str(header_trans_line_num) + ", real=" + str(trans_line_num))
        

    if header_emiss_line_num == emiss_line_num:
        print(data[4])
        
    else:
        print("warning: different numbers of emiss_line_num: claimed=" + str(header_emiss_line_num) + ", real=" + str(emiss_line_num))
        

    checkProb(is2gram, haslgprob, transition_dict, emission_dict)