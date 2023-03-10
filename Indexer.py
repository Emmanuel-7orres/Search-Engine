import os
import time
import json
import re
import math
from nltk.stem import PorterStemmer
from collections import defaultdict, Counter
from bs4 import BeautifulSoup
from urllib.parse import urldefrag



def writeIndextoFile(Index, part_num, IndexofIndex):
    # writes all the terms and docid + tf score to the 3 parts 
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
    
def parseTags(tag, soup, ps): 
    # returns a list of the tag tokens e.g tag = strong/bold/title
    tags = soup.find_all(tag)
    if len(tags) > 0:
        tag_string = ""
        for tag in tags:
            tag_string += ps.stem(tag.text)
        return re.findall("([a-zA-Z0-9]+)", tag_string)
    return []




# indexer function handles reading json files with parameters link, Index, links, Tfs
def indexer(ListLinks, Index, links, IndexofIndex, part_num):
    link_counter = 0
    # stemming
    ps = PorterStemmer()
    for link in ListLinks:
        with open(link, "r") as jason:
            # opening the json in the folder 
            # calling load to convert the json file into a dictionary 
            # tokens: a list of all all alphanumeric sequences in the dataset
            # called ps to stem each word in the list
            # covert each word in text to lower case characters
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
            # regular expression find possible terms in text
            tokens = re.findall("([a-zA-Z0-9]+)", soup.get_text())
            
            # Counter is a dictionary with terms as keys and values = term frequency
            tokens = Counter([ps.stem(i) for i in tokens]) 
            
            # strong_tokens is a list of all strong terms in the document   
            strong_tokens = parseTags("strong", soup, ps)
            
            # bold_tokens is a list of all bold terms in the document
            bold_tokens = parseTags("b", soup, ps)
            
            # header_tokens is a list of all headers 1 2 and 3 in the document
            header_tokens = parseTags(["h1", "h2", "h3"], soup, ps)

            # title_tokens is a list of all headers 1 2 and 3 in the document
            title_tokens = parseTags("title", soup, ps)
            
            for word in tokens:
                if not word.isascii():
                    continue

                first_letter = word[0]
                if first_letter not in Index:
                    # create empty list (posting) for the word & the first letter is to organize the dictionary
                    Index[first_letter][word] = []
                
                if defragged_url in links:
                    # if current url is in links then get the index from links data structure for docid
                    # Increment if needed for Tf score
                    linkIdx = links.index(defragged_url) + 1
                    word_count = tokens[word]
                    Tf =  1 + math.log10(word_count) 
                    if (word in bold_tokens):
                        Tf += 1
                    if (word in strong_tokens):
                        Tf += 1
                    if (word in title_tokens):
                        Tf += 2
                    if (word in header_tokens):
                        Tf += 2
                    
                    # adding the word and tf score to Index
                    Index[first_letter][word].append((linkIdx, Tf))
                else:
                    # Increment if needed for Tf score
                    word_count = tokens[word]
                    Tf =  1 + math.log10(word_count) 
                    if (word in bold_tokens):
                        Tf += 1
                    if (word in strong_tokens):
                        Tf += 1
                    if (word in title_tokens):
                        Tf += 2
                    if (word in header_tokens):
                        Tf += 2
            
                    # Also appending the current link into the list links
                    links.append(defragged_url)
                    # adding the word and tf score to Index
                    Index[first_letter][word].append((len(links), Tf))

        link_counter+=1

        # To track if we covered all the links given in function call, if true write to Indexfile for part #
        if link_counter == len(ListLinks):
            writeIndextoFile(Index, part_num, IndexofIndex)
            Index.clear()
            link_counter = 0


def main():
    start_time = time.time()
    Index = defaultdict(lambda: defaultdict(list))
    # Index contains first letter -> term -> posting (docid, term frequency)
    IndexofIndex = defaultdict(list)
    # IndexofIndex contains term -> [(part#, seekpos), ...]
    links = []
    # list of links
    directory = "DEV" 
    drList = os.listdir(directory)
    # list of all folders
    ListLinks = []
    # list of all json files from the folders
    
    # populating ListLinks
    for dir in drList:
        linkList = os.listdir(directory + "/" + dir)
        for link in linkList:
            ListLinks.append(directory + "/" + dir + "/" + link)

    # splitting the corpus into 3 parts and indexing each part into a file
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

    # writes total links indexed
    with open("TotalLinks.txt", "w+") as total:
        total.write(str(len(links)))

    print(time.time() - start_time)
            
if __name__ == "__main__":
    main()