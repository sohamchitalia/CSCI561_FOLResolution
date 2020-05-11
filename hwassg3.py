import copy
import signal

# def signal_handler(signum, frame):
#     raise Exception("Timed out!")

# signal.signal(signal.SIGALRM, signal_handler)
# signal.alarm(20)   # Ten seconds
depth = 10
def convertKbtoCNF(sentences):
    cnfKB = []
    for s in sentences:
        cnfKB.append(queryToCNF(s).strip())

    return cnfKB

def getconstants(query):
    querysplit = query.split("(")
    name = querysplit[0]
    args = querysplit[1][0:-1].split(",")
    op = []
    for a in args:
        if a[0].isupper():
            op.append(a)
    return op

def simplesent(sent):
    if "|" in sent:
        return False
    else:
        sentencepartition = sent.split("(")
        pred = sentencepartition[0]
        args = sentencepartition[1][0:-1].split(",")
        for i in args:
            if i[0].islower():
                return False
        return True

def atomicwithvars(sent):
    if "|" in sent:
        return False
    else:
        sentencepartition = sent.split("(")
        pred = sentencepartition[0]
        args = sentencepartition[1][0:-1].split(",")
        for i in args:
            if i[0].isupper():
                return False
        return True


def queryToCNF(s):
    if "=>" in s:
        qparts = s.split(" => ")
        ante = qparts[0]
        conse = qparts[1]
        if " & " in ante:
            clauses = ante.split(" & ")
            st = ""
            for c in clauses:
                if c[0] == "~":
                    st = st + c[1:]
                    st = st + " | "
                else:
                    st = st + "~" + c 
                    st = st + " | "
            st = st + conse
        else:
            st = ""
            if ante[0] == "~":
                st = st + ante[1:]
                st = st + " | "
            else:
                st = st + "~" + ante 
                st = st + " | "
            st = st + conse
        return st.strip()
    else:
        return s.strip()


def standardize(kb):
    counter = 0
    newkb = []
    for sentence in kb:
        dc = dict()
        newsent = ""
        clauses = sentence.split(" | ")
        for c in clauses:
            parts = c.split("(")
            args = parts[1][0:-1]
            arglist = args.split(",")
            for ag in arglist:
                if "a" <= ag <= "z":
                    if ag not in dc.keys():
                        dc[ag] = "v" + '{0:03}'.format(counter)
                        counter+=1

            for i in range(len(arglist)):
                x = arglist[i]
                if "a" <= x <= "z":
                    y = dc[x]
                    arglist[i] = y
            newclause = parts[0] + "(" + ",".join(arglist) + ")"
            newsent = newsent + newclause + " | "
        newkb.append(newsent[0:-3])
    return newkb

def makingkb(kb, dc):
    # predsdict = dict()
    for sentence in kb:
        clauses = sentence.split(" | ")
        for clause in clauses:
            predicate = clause.split("(")[0]
            if predicate in dc.keys():
                if sentence not in dc[predicate]:
                    dc[predicate].append(sentence)
            else:
                dc[predicate] = [sentence]
    return dc


def resolution(query, kb, simple, atvar, fo):
    ##print("\nbefore -- ",kb)
    ##print("\n Query -- ", query)
    querystacklist = []
    query.replace(" ", "")
    if query[0] != "~":
        newquery = "~"+query
    else:
        newquery = query[1:]
    querystacklist.append(newquery)
    newkb = copy.deepcopy(kb)
    newquerypred = newquery.split("(")[0]
    if newquerypred in newkb.keys():
        newkb[newquerypred].append(newquery)
    else:
        newkb[newquerypred] = [newquery]
    ##print("\nAfter -- ", newkb)
    ##print("\n new Query -- ", newquery)
    op = resolve(querystacklist, 0, newkb, simple, atvar)
    if op:
        ##print("TRUEEEE")
        fo.write("TRUE")
        return
    else:
        ##print("FALSEEE")
        fo.write("FALSE")
        return

def checkunifiyatvar(tempatvar, queryargslist):
    for v in tempatvar:
        vpartition = v.split("(")
        vpred = vpartition[0]
        varglist = vpartition[1][0:-1].split(",")
        if unify(queryargslist, varglist):
            return True
    return False


