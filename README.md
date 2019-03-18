# Turbines Signals Ingestion

The pipeline is made of four components.

1) Async API that mimicks IOT data transmit

2) Pub/Sub Ingestion Pipeline that runs on stateful deployment on Kubernetes

3) Persistance Streaming DataFlow pipeline that stores the data in BQ table and mySQL tables

4) API that serves the data
