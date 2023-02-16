import os
import time
import json
import re
from math import log10
from nltk.stem import PorterStemmer, WordNetLemmatizer
from collections import defaultdict

def indexer(link, Index, links, Tfs):
    ps = PorterStemmer()
    lm = WordNetLemmatizer()

    with open(link, "r") as jason:
        text = json.load(jason)
        tokens = re.findall("([a-zA-Z0-9]+)", text["content"])
        for word in set(tokens):
            word = lm.lemmatize(word)
            if not word.isascii():
                continue
            if not word.islower():
                word = word.lower()
            

            if text["url"] in links:
                lnkIdx = links.index(text["url"])
                if lnkIdx in Index[word]:
                    continue
                else:
                    Index[word].add(lnkIdx)
            else:
                Tf = tokens.count(word) / len(tokens)
                Tfs[text["url"]][word] = Tf

                links.append(text["url"])
                Index[word].add(len(links))


def main():
    Index = defaultdict(set)
    Tfs = defaultdict(defaultdict) #Tfs[url][word] = Tf
    Tf_IdF = defaultdict(int)
    links = []
    directory = "ANALYST"
    drList = os.listdir(directory)
    for dir in drList:
        linkList = os.listdir(directory + "/" + dir)
        for link in linkList:
            indexer(directory + "/" + dir + "/" + link, Index, links, Tfs)
    #print(Index.keys())

    #TF = num of times word appears in doc/ total number of terms in doc   
    #IDF = log(number of documents/number of documents that have the word)
    #tf-idf = TF * IDF
    for word in Index.keys():
        Idf = log10(len(links) / len(Index[word]))
        for urls in Index[word]:
            Tfs[urls][word] = Tfs[urls][word] * Idf

    
    with open("Index.txt", "w+") as Inverted:
        for word in Index:
            Inverted.write(word)
            Inverted.write(",")
            for idx in Index[word]:
                Inverted.write(str(idx))
                Inverted.write("-")
            Inverted.write("\n")
    with open("Links.txt", "w+") as linkList:
        for link in links:
            linkList.write(str(link))
            linkList.write("\n")
    print(len(links))
    print(len(Index))
            



if __name__ == "__main__":
    main()