def resolve(querystack, iterations, kb, simple, atvar):
    ##print("\nQuery stack is -- ", querystack)
    # ##print(querystack, "\n")
    if iterations >=80:
        return False
    tempatvar = copy.deepcopy(atvar)

    while querystack:
        q = querystack.pop(-1)
        if "~" in q:
            q = q[1:]
        else:
            q = "~"+q
        q = q.rstrip()
        # ##print("\n Query --- ",q)
        querypartition = q.split("(")
        predicate = ""
        predicate = predicate + querypartition[0]
        queryargs = querypartition[1][0:-1]
        queryargslist = queryargs.split(",")

        if predicate not in kb.keys():
            # ##print("Predicate not in KB")
            return False
        else:
            predicatesentences = kb[predicate]
            ##print("\nPredicate sentences -- ", predicatesentences)
            for sentence in predicatesentences:
                ##print("Current sentence -- ", sentence)
                clauses = sentence.split(" | ") # clauses = atomic
                ####print("Clauses --- ", clauses)
                predicatematch = ""
                for cl in clauses:
                    c = cl.split("(")[0]
                    if predicate == c:
                        predicatematch = cl # check with predicate == c
                ##print(predicatematch)
                clauseargs = predicatematch.split("(")[1][0:-1].split(",")
                unifi = unify(queryargslist, clauseargs)
                
                if unifi:
                    ##print("In unify")
                    submap = {}
                    literals = []
                    for cl in clauses:
                        literals.append(cl)
                    iterations += 1
                    
                    for x in range(len(queryargslist)):
                        qargs = queryargslist[x]
                        cargs = clauseargs[x]
                        if cargs[0].islower() and qargs[0].isupper():
                            if cargs not in submap.keys():
                                submap[cargs] = qargs
                        elif cargs[0] == qargs[0]:
                            if cargs not in submap.keys():
                                submap[cargs] = qargs
                        elif cargs[0].islower() and qargs[0].islower():
                            if cargs not in submap.keys() and qargs not in submap.keys():
                                submap[cargs] = qargs
                        elif cargs[0].isupper() and qargs[0].islower:
                            if qargs not in submap.keys():
                                submap[qargs] = cargs

                    ##print("\nsubmap is -- ",submap)
                    
                    l = len(querystack)
                    qlist = []
                    for qs in querystack:
                        qlist.append(qs)
                    ##print("Query stack after unification -- ", qlist)

                    litst = ""
                    for al in literals:
                        # ##print("Old  -- ", al)
                        alpartition = al.split("(")
                        alpred = alpartition[0]
                        alarglist = alpartition[1][0:-1].split(",")
                        for ag in range(len(alarglist)):
                            if alarglist[ag] in submap.keys():
                                alarglist[ag] = submap[alarglist[ag]]
                        newalarg = ",".join(alarglist)
                        al = alpred + "(" + newalarg + ")"
                        # ##print("New al -- ", al)
                        search = al.split("(")[0]
                        search = search.lstrip()
                        if q != al:
                            litst = litst + al + " | "
                            currentcopy = al
                            off = ""
                            if "~" not in currentcopy:
                                off = "~"+currentcopy
                            else:
                                off = currentcopy[1:]
                            flag = False

                            # for qli in range(0,len(qlist)):
                            #     if qlist[qli] == off:
                            #         del qlist[qli]
                            #         flag = True 

                            if flag == False:
                                qlist.append(currentcopy)

                    # if kb[predicate]:
                    #     newkb = copy.deepcopy(kb)
                        # kb[predicate].remove(sentence)
                    litst = litst[0:-3]
                    newkb = copy.deepcopy(kb)
                    for lit in literals:
                        litsplit = lit.split("(")[0]
                        if litsplit != predicate:
                            if litsplit in newkb.keys():
                                newkb[litsplit].insert(0,litst)
                            else:
                                newkb[litsplit] = [litst]
                    ##print("Query stack for rec -- ", qlist)
                    # for ql in qlist:
                    #     qlpartition = ql.split("(")
                    #     qlpred = qlpartition[0]
                    #     qlarglist = qlpartition[1][0:-1].split(",")
                    #     for qg in range(len(qlarglist)):
                    #         if qlarglist[qg] in submap.keys():
                    #             qlarglist[qg] = submap[qlarglist[qg]]
                    #     newqlarg = ",".join(qlarglist)
                    #     ql = alpred + "(" + newqlarg + ")"


                    result = resolve(qlist, iterations+1, newkb, simple, tempatvar)
                    if result:
                        return True

            return False
    return True


def unify(a,b):
    if len(a) != len(b):
        return False
    counter = 0
    for i in range(len(a)):
        x = a[i]
        y = b[i]
        if "a" <= x[0] <= "z" and "a" <= y[0] <= "z":
            counter +=1
        elif "A" <= x[0] <= "Z" and "a" <= y[0] <= "z":
            counter += 1
        elif "a" <= x[0] <= "z" and "A" <= y[0] <= "Z":
            counter += 1
        elif x == y:
            counter += 1

    if counter == len(a):
        return True
    else:
        return False

def main():
    output_file = "output.txt"
    fo = open(output_file, 'w')
    # query_list, sentencesinp = get_input()
    inputfile = open("input.txt", "r").readlines()
    queryNumber = int(inputfile[0].strip())
    query_list = []
    for qn in range(queryNumber):
        query_list.append(str(inputfile[1+qn]).strip())
    sentenceNumber = int(inputfile[queryNumber+1].strip())
    sentenceinp = []
    for sn in range(sentenceNumber):
        sentenceinp.append(str(inputfile[queryNumber+2+sn]).strip())
    sentences = convertKbtoCNF(sentenceinp)
    simple = []
    atvar = []
    #change from here
    std = standardize(sentences)
    # ##print("standardize -- ", std)
    for st in std:
        if simplesent(st) == True:
            simple.append(st)
            # std.remove(st)
        elif atomicwithvars(st) == True:
            atvar.append(st)
    dc = {}
    newdc = makingkb(atvar, dc)
    newnewdc = makingkb(simple, newdc)
    finaldc = makingkb(std, newnewdc)
    # ##print("\nKB -- ",finaldc)
    for ind,q in enumerate(query_list):
        # ##print(q, "\n")
        if q in std:
            ##print("Trueee")
            fo.write("TRUE")
            if ind < len(query_list) - 1:
                fo.write("\n")
            continue
        try:
            resolution(q,finaldc, simple, atvar, fo)

        except Exception as re:
            if 'maximum recursion depth' in re.args[0]:
                ##print("False max red")
                fo.write("FALSE")
            # elif 'Timed out!' in re.args[0]:
            #     ##print("False Time out")
            #     fo.write("False")

        if ind < len(query_list) - 1:
                fo.write("\n")
                

if __name__ == '__main__':
    main()