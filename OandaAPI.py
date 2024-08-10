
class OandaAPI:
    def __init__(self, account_id, api_token):
        self.ACCOUNT_ID = account_id
        self.API_TOKEN = api_token
        self.API_URL = "api-fxtrade.oanda.com"
        self.STREAM_URL = "stream-fxtrade.oanda.com"

        self.granularity_conv_dict = {'S5': 5,'S10': 10,'S15': 15,'S30': 30,
                                'M1': 60,'M2': 120,'M4': 240,'M5': 300,
                                'M10': 600,'M15': 900,'M30': 1800,
                                'H1': 3600,'H2': 7200,'H3': 10800,
                                'H4': 14400,'H6': 21600,'H8': 28800,
                                'H12': 43200,'D': 86400,'W': 604800,
                                'M': 2620800} 

    def candle_delta(self, start_date='08/09/2023', end_date='08/09/2024', granularity='M5') -> float:
        """This will return the number of candles between start_date and end_date.

        Args:
            start_date: Date to start calculations.
            end_date: Date if ending.
            granularity: Price update frequency.

        Returns:
            float: Number of candle sticks between start_date and end_date.
        """
        # Import Necessary Libraries
        import pandas as pd

        # Convert Dates to dateTimes
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date)

        # Calculate Seconds Between DateTimes
        datetime_dif = end_datetime - start_datetime   
        seconds_between = datetime_dif.total_seconds() 

        # Convert second between to number of candles
        num_candles = seconds_between / self.granularity_conv_dict.get(granularity)

        # Return Number of Candle Sicks
        return num_candles

    def historical_data(self, currency_pair='EUR_USD', start_date='08/09/2023', end_date='08/09/2024', granularity='D', as_pandas=True):
        """Will get the historical json data for a given currency pair.

        Args:
            currency_pair: Currency pair name. 
            start_date: Date of start of historical data.
            end_date: Closest date of historical data. 
            granularity: How often price data is updated.
            as_pandas: Set to True to return as pandas dataframe.

        Returns:
            json: Historical pricing data in json format.
            Pandas: Historical pricing dataframe.
        """
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
        candle_url = f"/v3/accounts/{self.ACCOUNT_ID}/instruments/{currency_pair}/candles"

        # Request for Candle Stick Data
        json_response = requests.get("https://"+self.API_URL+candle_url, headers=auth_header, params=parameters).json()

        # Create Pandas DataFrame
        if as_pandas is True:
            # Convert Json to Pandas df
            candle_df = pd.json_normalize(json_response["candles"])

            # Drop complete Column
            try: 
                candle_df.drop('complete', inplace=True, axis=1)
            except Exception as e:
                print(json_response)
                print(e)

            # Rename Columns
            candle_df.rename(inplace=True,columns={'time':'DateTime','volume':'Volume','mid.o':'Open',
                                                    'mid.h':'High','mid.l':'Low','mid.c':'Close'})

            # Convert Datetime= Column to datetime object
            candle_df['DateTime'] = pd.to_datetime(candle_df['DateTime'])

            # Set DateTime to Index
            candle_df.set_index('DateTime',inplace=True)

            # Restructure Column Names
            candle_df = candle_df[['Open','High','Low','Close','Volume']]
            
            # Return DataFrame
            return candle_df
    
        # Return as Json 
        else: 
            return json_response

    def load_candlestick_datafame(self, currency_pair='EUR_USD',start_date='08/09/2023', end_date='08/09/2024', granularity='D'):
        """This will return a large candle stick dataframe 

        Args:
            currency_pair: Currency pair name. 
            start_date: Date of start of historical data.
            end_date: Closest date of historical data. 
            granularity: How often price data is updated.

        Returns:
            Pandas: A large dataframe of candle stick data.
        """

        # Import Necessary Libraries
        import math
        import tqdm
        import pandas as pd
        from datetime import timedelta

        # Set Constants
        MAX_CANDLES = 4000  # Max Number of candles retrieved each call
        
        # Calculate number of candles between datetimes
        num_candles = self.candle_delta(start_date=start_date,end_date=end_date,
                                        granularity=granularity)

        # Convert to DateTime foramt
        start_datetime = pd.to_datetime(start_date)
        end_datetime = pd.to_datetime(end_date)

        # Initialize Variables
        candle_secs = MAX_CANDLES * math.floor(self.granularity_conv_dict.get(granularity))   # Max candles forwards in seconds
        max_date = start_datetime+timedelta(seconds=candle_secs)                              # Max date forwards in candles
        new_start_datetime = start_datetime                                                   # New Start DateTime variable to hold future start date
        candles_df = pd.DataFrame()                                                           # Pandas DataFrame to hold candlestick data
        start_datetime_list = []                                                              # Start DateTime list 
        end_datetime_list = []                                                                # End DateTime list

        if num_candles < MAX_CANDLES:

            # Fetch Historical Price Data
            candles_df = self.historical_data(currency_pair=currency_pair, start_date=start_date,
                                             end_date=end_date, granularity=granularity,
                                             as_pandas=True)
            
            # Return Candle Stick DataFrame
            return candles_df
        
        else: 
            while True:
                if max_date >= end_datetime:

                    # Append Last DateTime values
                    start_datetime_list.append(new_start_datetime)
                    end_datetime_list.append(end_datetime)

                    # Break out of While Loop
                    break

                else:
                    # Append DateTimes to lists
                    start_datetime_list.append(new_start_datetime)
                    end_datetime_list.append(max_date) 
                    
                    # Overwrite existing variables
                    candle_secs = MAX_CANDLES * math.floor(self.granularity_conv_dict.get(granularity))   # Max candles forwards in seconds
                    new_start_datetime = max_date+timedelta(seconds=self.granularity_conv_dict.get(granularity))                          # Set new date time to old max_date plus additional candle secs
                    max_date = new_start_datetime+timedelta(seconds=candle_secs)                          # Set new max date to last start datetime plus additional candle secs

            # Create Loading Bar 
            for i in tqdm.tqdm(range(len(start_datetime_list)),                           # Iteration range
                               colour='GREEN',                                            # Loading Bar Color
                               ncols=100,                                                 # Loading Bar width
                               desc=f'Downloading {currency_pair} {granularity} Data'):   # Loading Message

                # Download Historical Data
                new_candles_df = self.historical_data(currency_pair=currency_pair, start_date=start_datetime_list[i],   
                                                      end_date=end_datetime_list[i], granularity=granularity)
                # Concatenate DateFrames
                candles_df = pd.concat([candles_df, new_candles_df])
            
            # Return Candles Stick DataFrame
            return candles_df
            
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