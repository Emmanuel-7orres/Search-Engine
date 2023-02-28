import os
import time
import json
import re
import math
from nltk.stem import WordNetLemmatizer
from collections import defaultdict
from bs4 import BeautifulSoup

def writeIndextoFile(Index, part_num):
    #create file index for 0-9
    with open("IndexSeek.txt", "a+") as Seek:


        with open("IndexPart" + str(part_num) + ".txt", "w+") as Part:
            
            for i in range(10):
                # writes seek position for each number into index of index file IndexSeek
                current_position = Part.tell()
                Seek.write("Part" + str(part_num) + " " + str(i) + " " + str(current_position) + "\n")
                for term in Index[str(i)].keys():
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
                # writes seek position for each character into index of index file IndexSeek
                current_position = Part.tell()
                Seek.write("Part" + str(part_num) + " " + letter + " " + str(current_position) + "\n")

                for term in Index[letter].keys():
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
                # writes seek position for each character into index of index file IndexSeek
                current_position = Part.tell()
                Seek.write("Part" + str(part_num) + " " + letter + " " + str(current_position) + "\n")
                for term in Index[letter].keys():
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
                # writes seek position for each character into index of index file IndexSeek
                current_position = Part.tell()
                Seek.write("Part" + str(part_num) + " " + letter + " " + str(current_position) + "\n")
                for term in Index[letter].keys():
                    termstring = term + ","
                    for tup in Index[chr(i)][term]:
                        termstring += str(tup[0])
                        termstring += "|"
                        termstring += str(tup[1])
                        termstring += ";"
                    Part.write(termstring)
                    Part.write("\n")
    

# indexer function handles reading json files with parameters link, Index, links, Tfs
def indexer(ListLinks, Index, links):
    counter = 0
    part_counter = 1
    link_counter = 0
    for link in ListLinks:
        
        # Lemmatizer object to stem unnecessary words 
        lm = WordNetLemmatizer()
        with open(link, "r") as jason:
            
            # opening the json in the folder 
            # calling load to convert the json file into a dictionary 
            # tokens: a list of all all alphanumeric sequences in the dataset
            # called lemmatize to stem each word in the list
            # checked if each word is ascii and covert each word to lower case characters
            text = json.load(jason)

            soup = BeautifulSoup(text["content"].lower(), 'lxml')
            tokens = re.findall("([a-zA-Z0-9]+)", soup.get_text())
            
            strong = soup.findAll('strong')
            strong_tokens = []
            # strong_tokens is a list of all strong terms in the document   
            if len(strong) > 0:
                strong_string = ""
                for s in strong:
                    strong_string += str(s.text)
                strong_tokens = re.findall("([a-zA-Z0-9]+)", strong_string)  
                             

            bolding = soup.findAll('b')
            bold_tokens = []
            # bold_tokens is a list of all bold terms in the document
            if len(bolding) > 0:
                boldstring = ""
                for bold in bolding:
                    boldstring += str(bold.text)
                bold_tokens = re.findall("([a-zA-Z0-9]+)", boldstring)

            headers = soup.find_all(re.compile('^h[1-3]$'))
            header_tokens = []
            # header_tokens is a list of all headers 1 2 and 3 in the document
            if len(headers) > 0:
                headers_string = ""
                for head in headers:
                    headers_string += str(head.text)
                header_tokens = re.findall("([a-zA-Z0-9]+)", headers_string)

            titles = soup.findAll('title')
            title_tokens = []
            # title_tokens is a list of all headers 1 2 and 3 in the document
            if len(titles) > 0:
                title_string = ""
                for title in titles:
                    title_string += str(title.text)
                title_tokens = re.findall("([a-zA-Z0-9]+)", title_string)

            
            for word in set(tokens):
                
                word = lm.lemmatize(word)
                
                if not word.isascii():
                    continue

                first_letter = word[0]
                if first_letter not in Index:
                    Index[first_letter][word] = []
                
                if text["url"] in links:
                    # if current url is in the list links and the index of current link is also the set of integers,
                    # we move on to the next iteration, otherwise we add the index of the url to the set of that word
                    linkIdx = links.index(text["url"]) + 1

                    Tf = 1 + (math.log10(tokens.count(word)) if tokens.count(word) != 0 else 0)
                    if (word in bold_tokens):
                        Tf += 1
                    if (word in strong_tokens):
                        Tf += 1
                    if (word in title_tokens):
                        Tf += 2
                    if (word in header_tokens):
                        Tf += 2
                    

                    Index[first_letter][word].append((linkIdx, Tf))
                    counter+=1
                else:
                    # if current url is not in list links, then we divide the number of times word appears in doc/ total number of terms in doc to get the TF value
                    Tf = 1 + (math.log10(tokens.count(word)) if tokens.count(word) != 0 else 0)
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
                    links.append(text["url"])
                    
                    # Reminder docid 1 is referring to line 1 in linkstxt
                    Index[first_letter][word].append((len(links), Tf))
                    counter+=1

        link_counter+=1
        #print(counter)

        if link_counter > math.ceil(len(ListLinks)/3):
            writeIndextoFile(Index, part_counter)
            Index.clear()
            part_counter += 1
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
    
    #Creating faster access time through multiple dictionary indexes containing a-z 0-9
    

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
            #indexer(directory + "/" + dir + "/" + link, Index, links)
            ListLinks.append(directory + "/" + dir + "/" + link)

    
    indexer(ListLinks, Index, links)

    writeIndextoFile(Index, 3)

    # opens the Links.txt and writes each url 
    with open("Links.txt", "w+") as linkList:
        link_counter = 1
        for link in links:
            if link_counter % 100 == 0:
                with open("LinksSeek.txt", "a+") as Seek:
                    Seek.write(str(link_counter) + ":" + str(linkList.tell()) + "\n")
            linkList.write(str(link))
            linkList.write("\n")
            link_counter += 1


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