import requests
import pandas as pd
from datetime import datetime

eia_api = '5F4109570C68FDE20F42C25F5152D879'
sid = 'EBA.SCL-ALL.D.H'
start1 = '2016-08-11 01:00:00'
end1 = '2016-08-11 23:00:00'
freq1 = 'H'


class GetSeries(object):
    '''
    Performs a default call to the EIA API and captures the response
    '''

    eia_url = 'http://api.eia.gov/series/'

    def __init__(self, **kwargs):
        '''
        valid kwargs:
        :param api_key: an valid API key provided by EIA
        :param series: a valid EIA series ID
        '''
        self.kwargs = kwargs
        self.parms = self.create_parms()
        self.response = self.get_response()

    def create_parms(self):
        '''
        Convert kwargs into a list to pass into api call
        '''
        try:
            kwargs_list = [['api_key', self.kwargs['api_key']]]
            kwargs_list.append(['series_id', self.kwargs['series_id']])
        except KeyError:
            pass
        return kwargs_list

    def get_response(self):
        '''
         Calls the EIA API and returns response object
        '''
        api_parms = [tuple(parm) for parm in self.parms]
        return requests.get(self.eia_url, params=api_parms)


class CreateDataFrame(object):
    '''Creates the dataframe for Energy API call'''

    def __init__(self, json):
        """:param json: eia json"""
        self.json = json
        self.series = self.json['series']
        self.data = self.series[0]['data']
        self.df = self.create_dataframe()

    def create_dataframe(self):
        """Function to create dataframe from json['series'] """
        values = [x[1] for x in self.data]
        dates = self.get_dates()
        return pd.DataFrame(values, index=dates, columns=['values'])

    def get_dates(self):
        """Parses text dates to datetime index"""
        freq = {'A': '%Y', 'M': '%Y%m', 'W': '%Y%m%d',
                'D': '%Y%m%d', 'H': '%Y%m%d %H'}
        date_list = []
        for x in self.data:
            # need to add this ugly bit to remove hourly time format from EIA
            time = x[0].replace('T', ' ')
            time = time.replace('Z', '')
            time = datetime.strptime(time, freq[self.series[0]['f']])
            date_list.append(time.strftime('%Y-%m-%d %H:%M:%S'))
        return date_list
