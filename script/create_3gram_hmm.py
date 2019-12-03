import re, sys, math
from collections import Counter

def truncate(n, decimals=10):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

def print3gramCounter(counter_obj):
    # Sort first by first word alphabetically, then by second word alphabetically, then by third word alphabetically
    sorted_counter = sorted(counter_obj.items(), key=lambda item: (item[0][0], item[0][1], item[0][2]))
    for entry in sorted_counter:
        lgprob = truncate(math.log10(entry[1]))
        f.write(str(entry[0][0])+"\t"+str(entry[0][1])+"\t"+str(entry[0][2])+"\t"+str(entry[1])+"\t"+str(lgprob))
        f.write("\n")

def print2gramCounter(counter_obj):
    # Sort first by first word alphabetically, then by second word alphabetically
    sorted_counter = sorted(counter_obj.items(), key=lambda item: (item[0][0], item[0][1]))
    for entry in sorted_counter:
        lgprob = truncate(math.log10(entry[1]))
        f.write(str(entry[0][0])+"\t"+str(entry[0][1])+"\t"+str(entry[1])+"\t"+str(lgprob))
        f.write("\n")


if __name__ == "__main__":

    data = sys.stdin.readlines()
    out = sys.argv[1]
    l1 = float(sys.argv[2])
    l2 = float(sys.argv[3])
    l3 = float(sys.argv[4])
    with open(sys.argv[5], "r") as f:
        unk = f.readlines()

    unk_dict = {}
    for line in unk:
        pair = line.replace("\n", "").split(" ")
        unk_dict[pair[0]] = float(pair[1])

    words = []
    pos = []

    for line in data:
        line = "bos/BOS " + line.replace("\n", " eos/EOS")
        pairs = line.split(" ")
        words_line = [pair[:pair.rfind('/')] for pair in pairs]
        pos_line = [pair[pair.rfind('/')+1:] for pair in pairs]
        words.append(words_line)
        pos.append(pos_line)

    transition_dict = {}
    emission_dict = {}

    bigram_pos_freq = Counter()
    trigram_pos_freq = Counter()
    pos_freq = Counter()
    word_pair_freq = Counter()

    state_num = len(set([item for sublist in pos for item in sublist]))
    sym_num = len(set([item for sublist in words for item in sublist]))
    num_tokens = len([item for sublist in pos for item in sublist])


    for i in range(len(pos)):
        pos_line = pos[i]
        words_line = words[i]
        bigram_pos_freq += Counter(zip(pos_line, pos_line[1:]))
        trigram_pos_freq += Counter(zip(pos_line, pos_line[1:], pos_line[2:]))
        pos_freq += Counter(pos_line)
        word_pair_freq += Counter(zip(pos_line, words_line))
        

    for entry in trigram_pos_freq:
        p1 = pos_freq[entry[2]] / num_tokens
        p2 = bigram_pos_freq[(entry[1], entry[2])] / pos_freq[entry[1]]
        p3 = trigram_pos_freq[entry] / bigram_pos_freq[(entry[0], entry[1])]
        trigram_pos_prob = l1*p1 + l2*p2 + l3*p3

        #if bigram_pos_freq[entry] == 0:
            #trigram_pos_prob = 1/(state_num-2+1)
        #else:
            #trigram_pos_prob = l1*p1 + l2*p2 + l3*p3
        
        transition_dict[entry] = truncate(trigram_pos_prob)
        
    for entry in word_pair_freq:
        if entry[0] in unk_dict:
            emission_dict[entry] = truncate((word_pair_freq[entry] / pos_freq[entry[0]])*(1-unk_dict[entry[0]]))
        else:
            emission_dict[entry] = truncate(word_pair_freq[entry] / pos_freq[entry[0]])

    state_num = len(set([item for sublist in pos for item in sublist]))
    sym_num = len(set([item for sublist in words for item in sublist]))
    init_line_num = 1
    trans_line_num = len(transition_dict)
    emiss_line_num = len(emission_dict)

    
    with open(out, 'w') as f:
        f.write("state_num=" + str(state_num))
        f.write("\n")
        f.write("sym_num=" + str(sym_num))
        f.write("\n")
        f.write("init_line_num=" + str(init_line_num))
        f.write("\n")
        f.write("trans_line_num=" + str(trans_line_num))
        f.write("\n")
        f.write("emiss_line_num=" + str(emiss_line_num ))
        f.write("\n")
        f.write("\n")
        f.write("\\init")
        f.write("\n")
        f.write("BOS\t1.0\t0.0")
        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write("\n")
        f.write("\\transition")
        f.write("\n")
        print3gramCounter(transition_dict)
        f.write("\n")
        f.write("\\emission")
        f.write("\n")
        print2gramCounter(emission_dict)
    
