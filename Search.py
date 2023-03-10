import math
from collections import defaultdict
from nltk.stem import PorterStemmer
import heapq
import time

def find_seek_pos(IndexofIndex, term, part_num):
    # returns the byte position to seek for term/token
    for tup in IndexofIndex[term]:
        if part_num == tup[0]:
            return int(tup[1])
    return -1

def searchIndexPart(Indexfile, Seek_position, query_term, posting):
    # populates posting which is a max heap with (tf score, docid)
    Indexfile.seek(Seek_position)
    line = Indexfile.readline().rstrip()
    line_split = line.split(",")
    if query_term == line_split[0]:
        term_data = line_split[1]
        for docid_tf in term_data.split(";"):  
            tup = docid_tf.split("|")
            if (len(tup) == 1):
                continue
            max_heap_tup = (-1*float(tup[1]), int(tup[0])) # (-TF, DOCID) 
            heapq.heappush(posting, max_heap_tup) # 0th index has max tf score

def Search():
    # opens all files
    Idx1 = open("IndexPart1.txt", "r")
    Idx2 = open("IndexPart2.txt", "r")
    Idx3 = open("IndexPart3.txt", "r")
    LinksTxt = open("Links.txt", "r")

    # Load all links into memory for fast access 
    links = [0]
    for line in LinksTxt:
        links.append(line)

    # Load Index of Indexes into memory for fast access
    IndexofIndex = defaultdict(list)
    with open("IndexofIndex.txt", "r+") as IndexSeek:
        for line in IndexSeek:
            line_split = line.strip().split()
            for i in range(1, len(line_split), 2):
                IndexofIndex[line_split[0]].append((line_split[i], line_split[i+1]))

    # links len = total number of links
    links_len = 0
    with open("TotalLinks.txt", "r") as TotalL:
        links_len = int(TotalL.readline())

    query = ""
    ps = PorterStemmer()
    
    while query != "quit":
        queryScore = defaultdict(float) # term -> tf_idf score
        documentScore = defaultdict(lambda: defaultdict(float)) # docid -> term -> tf
        query = input("Enter a query: ").lower() 
        start_time = time.time()
        # starts timer as soon as user enters query
        queryList = query.split() 
        q_count = defaultdict(int) # dictionary holding counts for each query term

        # stem or dont stem based on more data in index
        for i in range(len(queryList)):
            if len(IndexofIndex[queryList[i]]) < len(IndexofIndex[ps.stem(queryList[i])]):
                queryList[i] = ps.stem(queryList[i])
            
        for q in queryList:
            # find all seek positions for each part for the query term
            Seek_position_part1 = find_seek_pos(IndexofIndex, q, "1") 
            Seek_position_part2 = find_seek_pos(IndexofIndex, q, "2") 
            Seek_position_part3 = find_seek_pos(IndexofIndex, q, "3") 
            
            # posting is maxheap for top scoring docs for each q (term)
            posting = []
            if (Seek_position_part1 != -1):
                searchIndexPart(Idx1, Seek_position_part1, q, posting)

            if (Seek_position_part2 != -1):
                searchIndexPart(Idx2, Seek_position_part2, q, posting)
                
            if (Seek_position_part3 != -1):
                searchIndexPart(Idx3, Seek_position_part3, q, posting)

            len_postings = len(posting)
            # populates top_k_postings with the top 200 or len(posting) tf scores
            top_k_posting = []
            k = 0
            if len(posting) < 200:
                k = len(posting)
            else:
                k = 200
            for i in range(k):
                # tf_id_tup is largest tf score documentid for q(term)
                tf_id_tup = heapq.heappop(posting)
                tf_id_tup = (tf_id_tup[0]*-1, tf_id_tup[1])
                top_k_posting.append(tf_id_tup)
                docid = tf_id_tup[1]
                documentScore[docid][q] = tf_id_tup[0]
            
            if (len(top_k_posting) == 0):
                print("There are no links with the query: ", q)
                continue
            
            # Fill in q_count (frequency each q(term) shows up in query)
            for q_term in queryList:
                if q == q_term:
                    q_count[q] += 1

            # calculate query term rank tf*idf
            Idf = math.log10(links_len / len_postings) 
            Tf_q = q_count[q]
            Tf_idf = Tf_q * Idf
            queryScore[q] = Tf_idf

    
        # Get query length for normalization
        all_scores = queryScore.values()
        query_length = 0
        for score in all_scores:
            query_length += score*score
        query_length = math.sqrt(query_length)

        
        max_heap_cos = []
        # heap containing top documents for the query

        n = len(queryList) 
        # n is requirement of terms in docid for ex n = 4, means 4/4 terms must be in docid        

        # Vector space model ranked retrieval cos sim ...
        while (len(max_heap_cos) <= 5):
            for DocId in documentScore: # eachDocId is a dictionary with term -> tf
                eachDocId = documentScore[DocId]
                if len(eachDocId.keys()) != n:
                    continue
                # Get document length for normalization
                all_scores = eachDocId.values()

                if n != 1:
                    doc_length = 0
                    for score in all_scores:
                        doc_length += score*score
                    doc_length = math.sqrt(doc_length)
                else:
                    doc_length = 1
                
                
                eachDocId_score = 0
                #cosine similarity score for each docid
                
                for q in queryScore:
                    q_score = queryScore[q]/query_length
                    d_score = documentScore[DocId][q]/doc_length
                    cos_score = q_score*d_score
                    eachDocId_score += cos_score
                heapq.heappush(max_heap_cos, (-eachDocId_score, DocId))

            n -= 1    
            # decrease the required # of terms from query that must be in query -> jumps to if not enough ranked docs
            if n <= 0:
                break

        # prints information for user
        if (len(max_heap_cos)) == 0 and n == 0:
            print("no matches found for query")
        else:
            print("Top 5 results for", query + ":\n")
            n = 5 if len(max_heap_cos) >= 5 else len(max_heap_cos)
            for i in range(n):
                tf_id = heapq.heappop(max_heap_cos)
                tf_id = (-tf_id[0], tf_id[1])
                print(links[tf_id[1]])

            if n != 5:
                print(f"There are only {n} results based on the corpus")
        
        print(time.time() - start_time)

    # close all files
    Idx1.close()
    Idx2.close()
    Idx3.close()
    LinksTxt.close()
    
if __name__ == "__main__":
    Search()