from collections import defaultdict
from nltk.stem import PorterStemmer
from tkinter import *
import heapq
import time
import math

def find_seek_pos(IndexofIndex, term, part_num):
    # returns the byte position to seek for term/token
    for tup in IndexofIndex[term]:
        if part_num == tup[0]:
            return int(tup[1])
    return -1

def searchIndexPart(Indexfile, Seek_position, query_term, posting):
    # returns a list posting for the term
    Indexfile.seek(Seek_position)
    line = Indexfile.readline().rstrip()
    line_split = line.split(",")
    if query_term == line_split[0]:
        term_data = line_split[1]
        for docid_tf in term_data.split(";"):  # 2060 | tf ; 3030 | tf 
            tup = docid_tf.split("|")
            if (len(tup) == 1):
                continue
            max_heap_tup = (-1*float(tup[1]), int(tup[0])) # (-TF, DOCID) 
            heapq.heappush(posting, max_heap_tup) # 0th index has max tf score


def Search(Idx1, Idx2, Idx3, links, IndexofIndex, links_len, ps, query, returnLabel):
    if query == "":
        return
    start_time = time.time()
    queryScore = defaultdict(float) # term -> normalized score
    documentScore = defaultdict(lambda: defaultdict(float)) # docid -> term -> tf
    queryList = query.split()
    q_count = defaultdict(int) # dictionary holding counts for each query term, reminder to count stemmed q terms

    # stem or dont stem
    
    for i in range(len(queryList)):
        if len(IndexofIndex[queryList[i]]) < len(IndexofIndex[ps.stem(queryList[i])]):
            queryList[i] = ps.stem(queryList[i])

    for q in queryList:
        # find all seek positions for each part for the query term
        Seek_position_part1 = find_seek_pos(IndexofIndex, q, "1") 
        Seek_position_part2 = find_seek_pos(IndexofIndex, q, "2") 
        Seek_position_part3 = find_seek_pos(IndexofIndex, q, "3") 
        
        # posting is posting for 1 term the q of queryList, combination of posting from 3 parts
        posting = []
        if (Seek_position_part1 != -1):
            searchIndexPart(Idx1, Seek_position_part1, q, posting)
            

        if (Seek_position_part2 != -1):
            searchIndexPart(Idx2, Seek_position_part2, q, posting)
            
        
        if (Seek_position_part3 != -1):
            searchIndexPart(Idx3, Seek_position_part3, q, posting)

        len_postings = len(posting)
        top_k_posting = []
        k = 0
        if len(posting) < 200:
            k = len(posting)
        else:
            k = 200
        for i in range(k):
            tf_id_tup = heapq.heappop(posting)
            tf_id_tup = (tf_id_tup[0]*-1, tf_id_tup[1])
            top_k_posting.append(tf_id_tup)

            docid = tf_id_tup[1]
            documentScore[docid][q] = tf_id_tup[0]
        
        if (len(top_k_posting) == 0):
            #print("There are no links with the query: ", q)
            # will need to fix this so that if we dont find lopes we can go to next closest thing
            continue
        
        # Fill in q_count
        for q_term in queryList:
            if q == q_term:
                q_count[q] += 1

        # calculate query term rank
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

    #cosine similarity score for each docid
    max_heap_cos = []

    n = len(queryList) # n is requirement of terms in docid for ex n = 4, means 4/4 terms must be in docid        
    while (len(max_heap_cos) <= 5 ):
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
            
            for q in queryScore:
                q_score = queryScore[q]/query_length
                d_score = documentScore[DocId][q]/doc_length
                cos_score = q_score*d_score
                eachDocId_score += cos_score
            heapq.heappush(max_heap_cos, (-eachDocId_score, DocId))

        n -= 1
        if (n <= 0):
            break
    

    # # for multi queries do we want to use the sum scores of each term in the docid, we do each docid at a time
    # intercept_posting = min(List_of_Postings, key=len)
    # final_posting = intercept_posting
    # for data_tup in intercept_posting:
    #     for posting in List_of_Postings:
    #         if data_tup not in posting:
    #             final_posting.remove(data_tup)
    #             break

    # 
    if (len(max_heap_cos)) == 0 and n <= 0:
        urls = "No matches found for query\n"
    else:
        
        n = 5 if len(max_heap_cos) >= 5 else len(max_heap_cos)
        urls = f"Top {n} results for " + query + " :\n"
        for i in range(n):
            tf_id = heapq.heappop(max_heap_cos)
            tf_id = (-tf_id[0], tf_id[1])
            urls += str(links[tf_id[1]]) + "\n"

    urls += "Time: " + str(time.time() - start_time)
    #print("Time: ", time.time() - start_time)
    returnLabel["bg"] = "lightgrey"
    returnLabel["text"] = urls
    return returnLabel
    
    # print(time.time() - start_time)

    
    

def Gui():
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

    links_len = 0
    with open("TotalLinks.txt", "r") as TotalL:
        links_len = int(TotalL.readline())

    # example term,2060|0.0033003300330033004;333|0.000333 
    ps = PorterStemmer()

    root = Tk()
    
    root.title("Search Engine")
    root.geometry('1200x400')
    root.config(bg="grey")
    root.resizable(1,1)

    Querylabel = Label(root, text='Query:', bg='lightgrey', font=('arial', 20,'bold'))
    EnterQuery = Entry(root, width=50, bd=4)

    returnLabel = Label(root, bg='grey', font=('arial', 10,'bold'))
    searchButton = Button(root,text="Search", bg='lightgrey', command=lambda :Search(Idx1, Idx2, Idx3, links, IndexofIndex, links_len, ps, EnterQuery.get().lower(), returnLabel))

    Querylabel.grid(row=0,column=0, sticky="NSEW")
    EnterQuery.grid(padx=10, row=0, column=1, sticky="NSEW")
    searchButton.grid(row=0, column=2, sticky="NSEW")
    returnLabel.grid(row=1, column=1, sticky="NSEW")
    root.grid_rowconfigure(0, weight=0)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(1, weight=1)
    
    root.mainloop()
    Idx1.close()
    Idx2.close()
    Idx3.close()
    LinksTxt.close()


if __name__ == "__main__":
    Gui()
    