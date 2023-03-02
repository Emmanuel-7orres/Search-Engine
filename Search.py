import math
from collections import defaultdict

import time

def find_seek_pos(IndexSeek, letter, part_num):
    # returns the byte position to seek for start_range and Idx Part number
    IndexSeek.seek(0)
    for line in IndexSeek:
        
        if (part_num == line[4] and letter == line[6]): # Part# 4th index rep num  
            return int(line.split(" ")[2])

def letter_range(first_letter_q):
    first_letter_q = ord(first_letter_q)
    if (first_letter_q < 10):
        return "nums"
    if (first_letter_q <= 105):
        return "atoi"
    if (first_letter_q <= 114):
        return "jtor"
    if (first_letter_q <= 122):
        return "stoz"

def searchIndexPart(Indexfile, Seek_position, query_term):
    # returns a list posting for the term
    postings = []
    Indexfile.seek(Seek_position)
    for line in Indexfile:
        line_split = line.split(",")
        if query_term == line_split[0]:
            term_data = line_split[1]
            for docid_tf in term_data.strip().split(";"):  # 2060 | tf ; 3030 | tf 
                tup = docid_tf.split("|")
                if (len(tup) == 1):
                    continue
                postings.append((tup[0], tup[1]))
    return postings


def Search():
    Idx1 = open("IndexPart1.txt", "r")
    Idx2 = open("IndexPart2.txt", "r")
    Idx3 = open("IndexPart3.txt", "r")
    LinksTxt = open("Links.txt", "r")
    LinksSeek = open("LinksSeek.txt", "r")
    IndexSeek = open("indexSeek.txt", "r")

    #term wit

    links = [0]
    for line in LinksTxt:
        links.append(line)

    # example term,2060|0.0033003300330033004;333|0.000333 
    query = ""
    
    while query != "quit":
        query = input("Enter a query: ").lower()
        start_time = time.time()
        queryList = query.split()
        List_of_Postings = []
        for q in queryList:
            postings = []
            first_letter_q = q[0]
            # determine whether first letter is 0-9 a-z
            # find all seek positions for each part for the starting range
            Seek_position_part1 = find_seek_pos(IndexSeek, first_letter_q, "1") 
            Seek_position_part2 = find_seek_pos(IndexSeek, first_letter_q, "2") 
            Seek_position_part3 = find_seek_pos(IndexSeek, first_letter_q, "3") 
            
            # posting is posting for 1 term the q of queryList, combination of posting from 3 parts
            posting = []
            posting1 = searchIndexPart(Idx1, Seek_position_part1, q)
            posting += posting1
            postings2 = searchIndexPart(Idx2, Seek_position_part2, q)
            posting += postings2
            postings3 = searchIndexPart(Idx3, Seek_position_part3, q)
            posting += postings3

            links_len = 0
            with open("TotalLinks.txt", "r") as TotalL:
                links_len = int(TotalL.readline())
            
            if (len(posting) == 0):
                print("There are no links with the query: ", q)
                # will need to fix this so that if we dont find lopes we can go to next closest thing
                continue
            
            Idf = math.log10(links_len / len(posting))
            
            # can do this later to optimize, when doing interception you want the docid to be sorted in order so that the intercep is faster
            List_of_Postings.append(sorted(posting, key=lambda x: float(x[1]) * Idf, reverse=True))

        if (len(List_of_Postings)) == 0:
            print("no matches found for query")
            continue

        # for multi queries do we want to use the sum scores of each term in the docid, we do each docid at a time
        intercept_posting = min(List_of_Postings, key=len)
        final_posting = intercept_posting
        for data_tup in intercept_posting:
            for posting in List_of_Postings:
                if data_tup not in posting:
                    final_posting.remove(data_tup)
                    break


        

        print("Top 5 results for", query, ":\n")
        for tup in final_posting[:5]:
            docID = tup[0]
            print(links[int(docID)])

        
        print(time.time() - start_time)
        
        



    Idx1.close()
    Idx2.close()
    Idx3.close()
    LinksSeek.close()
    IndexSeek.close()
    LinksTxt.close()
    

if __name__ == "__main__":
    Search()