from sqlalchemy import create_engine
import pandas as pd
from pandas_gbq import to_gbq
import apache_beam as beam
from datetime import datetime,timedelta
import json,time 
from concurrent.futures import ThreadPoolExecutor
from .configs import *

class streamBQ(beam.DoFn):
    def process(self,batch):

        start = time.time()

        data = []

        for record in batch:
            data += json.loads(record)

        df = pd.DataFrame(data)

        with ThreadPoolExecutor() as f:
            f.map(self.stream,df.groupby('manufacturer',as_index=False))

        logger.info("Streamed {} records to BQ in {} seconds".format(len(df),round(time.time()-start,2)))
        
    def stream(self,args):
        manufacturer,data = args
        data= data.dropna(how='all',axis=1).reset_index(drop=True)

        to_gbq(data,destination_table="Turbines.{}".format(manufacturer),if_exists='append',
               project_id="casestudy")

class streamDB(beam.DoFn):
    def __init__(self):
        self.current_day = datetime.fromtimestamp(time.time()).day
    
    def start_bundle(self):
        self.engine = create_engine(DB_URI)
        
        self.tables = self.engine.table_names()
        
    def close_bundle(self):
        self.engine.dispose()
        
    def process(self, data):
        start = time.time()
         
        data = json.loads(data)
        
        df = pd.DataFrame(data)
        
        df.coordinates = df.coordinates.apply(str)
        
        df.timestamp = df.timestamp.apply(self.to_epochs)
        
        for table,data in df.groupby('manufacturer'):
            
            data = data.dropna(how='all',axis=1).reset_index(drop=True)
            
            try:
                data.to_sql(table, self.engine, if_exists='append', index=False)
                
            except:
                data = self.remove_duplicates(data,table)
                
                data.to_sql(table, self.engine, if_exists='append', index=False)
                
                logger.info('Encountered duplicates,deduped and inserted to db')
                
            if len(self.tables)==0:
                self.engine.execute('ALTER TABLE {} ADD PRIMARY KEY (rowKey(40))'.format(table))
        
        logger.info("Wrote {} records to mySQL db in {} seconds".format(len(df),round(time.time()-start,2)))
        
        day = datetime.fromtimestamp(time.time()).day
        
        if day!=self.current_day:
            self.deleteOldRecords()
            self.current_day = day
            
    def to_epochs(self,timestamp):
        dt = datetime.strptime(timestamp,"%Y-%m-%dT%H:%M:%S.%f")
        
        epochs = time.mktime(dt.timetuple()) + dt.microsecond * 1e-6
        
        return int(epochs*1000)
    
    def remove_duplicates(self,data,table):
        
        min_time,max_time = data.timestamp.min(),data.timestamp.max()

        query = 'select rowKey from {} where timestamp between {} and {}'.format(table,min_time,max_time)

        results = self.engine.execute(query)

        primary_keys = [item[0] for item in results.fetchall()]

        return data[~data['rowKey'].isin(primary_keys)]
        
    
    def deleteOldRecords(self,day):
        
        days_30 = datetime.now() - timedelta(days=30)
        
        days_30_epochs = int(days_30.timestamp()*1000)
        
        tables = self.engine.table_names()
        
        if len(tables)==0: return
        
        query = 'DELETE FROM {} WHERE timestamp > {};'
        
        for table in tables:
            self.engine.execute(query.format(table,days_30_epochs))
            
        logger.info("Deleted records older than 30 days")
            



    