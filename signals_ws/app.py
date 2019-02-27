from flask import request,jsonify
from flask import Flask
from prometheus_client import start_http_server
from flask_sqlalchemy import SQLAlchemy
from src import Monitor
from configs import *
from sqlalchemy.sql import text
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI 

db = SQLAlchemy(app)

class Harness:
    
    def __init__(self):
        
        Monitor.monitor_flask(app)
        
        start_http_server(9102)
        
        app.run(host="0.0.0.0",port=80)
        
    @app.route('/signals')
    def service():
        
        if 'startEpochMs' not in request.args or 'endEpochMs' not in request.args:
            raise Exception("Missing startEpochMs or endEpochMs in params")
            
        if 'turbineId' not in request.args:
            raise Exception("Missing turbineId")
            
        start,end = request.args['startEpochMs'] , request.args['endEpochMs']
        
        turbine = request.args['turbineId']
        
        tables = ['manufacturer_1', 'manufacturer_2']
        
        query = 'select * from {} where turbineId="{}" and timestamp between {} and {}'
        
        results = {}
            
        def fetch_query(table):
            rows = db.engine.execute(query.format(table,turbine,start,end))
            keys = rows.keys()
            results[table] = [dict(zip(keys,row)) for row in rows.fetchall()]
        
        with ThreadPoolExecutor() as f:
            f.map(fetch_query,tables)
            
        return jsonify(results), 200
        
    
    @app.route('/ping')
    def ping():
        return jsonify({"Respone":"pong"}), 200
    
    @app.errorhandler(Exception)
    def unhandled_exception(e):
        logger.error("Error in processing request: {}".format(str(e)))
        return jsonify({"Error: ": str(e)}), 500


if __name__ == "__main__":
    
    Harness()
    
