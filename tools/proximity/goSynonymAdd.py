########## parses a result from the goQuery.py and appends results and syns to data

import json
import pandas as pd 
import explodeJSON as ej
from itertools import chain
import re


dbase = "data/lysis-family.json" # generated from generateLysisFamily.py
go_file = "go-synonym-results-JRR.txt" # cleared up results from JRR

### Using ej to parse json
db = ej.explodeJSON(dbase)
db = db.readJSON()

### Using pandas to peek into txt file
cols = ["query_term", "GO:id", "GO:name", "description", "restriction", "synonyms"]
go = pd.read_csv(go_file, names=cols, sep="\t")
go_syns = go[["query_term","GO:name","synonyms"]] # subset of what I want from the datafile

def parse_pipes(piped_data): 
    """ 
    Extracts synonyms, and separates them, based on the pipe delimiter used from goQuery.py
    """
    pipe = piped_data.split("|")
    return pipe

def remove_fat(term): 
    """
    removes extra fluff of terms, such as regulation, etc... 
    Do this within a loop to suck all the fat out of terms/synonyms
    """
    s = term
    if re.search(("regulation"), s):
        s = s.split("regulation of")[1]
        s = s.strip()
    else:
        pass
    if re.search(("activity"), s):
        s = s.split(" activity")[0]
        s = s.strip()
    else:
        pass
    if re.search(("inhibition of"), s):
        s = s.split("inhibition of")[1]
        s = s.strip()
    else:
        pass

    return s

def readFrameVals(frame=go_syns): # PASS
    """
    reads the go_syns frame, and grabs the information we want from it, which is the mapping query term; name of GO term; and synonyms
    """
    link = frame["query_term"].tolist()
    go = frame["GO:name"].tolist()
    syn = frame["synonyms"].tolist()
    return link, go, syn, zip(link,go,syn)

def form_dict(link, go, syn): # PASS
    """
    format a dictionary that will stack all matching query terms (eventually mapped back to json); remove duplicate / redundant names and synonyms
    """
    sync = {}
    for i, name in enumerate(link):
        try:
            if sync[name] != []:
                sync[name].append(remove_fat(go[i]))
                pipes = parse_pipes(syn[i])
                for p in pipes:
                    p = remove_fat(p)
                    sync[name].append(p)
        except KeyError:
            sync[name] = []
            sync[name].append(remove_fat(go[i]))
            pipes = parse_pipes(syn[i])
            for p in pipes:
                p = remove_fat(p)
                sync[name].append(p)
    # Removing Duplicates
    unq = {}
    for k, v in sync.items():
        unq[k] = list(set(v))
        # Removing "None" and "NoneAtAll", this should be the last cleaning needed
        is_not = lambda x: x is not "None" or "NoneAtAll" # not working as expected, moved to later step. likely needs copy of list.
        unq[k] = list(filter(is_not, unq[k]))

    return unq

def match_and_store(input_data, db=db):
    """ return JSON object that has go-synonyms added ; input will be return of form_dict function """
    new_db = {}
    for mapper, synonyms in input_data.items():
        for family_term, list_of_syns in db.items():
            for pair_map in list_of_syns:
                if pair_map == mapper:
                    if family_term in new_db:
                        new_db[family_term].extend(synonyms)
                    else:
                        new_db[family_term] = synonyms
                else:
                    continue
    removes = ["None", "NoneAtAll","suppression by virus of host cell lysis in response to superinfection","suppression by virus of host cell lysis in response to superinfecting virus"]
    for each_list in new_db.values():
        for element in each_list[:]:
            if element == removes[0] or element == removes[1] or element == removes[2] or element == removes[3]:
                each_list.remove(element)
            else:
                continue

    return new_db

def merge_go(go_dbase, lysis_dbase):
    """ match_and_store will have returned a dictionary that can then be fed into this file to merge the datasets, and remove duplicates. Results in the final dbase """
    combined = {}
    for dictionary in [go_dbase, lysis_dbase]:
        for keys, terms in dictionary.items():
            if keys in combined.keys():
                combined[keys].extend(terms)
            else:
                combined[keys] = terms
    return combined

    

if __name__ == "__main__":
    link, go, syn, zipped = readFrameVals()
    u = form_dict(link=link,go=go,syn=syn)

    complete = match_and_store(input_data=u, db=db)
    merged = merge_go(go_dbase=complete,lysis_dbase=db)

    # SAVE AS JSON
    filename = "lysis-family-expanded.json"
    with open("data/" + filename, "w") as j:
        json.dump(merged, j, indent="\t")
