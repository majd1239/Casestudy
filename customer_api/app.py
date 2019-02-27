from sanic.response import json
from sanic import Sanic
import time
import traceback
import ujson
from datetime import datetime,timedelta
import random

app = Sanic(__name__)

class Service:
        
    @classmethod
    def Start(cls,sites_mock,turbines_mock):
        
        cls.sites_data = sites_mock
        
        cls.turbines_data = {}
        for (i,k),site in zip([(0,800),(800,1600),(1600,2500)],['site_1','site_2','site_3']):
            cls.turbines_data[site] = turbines_mock[i:k]
        
        app.run(host='0.0.0.0', port=80)
        
    @app.route('/sites',methods=['GET'])
    async def sites(request):
        return json(Service.sites_data)
    
    @app.route('/turbines',methods=['GET'])
    async def turbines(request):
        siteId = request.args['siteId'][0]
        
        return json(Service.turbines_data[siteId])
    
    @app.route('/signals',methods=['GET'])
    async def signals(request):
        
        start,end = int(request.args['startEpochMs'][0]) , int(request.args['endEpochMs'][0])
        turbine_id = request.args['turbineId'][0]
        
        turbine_id = int(turbine_id.split("_")[-1]) - 1
        
        diff = min(180,max(1,int((end-start)/1000)))
        
        date_str = lambda x: x.strftime("%Y-%m-%dT%H:%M:%S.%f")
        
        times = map(date_str,[datetime.fromtimestamp(int(start)/1000) + timedelta(milliseconds=i) for i in range(diff)])
        
        response_data = []
        
        for time in times:
            data = {'cellTemp': round(random.uniform(30,55),3),
             'orientation': round(random.uniform(30,370),3),
             'power': round(random.uniform(100,550),3),
             'rpm': round(random.uniform(0,8),3),
             'temperature':round(random.uniform(32,55),3),
             'vibration': round(random.uniform(3000,9479),3),
             'windSpeed': round(random.uniform(10,36),0)
             }
            if turbine_id<1250:
                data['bearingTemp'] = round(random.uniform(30,55),3)
            else:
                data['bladeAngle'] = round(random.uniform(164,280),0)
                
            data['gear'] = 'gear_{}'.format(random.randint(1,10))
            
            data['timestamp'] = time
            
            response_data.append(data)
            
            
        return json(response_data)
        
    
    @app.route('/ping')
    def ping(request):
        return json({"Respone":"pong"})
    
    
    @app.exception(Exception)
    def route_exceptions(request, exception):
        return json("Error: {}".format(str(traceback.format_exc())), status=500)

        
if __name__ == "__main__":

    sites_mock = ujson.load(open('mock_data/sites_mock.json',"r"))
    turbines_mock = ujson.load(open('mock_data/turbines_mock.json',"r"))
    
    Service.Start(sites_mock,turbines_mock)