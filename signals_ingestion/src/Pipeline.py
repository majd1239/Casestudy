import os
import time
import json
from google.cloud import pubsub
from .Api import Sites,Turbines,Signals
import pandas as pd
from pandas_gbq import to_gbq
from configs import *
from random import choice,random
from toolz import partition_all

class Pipeline:
    def __init__(self):

        self.turbines = Turbines(SITE_ID)
        
        self.signals = Signals(self.turbines)
        
        self.producer = pubsub.PublisherClient()
        
        self.checkpoint = False
        
        self.timestamp = int(time.time()*1000)


    @FETCH_TIME.time()
    def fetchData(self):
        if self.checkpoint is False and os.path.exists(CHECKPOINT_PATH):
            
            FAILURE_COUNTER.inc()
            
            checkpoint = json.load(open(CHECKPOINT_PATH))
        
            self.timestamp = checkpoint["timestamp"]
            
            logger.info("Picking up from checkpoint at timestamp {}".format(self.timestamp))
            
        endEpochMs, data = self.signals.collect(startEpochMs = self.timestamp)
        
        logger.info("succefully pulled {} data points from {} to {}".format(len(data),self.timestamp,endEpochMs))
        
        self.timestamp = endEpochMs + 1
        
        DATA_INGESTED_COUNTER.inc(len(data))
        
        return data

    def save_checkpoint(self):
        checkpoint = {}
        
        checkpoint["timestamp"] = self.timestamp
        
        json.dump(checkpoint,open(CHECKPOINT_PATH,"w"))
        
        self.checkpoint = True
        
    def _callbackSuccess(self,record_metadata):
        logger.info("Succefully published batch to topic turbines_site_{}".format(SITE_ID))
    
    
    def refreshData(self):
        self.sites = Sites()
        
        self.turbines = Turbines(self.sites)
        
        self.signals = Signals(self.turbines)
        
    def pushToPub(self,data):
        for batch in partition_all(4000,data):
            encoded_data = json.dumps(batch).encode()
        
            self.producer.publish(TOPIC,encoded_data).add_done_callback(self._callbackSuccess)
            
        
    def run(self):
        while(True):
                
            start = time.time()
            
            data = self.fetchData()
            
            if len(data)!=0:
                
                self.pushToPub(data)
                    
            self.save_checkpoint()
            
            time_elapsed = time.time() - start
            
            logger.info("Elapsed Time {}".format(time_elapsed))
            
            sleep_time = max(0,INTERVAL - time_elapsed)
            
            logger.info("Sleeping for {} seconds".format(sleep_time))
            
            time.sleep(sleep_time)
            