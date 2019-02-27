import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from src import streamBQ,streamDB

class Dataflow_Pipeline:
    
    def __init__(self):
        for option,value in PipelineOptions().get_all_options().items():
            setattr(self,option,value)
        
        self.save_main_session = True
        self.runner = 'DataflowRunner'
        self.project = 'casestudy'
        self.staging_location = 'gs://turbines-dataflow-staging/'
        self.temp_location = 'gs://turbines-dataflow-temp/'
        self.job_name = "turbine-signals-persisting"
        self.setup_file = './setup.py'
        self.disk_size_gb = 50
        self.autoscaling_algorithm='THROUGHPUT_BASED'
        self.max_num_workers = 3
        self.streaming = True
     
        
        self.topics = ["projects/casestudy/topics/turbines_site_{}".format(i+1) for i in range(3)]
        
    def items(self):
        options = set(PipelineOptions().get_all_options().keys())
        return {key:value for key,value in self.__dict__.items() if value and key in options}.items()
    
    def get_all_options(self):
        return self.options.get_all_options()
    
    @property
    def options(self):
        return PipelineOptions().from_dictionary(self)
        
    def run(self):
        with beam.Pipeline(options=self.options) as p:
            
            site_1 = p | "Read Site_1 Data" >> beam.io.ReadFromPubSub(topic=self.topics[0])
            
            site_2 = p | "Read Site_2 Data" >> beam.io.ReadFromPubSub(topic=self.topics[1])
            
            site_3 = p | "Read Site_3 Data" >> beam.io.ReadFromPubSub(topic=self.topics[2])
            
            raw_data = (site_1, site_2, site_3) | 'Merge Records' >> beam.Flatten()
            
            batch_data = raw_data | 'Batch Records' >> beam.BatchElements(min_batch_size=5,max_batch_size=100)
            
            batch_data | "Stream to BQ" >> beam.ParDo(streamBQ()) 
            
            raw_data | "Stream to Postgres" >> beam.ParDo(streamDB())
            


if __name__ == "__main__":
    pipeline = Dataflow_Pipeline()
    pipeline.run()

