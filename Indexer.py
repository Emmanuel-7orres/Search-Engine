import os
import time
import json
import re
import math
from nltk.stem import WordNetLemmatizer
from collections import defaultdict, Counter
from bs4 import BeautifulSoup
from urllib.parse import urldefrag



def writeIndextoFile(Index, part_num, IndexofIndex):

    with open("IndexPart" + str(part_num) + ".txt", "w+") as Part:
        
        for i in range(10):
            for term in Index[str(i)].keys():
                # adds seek position to Index of Index for each term
                current_position = Part.tell()
                IndexofIndex[term].append((part_num, current_position))

                termstring = term + ","
                for tup in Index[str(i)][term]:
                    termstring += str(tup[0])
                    termstring += "|"
                    termstring += str(tup[1])
                    termstring += ";"
                Part.write(termstring)
                Part.write("\n")

        
        for i in range(97, 106, 1):
            letter = chr(i)

            for term in Index[letter].keys():
                # adds seek position to Index of Index for each term
                current_position = Part.tell()
                IndexofIndex[term].append((part_num, current_position))

                termstring = term + ","
                for tup in Index[chr(i)][term]:
                    termstring += str(tup[0])
                    termstring += "|"
                    termstring += str(tup[1])
                    termstring += ";"
                Part.write(termstring)
                Part.write("\n")

        for i in range(106, 115, 1):
            letter = chr(i)
            for term in Index[letter].keys():
                # adds seek position to Index of Index for each term
                current_position = Part.tell()
                IndexofIndex[term].append((part_num, current_position))

                termstring = term + ","
                for tup in Index[chr(i)][term]:
                    termstring += str(tup[0])
                    termstring += "|"
                    termstring += str(tup[1])
                    termstring += ";"
                Part.write(termstring)
                Part.write("\n")

        for i in range(115, 123, 1):
            letter = chr(i)
            for term in Index[letter].keys():
                # adds seek position to Index of Index for each term
                current_position = Part.tell()
                IndexofIndex[term].append((part_num, current_position))

                termstring = term + ","
                for tup in Index[chr(i)][term]:
                    termstring += str(tup[0])
                    termstring += "|"
                    termstring += str(tup[1])
                    termstring += ";"
                Part.write(termstring)
                Part.write("\n")
    
def parseTags(tag, soup, lm): 
    # returns a list of the tag tokens e.g tag = strong/bold/title
    
    tags = soup.find_all(tag)
    if len(tags) > 0:
        tag_string = ""
        for tag in tags:
            tag_string += lm.lemmatize(tag.text)
        return re.findall("([a-zA-Z0-9]+)", tag_string)
    return []




# indexer function handles reading json files with parameters link, Index, links, Tfs
def indexer(ListLinks, Index, links, IndexofIndex, part_num):
    link_counter = 0
    # Lemmatizer object to stem unnecessary words 
    lm = WordNetLemmatizer()
    for link in ListLinks:
        with open(link, "r") as jason:
            #print(link)
            # opening the json in the folder 
            # calling load to convert the json file into a dictionary 
            # tokens: a list of all all alphanumeric sequences in the dataset
            # called lemmatize to stem each word in the list
            # checked if each word is ascii and covert each word to lower case characters
            text = json.load(jason)

            # checking if the defragged url has already been visited
            defragged_url = urldefrag(text["url"])[0]

            if (defragged_url in links):
                link_counter+=1

                if link_counter == len(ListLinks):
                    writeIndextoFile(Index, part_num, IndexofIndex)
                    Index.clear()
                    link_counter = 0
                continue

            soup = BeautifulSoup(text["content"].lower(), 'lxml')
            tokens = re.findall("([a-zA-Z0-9]+)", soup.get_text())
            
            tokens = Counter([lm.lemmatize(i) for i in tokens]) 
            
            # strong_tokens is a list of all strong terms in the document   
            strong_tokens = parseTags("strong", soup, lm)

            
            # bold_tokens is a list of all bold terms in the document
            bold_tokens = parseTags("b", soup, lm)
            

            # header_tokens is a list of all headers 1 2 and 3 in the document
            header_tokens = parseTags(["h1", "h2", "h3"], soup, lm)
            

            # title_tokens is a list of all headers 1 2 and 3 in the document
            title_tokens = parseTags("title", soup, lm)
            
            for word in tokens:
                
                if not word.isascii():
                    continue

                first_letter = word[0]
                if first_letter not in Index:
                    Index[first_letter][word] = []
                
                if defragged_url in links:
                    # if current url is in the list links and the index of current link is also the set of integers,
                    # we move on to the next iteration, otherwise we add the index of the url to the set of that word
                    linkIdx = links.index(defragged_url) + 1
                    word_count = tokens[word]
                    Tf = 1 + (math.log10(word_count) if word_count != 0 else 0)
                    if (word in bold_tokens):
                        Tf += 1
                    if (word in strong_tokens):
                        Tf += 1
                    if (word in title_tokens):
                        Tf += 2
                    if (word in header_tokens):
                        Tf += 2
                    

                    Index[first_letter][word].append((linkIdx, Tf))
                else:
                    # if current url is not in list links, then we divide the number of times word appears in doc/ total number of terms in doc to get the TF value
                    word_count = tokens[word]
                    Tf = 1 + (math.log10(word_count) if word_count != 0 else 0)
                    if (word in bold_tokens):
                        Tf += 1
                    if (word in strong_tokens):
                        Tf += 1
                    if (word in title_tokens):
                        Tf += 2
                    if (word in header_tokens):
                        Tf += 2
            
                    # Also appending the current link into the list links
                    # Adding the word in the dictionary and adding the docId with Term frequency
                    links.append(defragged_url)
                    
                    # Reminder docid 1 is referring to line 1 in linkstxt
                    Index[first_letter][word].append((len(links), Tf))

        link_counter+=1

        if link_counter == len(ListLinks):
            writeIndextoFile(Index, part_num, IndexofIndex)
            Index.clear()
            link_counter = 0


