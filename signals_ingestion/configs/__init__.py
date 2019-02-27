import os

INTERVAL = int(os.getenv("INTERVAL",5))

API_URL = "http://" + os.getenv("APIURL","customer-api.default.svc.cluster.local") +  "/{}"

SITE_ID = int(os.getenv('SITE_ID','site_1').split("-")[-1])+1

TOPIC = os.getenv("TOPIC","projects/casestudy/topics/turbines_site_{}".format(SITE_ID))

HEADERS = {'apiKey': 'casestudy'}

GCP_KEY = 'casestudy-key.json'

CHECKPOINT_PATH = '/opt/checkpoint.json'

import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

from prometheus_client import Summary,Counter

FETCH_TIME = Summary('data_fetching_seconds', 'Time spent fetching data')

DATA_INGESTED_COUNTER = Counter('data_ingested_counter', 'Data Ingested Counter')

FAILURE_COUNTER = Counter('failure_counter', 'App Failure Counter')