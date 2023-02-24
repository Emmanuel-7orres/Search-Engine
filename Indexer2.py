import json
import os
import re
import time
from bs4 import BeautifulSoup
from collections import defaultdict
from nltk.stem import WordNetLemmatizer

def build_inverted_index(file_list):

    inverted_index = defaultdict(dict)  # Use defaultdict to automatically initialize missing terms
    #doc_lengths = defaultdict(int)  # Keep track of the length of each document
    Numinverted_index = defaultdict(dict)
    A_Iinverted_index = defaultdict(dict)
    J_Rinverted_index = defaultdict(dict)
    S_Zinverted_index = defaultdict(dict)
    lemmatizer = WordNetLemmatizer()
    for filename in file_list:
        with open(filename, "r") as f:
            data = json.load(f)
            #doc_lengths[data["url"]] = len(data["content"])
            #word_counts = defaultdict(int)  # Count the frequency of each word in the current document
            soup = BeautifulSoup(data["content"], 'lxml')
            tokens = re.findall("([a-zA-Z0-9]+)", soup.get_text().lower())
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
                if word[0] < "a":
                    Numinverted_index[word][data["url"]] = tf
                elif word[0] >= "a" and word[0] <= "i":
                    A_Iinverted_index[word][data["url"]] = tf
                elif word[0] > "i" and word[0] <= "r":
                    J_Rinverted_index[word][data["url"]] = tf
                elif word[0] > "r" and word[0] <= "z":
                    S_Zinverted_index[word][data["url"]] = tf
                #inverted_index[word][data["url"]] = tf # + weight
                # Sort the inverted index by term
    print("SORTING")
    Numsorted_index = sorted(Numinverted_index.items(), key=lambda x: x[0])
    A_Isorted_index = sorted(A_Iinverted_index.items(), key=lambda x: x[0])
    J_Rsorted_index = sorted(J_Rinverted_index.items(), key=lambda x: x[0])
    S_Zsorted_index = sorted(S_Zinverted_index.items(), key=lambda x: x[0])
    print("SORTED, WRITING TO FILE")
    # Idx = open('Index4.txt', 'w')
    Idx1 = open('Index1.txt', 'w')


    #0-i, j-r, s-z 
    for term in Numsorted_index:
        linkString = ""
        for link in term[1].keys():
            linkString += str(link) + " | " + str(term[1][link]) + "; "
        Idx1.write(term[0] + ", " + linkString + "\n")
    for term in A_Isorted_index:
        linkString = ""
        for link in term[1].keys():
            linkString += str(link) + " | " + str(term[1][link]) + "; "
        Idx1.write(term[0] + ", " + linkString + "\n")
    for term in J_Rsorted_index:
        linkString = ""
        for link in term[1].keys():
            linkString += str(link) + " | " + str(term[1][link]) + "; "
        Idx1.write(term[0] + ", " + linkString + "\n")
    for term in S_Zsorted_index:
        linkString = ""
        for link in term[1].keys():
            linkString += str(link) + " | " + str(term[1][link]) + "; "
        Idx1.write(term[0] + ", " + linkString + "\n")
        
    # for term in sorted_index:
    #     terms_file.write(str(term[0]) + '\n')
    # for link in doc_lengths.keys():
    #     links_file.write(link + '\n')
    # for word in inverted_index.values():
    #     tfidf_file.write(str(word.values()) + '\n')

    Idx1.close()
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