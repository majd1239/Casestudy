from functools import reduce
from operator import add
import requests
from aiohttp import ClientSession
import os
from datetime import datetime,timedelta
import json
from itertools import repeat
import time
from hashlib import md5
from asyncio import ensure_future,as_completed,get_event_loop
from configs import logger,API_URL,HEADERS

class Sites:
    def __init__(self):
        self.url = API_URL.format("sites")
  
        self.data = self.getData()
    
    def __len__(self):
        return len(self.data)
    
    def __iter__(self):
        return iter(self.data)
    
    def getData(self):
        request = requests.get(self.url,headers=HEADERS)
        
        status_code,content = request.status_code,request.content
        
        if status_code!=200:
            logger.error('''Error fetching /Sites from API,
                            status_code: {} error {}'''.format(status_code,str(content)))
        
        data = json.loads(content)
        
        return list(map(lambda record: {"siteId": record["siteId"]} ,data))
    
        
class Turbines:
    def __init__(self,site_id):
        self.url = API_URL.format("turbines")
        
        self.data = self.getData({'siteId':'site_{}'.format(site_id)})
    
    def __len__(self):
        return len(self.data)
    
    def __iter__(self):
        return iter(self.data)
    
    def getData(self,siteId):
        
        request = requests.get(self.url,headers=HEADERS,params=siteId)
        
        status_code,content = request.status_code,request.content
        
        if status_code!=200:
            logger.error('''Error fetching /turbines from API,
                            status_code: {} error {}'''.format(status_code,str(content)))
        
        data = json.loads(content)
        
        for record in data:
            record.update(siteId)
        
        return data
        
class Signals:
    def __init__(self,turbines):
        self.url = API_URL.format("signals")
        
        self.turbines = turbines
        
        self.loop = get_event_loop()
    
    def collect(self,startEpochMs):
        
        async def coroutine():
        
            endEpochMs = int(time.time()*1000)
            times = (startEpochMs,endEpochMs)
            
            async with ClientSession() as session:
                tasks = [ensure_future(self._getData(session,turbine,times)) for turbine in self.turbines]

                results = []

                for future in  as_completed(tasks,timeout=60):
                    results+= await future

            return endEpochMs,results
        
        return self.loop.run_until_complete(coroutine())
    

    
    async def _getData(self,session,turbineData,times):
        
        startEpochMs,endEpochMs = times
        
        params = {}
        
        params["startEpochMs"] = startEpochMs
            
        params["endEpochMs"] = endEpochMs
            
        params["turbineId"] = turbineData["turbineId"]
        
        
        for retry in range(3):
            async with session.get(self.url,headers=HEADERS,params=params ) as response:
                status_code = response.status
                
                if status_code == 200:
                    content =  await response.read()
                    break
                
                if status_code==429:
                    time.sleep(0.1)

        if retry==2: 
            logger.error('''Error Fetching Turbines Signals from API, 
                             timestamp: {} status_code: {}:
                             '''.format(startEpochMs,status_code))
            return []   
        
        data = json.loads(content)
        
        for record in data:
            
            for key,value in turbineData.items():
                record.update({key:value})
                
            record.update({"rowKey":md5(str(record).encode()).hexdigest()})
        
        return data