import gc
import time
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge

from flask import Flask,make_response,request


def remove_gc_collectors():
    for callback in gc.callbacks[:]:
        if 'GCCollector.' in callback.__qualname__:
            gc.callbacks.remove(callback)

    for name, collector in list(prometheus_client.REGISTRY._names_to_collectors.items()):
        if 'python_gc_' in name:
            try:
                prometheus_client.REGISTRY.unregister(collector)
            except KeyError:
                pass

remove_gc_collectors()


class Monitor:

        
    _request_histo = Histogram('http_requests_duration_seconds', 'Http request duration in seconds',
                               ['method', 'path', 'response_code'])

    _request_count = Counter('http_requests_total', 'Http request total counts',
                             ['method', 'path', 'response_code'])


    @staticmethod
    def monitor_flask(app):
        
        @app.before_request
        def before_request():
            request.start_time = time.time()

        @app.after_request
        def after_request(response):
            request_latency = time.time() - request.start_time
            
            Monitor._request_histo.labels(request.method, request.path, response.status_code).observe(request_latency)
            
            Monitor._request_count.labels(request.method, request.path, response.status_code).inc()
            
            return response
            
        