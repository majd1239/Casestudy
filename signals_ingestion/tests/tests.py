import unittest
from src.Api import Sites,Turbines,Signals


class TestApi(unittest.TestCase):
    
    def testSites(self):
        sites = Sites()
        
        self.assertEqual(len(sites),3)
        
        expected_sites = [{'siteId': 'site_1'}, {'siteId': 'site_2'}, {'siteId': 'site_3'}]
        
        for site,expected_site in zip(sites,expected_sites):
            self.assertEqual(site,expected_site)
            
            
    def testTurbines(self):
        #sites =  Sites()
        
        turbines = Turbines(0)
        
        self.assertTrue(len(turbines)>0)
        
        expected_turbine_keys = ['turbineId', 'coordinates', 'manufacturer', 'model', 'siteId']
        
        self.assertEqual(list(turbines.data[0].keys()),expected_turbine_keys)
        
        
    def testSignals(self):
        sites =  Sites()
        
        turbines = Turbines(sites)
        
        signals = Signals(turbines)
        
        start = int(time.time()/1000)
        
        end,data = signals.collect(start)
        
        self.assertLess(start,end)
        
        self.assertTrue(len(data)>0)
        
        expected_signals_keys = ['rpm', 'temperature', 'power', 'windSpeed', 'orientation', 'vibration', 'cellTemp','bearingTemp', 'gear', 'timestamp', 'turbineId', 'coordinates', 'manufacturer', 'model', 'siteId', 'rowKey']
        keys = list(data[0].keys())
        
        self.assertEqual(set(keys),set(expected_signals_keys))

        
                        
if __name__ == '__main__':
    
    unittest.main()
