import math
from collections import defaultdict

import time

def main():
    
    Idx1 = open("Index1.txt", "r")
    Idx2 = open("Index2.txt", "r")
    Idx3 = open("Index3.txt", "r")
    LinksTxt = open("Links.txt", "r")
    Index = defaultdict(lambda: defaultdict(float))

    #cmf,559:0.0-580:0.0-
    query = input("Enter a query: ").lower()
    
    
    while query != "quit":
        start_time = time.time()
        queryList = query.split()
        for q in queryList:
            Idx1.seek(0)
            Idx2.seek(0)
            Idx3.seek(0)
            for line in Idx1:
                lit = line.strip("\n").split(",")
                if q == lit[0]:
                    postings = lit[1].split("/")[:-1]
                    for tup in postings:
                        Tsplit = tup.split(":")
                        Index[q][Tsplit[0]] = float(Tsplit[1])
            for line in Idx2:
                lit = line.strip("\n").split(",")
                if q == lit[0]:
                    postings = lit[1].split("/")[:-1]
                    for tup in postings:
                        Tsplit = tup.split(":")
                        Index[q][Tsplit[0]] = float(Tsplit[1])
            for line in Idx3:
                lit = line.strip("\n").split(",")
                if q == lit[0]:
                    postings = lit[1].split("/")[:-1]
                    for tup in postings:
                        Tsplit = tup.split(":")
                        Index[q][Tsplit[0]] = float(Tsplit[1])

        List_Postings = []
        links = []
        for line in LinksTxt:
            links.append(line)

        

        for q in queryList:
            #SortedIndex = sorted(Index[q].keys())
            Idf = math.log10(len(links) / len(Index[q].keys()))
            List_Postings.append(sorted(Index[q].keys(), key = lambda x: Index[q][x] * Idf,  reverse=True))

        
            
        
        smallPosting = min(List_Postings, key=len)
        for postID in smallPosting:
            for posting in List_Postings:
                if postID not in posting:
                    smallPosting.remove(postID)
        print("Top 5 results for", query, ":\n")
        for doc in set(smallPosting[:5]):
            print(links[int(doc)])
        print(time.time() - start_time)
        query = input("Enter a query: ").lower()
    

    Idx1.close()
    Idx2.close()
    Idx3.close()
    LinksTxt.close()
    

if __name__ == "__main__":
    main()