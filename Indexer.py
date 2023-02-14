import os
import time
import json
import re
from nltk.stem import PorterStemmer
from collections import defaultdict

def indexer(link, Index):
    ps = PorterStemmer()
    with open(link, "r") as jason:
        text = json.load(jason)

        for word in re.findall("([a-zA-Z0-9]+)", text["content"]):
            if not word.isascii():
                raise Exception("Bad input")
            if not word.islower():
                word = word.lower()
            
            Index[ps.stem(word)].add(text["url"])
        



def main():
    Index = defaultdict(set)
    directory = "ANALYST"
    drList = os.listdir(directory)
    for dir in drList:
        linkList = os.listdir(directory + "/" + dir)
        for link in linkList:
            indexer(directory + "/" + dir + "/" + link, Index)
    print(Index)
            



if __name__ == "__main__":
    main()