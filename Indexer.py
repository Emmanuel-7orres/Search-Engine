import os
import time
import json
import re
from math import log10
from nltk.stem import WordNetLemmatizer
from collections import defaultdict

# indexer function handles reading json files with parameters link, Index, links, Tfs
def indexer(link, Index, links, Tfs):
    # Lemmatizer object to stem unnecessary words 
    lm = WordNetLemmatizer()
    with open(link, "r") as jason:
        # opening the json in the folder 
        # calling load to convert the json file into a dictionary 
        # tokens: a list of all all alphanumeric sequences in the dataset
        # called lemmatize to stem each word in the list
        # checked if each word is ascii and covert each word to lower case characters
        text = json.load(jason)
        tokens = re.findall("([a-zA-Z0-9]+)", text["content"])
        for word in set(tokens):
            word = lm.lemmatize(word)
            if not word.isascii():
                continue
            if not word.islower():
                word = word.lower()
            
            
            if text["url"] in links:
                # if current url is in the list links and the index of current link is also the set of integers,
                # we move on to the next iteration, otherwise we add the index of the url to the set of that word
                lnkIdx = links.index(text["url"])
                if lnkIdx in Index[word]:
                    continue
                else:
                    Index[word].add(lnkIdx)
            else:
                # if current url is not in list links, then we divide the number of times word appears in doc/ total number of terms in doc to get the TF value
                # then we add the current word with the current word with the TF value
                Tf = tokens.count(word) / len(tokens)
                Tfs[text["url"]][word] = Tf
                # Also appending the current link into the list links
                # Adding the word in the dictionary and adding to the set with integer index of the url from list links
                links.append(text["url"])
                Index[word].add(len(links))


def main():
    # Definition of link, Index, links, Tfs, directory
    # link: the directory of the folder of folder of json files
    # Index: a defaultdict with keys of strings and values of a set of integers 
    # links: a list of all the urls we have visited
    # Tfs: a defaultdict of defaultdict of int to store url and words in that url and the TF value
    # directory: the name of the directory folder
    # drList: grabbing all the folders within that directory
    start_time = time.time()
    Index = defaultdict(set)
    Tfs = defaultdict(lambda: defaultdict(int)) #Tfs[url][word] = Tf
    links = []
    directory = "DEV" #ANALYST
    drList = os.listdir(directory)

    # Looping through the list of folder from the directory
    # calling os.listdir to open those folders to get the json files
    # looping through the json files and calling indexer function above
    for dir in drList:
        linkList = os.listdir(directory + "/" + dir)
        for link in linkList:
            indexer(directory + "/" + dir + "/" + link, Index, links, Tfs)

    # TF = num of times word appears in doc/ total number of terms in doc   
    # IDF = log(number of documents/number of documents that have the word)
    # tf-idf = TF * IDF
    # Loops thorugh the TF dictionary and calculates the idf value 
    # then multiples the tf value after calling indexer with the idf we calculate 
    for word in Index.keys():
        Idf = log10(len(links) / len(Index[word]))
        for urls in Index[word]:
            Tfs[urls][word] = Tfs[urls][word] * Idf

    # opens the Index.txt and writes each word and the set of indexs
    with open("Index.txt", "w+") as Inverted:
        for word in Index:
            Inverted.write(word)
            Inverted.write(",")
            for idx in Index[word]:
                Inverted.write(str(idx))
                Inverted.write("-")
            Inverted.write("\n")
            
    # opens the Links.txt and writes each url 
    with open("Links.txt", "w+") as linkList:
        for link in links:
            linkList.write(str(link))
            linkList.write("\n")

    # prints the number of unique links
    # prints the total number of words
    print(len(links))
    print(len(Index))
    print(time.time() - start_time)
            



if __name__ == "__main__":
    main()