import os

DB_URI  = "mysql+pymysql://root:123@10.56.1.3:3306/signals"
PORT =  int(os.getenv("PORT",5000))

import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

