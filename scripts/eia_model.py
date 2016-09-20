import requests
import pandas as pd
from datetime import datetime

eia_api = '5F4109570C68FDE20F42C25F5152D879'
sid = 'EBA.SCL-ALL.D.H'
start1 = '2016-08-11 01:00:00'
end1 = '2016-08-11 23:00:00'
freq1 = 'H'


class GetSeries(object):
    """
    A class to capture an EIA API call and turn it into a pd dataframe
    """

    eia_url = 'http://api.eia.gov/series/'

    def __init__(self, api_key, series_id, **kwargs):
        '''
        Required parms
        :param api_key: an API key that is provided by EIA
        :param series_id: a valid EIA series_id
        Optional parms to query date range - all 3 must be specified
        :param start: an optional start date as %Y-%m-%d %H:%M:%S
        :param end: an optional end date %Y%m%d %H
        :param freq:  frequency of data valid inputs: 'A', 'M', 'W', 'D', 'H'
        '''
        self.parms = [['api_key', api_key], ['series_id', series_id]]
        self.parms.extend(self.create_optional_parms(kwargs))
        self.response = self.get_response()
        self.df = ParseEnergyData(self.response.json()).df

    def get_response(self):
        '''Calls the EIA API with supplied api_key on init and series_id and return json'''
        api_parms = [tuple(parm) for parm in self.parms]
        return requests.get(self.eia_url, params=tuple(api_parms))

    def create_optional_parms(self, kwargs):
        '''Return list of formatted start and end date if p freq=rovided'''
        kwargs_list = []
        try:
            kwargs_list.append(['start', self.format_date(kwargs['start'], kwargs['freq'])])
            kwargs_list.append(['end', self.format_date(kwargs['end'], kwargs['freq'])])
        except:
            pass
        return kwargs_list

    def format_date(self, date, freq):
        '''Formats dates for api call'''
        date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        freq_dict = {'A': '%Y', 'M': '%Y%m', 'W': '%Y%m%d',
                     'D': '%Y%m%d', 'H': '%Y%m%dT%HZ'}
        formatted_date = datetime.strftime(date, freq_dict[freq])
        return formatted_date


class ParseEnergyData(object):
    '''Creates the dataframe for Energy API call'''

    def __init__(self, json):
        ''':param json: eia json'''
        self.json = json
        self.series = self.json['series']
        self.data = self.series[0]['data']
        self.df = self.create_dataframe()

    def create_dataframe(self):
        '''Function to create dataframe from json['series']'''
        values = [x[1] for x in self.data]
        dates = self.get_dates()
        return pd.DataFrame(values, index=dates, columns=['values'])

    def get_dates(self):
        '''Parses text dates to datetime index'''
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