def main():
    # Definition of link, Index, links, Tfs, directory
    # link: the directory of the folder of folder of json files
    # Index: a defaultdict with keys of terms and values of docId and Term Frequency
    # links: a list of all the urls we have visited
    # directory: the name of the directory folder
    # drList: grabbing all the folders within that directory
    start_time = time.time()
    Index = defaultdict(lambda: defaultdict(list))
    
    IndexofIndex = defaultdict(list)
    

    links = []
    directory = "ANALYST" 
    drList = os.listdir(directory)
    ListLinks = []
    
    # Looping through the list of folder from the directory
    # call os.listdir to open those folders to get the json files
    # looping through the json files and calling indexer function above
    for dir in drList:
        linkList = os.listdir(directory + "/" + dir)
        for link in linkList:
            ListLinks.append(directory + "/" + dir + "/" + link)

    part1 = ListLinks[0:math.ceil(len(ListLinks)/3)]
    part2 = ListLinks[math.ceil(len(ListLinks)/3): 2*math.ceil(len(ListLinks)/3)]
    part3 = ListLinks[2*math.ceil(len(ListLinks)/3):]
    indexer(part1, Index, links, IndexofIndex, 1)
    indexer(part2, Index, links, IndexofIndex, 2)
    indexer(part3, Index, links, IndexofIndex, 3)

    # write seek positions for each term into a file IndexofIndex
    with open("IndexofIndex.txt", "w+") as seek:
        for term, seek_list in IndexofIndex.items():
            write_string = ""
            write_string += term
            for each_seek in seek_list:
                write_string += " "
                write_string += str(each_seek[0])
                write_string += " "
                write_string += str(each_seek[1])
            write_string += "\n"
            seek.write(write_string)

    # opens the Links.txt and writes each url 
    with open("Links.txt", "w+") as linkList:
        for link in links:
            linkList.write(str(link))
            linkList.write("\n")


    with open("TotalLinks.txt", "w+") as total:
        total.write(str(len(links)))

    # TF = num of times word appears in doc/ total number of terms in doc   
    # IDF = log(number of documents/number of documents that have the word)
    # tf-idf = TF * IDF
    # Loops thorugh the TF dictionary and calculates the idf value 
    # then multiples the tf value after calling indexer with the idf we calculate 
    # for word in Index.keys():
    #     Idf = log10(len(links) / len(Index[word]))
    #     for urls in Index[word]:
    #         Tfs[urls][word] = Tfs[urls][word] * Idf



    # prints the number of unique links
    # prints the total number of words
    # print(len(links))
    # print(len(Index))
    print(time.time() - start_time)
            



if __name__ == "__main__":
    main()