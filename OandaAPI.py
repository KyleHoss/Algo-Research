
class OandaAPI:
    def __init__(self, account_id, api_token):
        self.ACCOUNT_ID = account_id
        self.API_TOKEN = api_token
        self.API_URL = "api-fxtrade.oanda.com"
        self.STREAM_URL = "stream-fxtrade.oanda.com"


    def get_historical_data(self, instrument, start_date, end_date, granularity='D' ,as_pandas=True):
        # Must import Necessary Libraries
        import time
        import requests
        import pandas as pd

        # Convert Dates to DateTime objects
        start_dateTime = pd.to_datetime(start_date)
        end_dateTime = pd.to_datetime(end_date)

        # Convert Start Date & End Date to a UNIX timestamp
        unix_start = time.mktime(start_dateTime.timetuple())
        unix_end = time.mktime(end_dateTime.timetuple())

        # Authorization Header
        auth_header = {"Authorization": "Bearer "+self.API_TOKEN} 

        # Query Parameters
        parameters = {"from": str(unix_start), 
                      "to": str(unix_end), 
                      "granularity": granularity}
        
        # Historical Candle Stick Data URL
        candle_url = f"/v3/accounts/{self.ACCOUNT_ID}/instruments/{instrument}/candles"

        # Request for Candle Stick Data
        json_response = requests.get("https://"+self.API_URL+candle_url, headers=auth_header, params=parameters).json()

        # Return as Pandas DataFrame
        if as_pandas is True:
            # Convert Json to Pandas df
            candle_df = pd.json_normalize(json_response['candles'])

            # Drop complete Column
            candle_df.drop('complete', inplace=True, axis=1)

            # Rename Columns
            candle_df.rename(inplace=True,columns={'time':'DateTime',
                                                   'volume':'Volume',
                                                   'mid.o':'Open',
                                                   'mid.h':'High',
                                                   'mid.l':'Low',
                                                   'mid.c':'Close'})

            # Convert Datetime= Column to datetime object
            candle_df['DateTime'] = pd.to_datetime(candle_df['DateTime'])

            # Set DateTime to Index
            candle_df.set_index('DateTime',inplace=True)

            # Restructure Column Names
            candle_df = candle_df[['Open','High','Low','Close','Volume']]

            return candle_df
        else: 
            return json_response


    def show_granularity(self):
        import pandas as pd

        # Values of Granularity
        graulatity_values = ['S5','S10','S15','S30','M1','M2','M4','M5','M10','M15','M30','H1','H2','H3','H4','H6','H8','H12','D','W','M']
        
        # Descriptions of Granularity values
        granulatiry_descriptions = ['5 second candlesticks, minute alignment','10 second candlesticks, minute alignment',
                                    '15 second candlesticks, minute alignment','30 second candlesticks, minute alignment',
                                    '1 minute candlesticks, minute alignment','2 minute candlesticks, hour alignment',
                                    '4 minute candlesticks, hour alignment','5 minute candlesticks, hour alignment',
                                    '10 minute candlesticks, hour alignment','15 minute candlesticks, hour alignment',
                                    '30 minute candlesticks, hour alignment','1 hour candlesticks, hour alignment',
                                    '2 hour candlesticks, day alignment','3 hour candlesticks, day alignment',
                                    '4 hour candlesticks, day alignment','6 hour candlesticks, day alignment',
                                    '8 hour candlesticks, day alignment','12 hour candlesticks, day alignment',
                                    '1 day candlesticks, day alignment','1 week candlesticks, aligned to start of week',
                                    '1 month candlesticks, aligned to first day of the month']
        
        # Create Pandas DataFrame of granularity values
        granularity_df = pd.DataFrame({'Granularity Value': graulatity_values, 'Description': granulatiry_descriptions})
        
        # Set Granularity Values as Index
        granularity_df.set_index('Granularity Value',inplace=True)

        # Return Pandas Dataframe of granularity values
        return granularity_df