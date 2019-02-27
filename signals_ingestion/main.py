from src import Pipeline
from prometheus_client import start_http_server

if __name__ == "__main__":
    
    start_http_server(9102)
    
    pipeline = Pipeline()
    
    pipeline.run()