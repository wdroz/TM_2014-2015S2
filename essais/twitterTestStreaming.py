# coding=utf-8
from TwitterSearch import *
import socket
from threading import Thread

class StreamingManager(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('localhost', 9999))
        self.start()
        self.isConnectionAlive = True
        self.listClient = []
        
    def run(self):
        self.sock.listen(5)
        self.isConnectionAlive = True
        while self.isConnectionAlive:
            try:
                clientsocket, address = self.sock.accept()
                self.listClient.append(clientsocket)
            except Exception as e:
                print('quit %s' % str(e))
                self.isConnectionAlive = False
                
    def send(self, msg):
        for sock in self.listClient:
            self.mysend(msg, sock)
    
    def mysend(self, msg, sock):
        totalsent = 0
        print('SEND : %s' % msg)
        msg += '\n\n'
        while totalsent < len(msg):
            sent = sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

serveurStreaming = StreamingManager()

def twitterStreaming():
    import socket
    from time import sleep
    sleep(5)
    try:
        # it's about time to create a TwitterSearch object with our secret tokens
        tso = TwitterSearchOrder() # create a TwitterSearchOrder object
        tso.set_keywords(['Swissquote']) # let's define all words we would like to have a look for
        tso.set_language('en') # we want to see German tweets only
        tso.set_include_entities(False) # and don't give us all those entity information
        lastID = 569803155141206016
        tso.set_since_id(lastID)        
        ts = TwitterSearch(
            consumer_key = 'a',
            consumer_secret = 'a',
            access_token = 'a-a',
            access_token_secret = 'b'
        )
        for tweet in ts.search_tweets_iterable(tso):
            print( '[%s]@%s tweeted: %s' % ( tweet['created_at'], tweet['user']['screen_name'], tweet['text'] ) )
            if(lastID < tweet['id']):
                lastID = tweet['id']
            serveurStreaming.send(tweet['text'])
    except TwitterSearchException as e: # take care of all those ugly errors if there are some
        print(e)
    serveurStreaming.isConnectionAlive = False

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
    ssc.awaitTermination(20)  # Wait for the computation to terminate    
        
if __name__ == '__main__':
    import threading
    t1 = threading.Thread(target=twitterStreaming)
    t2 = threading.Thread(target=sparkTask)    
    t2.start()
    t1.start()
    t2.join()
    quit()