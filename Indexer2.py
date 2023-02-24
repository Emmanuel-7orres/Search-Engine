import json
import os
import re
import time
from collections import defaultdict
from nltk.stem import WordNetLemmatizer

def build_inverted_index(file_list):

    inverted_index = defaultdict(dict)  # Use defaultdict to automatically initialize missing terms
    #doc_lengths = defaultdict(int)  # Keep track of the length of each document
    lemmatizer = WordNetLemmatizer()
    for filename in file_list:
        with open(filename, "r") as f:
            data = json.load(f)
            #doc_lengths[data["url"]] = len(data["content"])
            #word_counts = defaultdict(int)  # Count the frequency of each word in the current document
            tokens = re.findall("([a-zA-Z0-9]+)", data["content"].lower())

            for word in set(tokens):
                # Lemmatize the word using the WordNetLemmatizer
                if not word.isascii():
                    continue
                word = lemmatizer.lemmatize(word)
                # if '<b>' in text or '<h' in text or '<title>' in text:
                #     # Assign higher weights to words in bold, headings, and titles
                #     weight = 2
                # else:
                #     weight = 1
                tf = tokens.count(word) / len(tokens)
                inverted_index[word][data["url"]] = tf # + weight
                # Sort the inverted index by term
    sorted_index = sorted(inverted_index.items(), key=lambda x: x[0])
    # Idx = open('Index4.txt', 'w')
    Idx1 = open('Index1.txt', 'w')
    Idx2 = open('Index12.txt', 'w')
    Idx3 = open('Index13.txt', 'w')
    

    #0-i, j-r, s-z 
    for term in sorted_index:
        linkString = ""
        for link in term[1].keys():
            linkString += str(link) + " | " + str(term[1][link]) + "; "

        if term[0][0] <= "i":
            Idx1.write(term[0] + ", " + linkString + "\n")
        elif term[0][0] > "i" and term[0][0] <= "r":
            Idx2.write(term[0] + ", " + linkString + "\n")
        elif term[0][0] > "r" and term[0][0] <= "z":
            Idx3.write(term[0] + ", " + linkString + "\n")
        

    # for term in sorted_index:
    #     terms_file.write(str(term[0]) + '\n')
    # for link in doc_lengths.keys():
    #     links_file.write(link + '\n')
    # for word in inverted_index.values():
    #     tfidf_file.write(str(word.values()) + '\n')

    Idx1.close()
    Idx2.close()
    Idx3.close()
    # Idx.close()
    
    return inverted_index

def main():
    start_time = time.time()
    linkList = []
    Links = []
    drList = os.listdir("DEV")
    for dir in drList:
        linkList += [["DEV" + "/" + dir + "/" , os.listdir("DEV" + "/" + dir)]]
    for link in linkList:
        for jason in link[1]:
            Links.append(link[0] + jason)
    #print(Links)
    build_inverted_index(Links)
    print(time.time() - start_time)
    #print(inverted_index)

if __name__ == "__main__":
    main()