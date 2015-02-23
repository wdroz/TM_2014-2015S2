# coding=utf-8
from TwitterSearch import *
def mysend(msg, sock):
    totalsent = 0
    print('SEND : %s' % msg)
    msg += '\n'
    while totalsent < len(msg):
        sent = sock.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent

def twitterStreaming():
    import socket
    from time import sleep
    try:
        s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)    
        try:
            s.connect(('localhost', 9999))
        except:
            print('error connection socket')
        # it's about time to create a TwitterSearch object with our secret tokens
        tso = TwitterSearchOrder() # create a TwitterSearchOrder object
        tso.set_keywords(['Swissquote']) # let's define all words we would like to have a look for
        tso.set_language('en') # we want to see German tweets only
        tso.set_include_entities(False) # and don't give us all those entity information
        lastID = 569803155141206016
        while(True):
            sleep(5.0) # 5 sec
            tso.set_since_id(lastID)        
            ts = TwitterSearch(
                consumer_key = '7rHng44nAkVvyPvxtYnVQvmjL',
                consumer_secret = 'pGL4s4T1OTkScLOsaXjynhYF8SYXbeZgu5wgcpIkJ317rMHEDl',
                access_token = '3055341988-VQXPgcjt40sje3mUghB1rB4AjAiO0TiIRKbXRV9',
                access_token_secret = 'B9RI43VILWhfYu0XNv5HrRmmrFmuOE1KFGa2hwLRFtMXO'
            )
            for tweet in ts.search_tweets_iterable(tso):
                print( '[%s]@%s tweeted: %s' % ( tweet['created_at'], tweet['user']['screen_name'], tweet['text'] ) )
                if(lastID < tweet['id']):
                    lastID = tweet['id']
                    mysend(tweet['text'], s)
    except TwitterSearchException as e: # take care of all those ugly errors if there are some
        print(e)

def sparkTask():
    from textblob import TextBlob
    import re    
    from pyspark import SparkContext
    from pyspark.streaming import StreamingContext
    sc = SparkContext()
    ssc = StreamingContext(sc, 1)
    quotes = ssc.socketTextStream("localhost", 9999)
    dataSentencesPolarity = quotes.map(lambda x: TextBlob(re.sub('[^A-Za-z0-9 \.\']+', '',x))).map(lambda y: (str(y.upper())[:60], y.sentiment.polarity))
    dataSentencesPolarity.pprint()
    ssc.start()             # Start the computation
    ssc.awaitTermination(25)  # Wait for the computation to terminate    
        
if __name__ == '__main__':
    import threading
    from threading import Timer
    t1 = threading.Thread(target=twitterStreaming)
    t1 = Timer(10, twitterStreaming)
    t2 = threading.Thread(target=sparkTask)    
    t2.start()
    t1.start()
    t2.join()
    quit()