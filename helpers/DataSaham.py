import pandas as pd
import pandas_datareader as pdr
import datetime as dt
import ta

class DataSaham():
    """
    This class is for constructing all the required variables. 
    There are 11 technical Indicators, sentiment score & category
    and Rupiah/USD exchange rate
    """

    def __init__(self, code, all_articles, saham, article_saham, start_date="2000-01-01", end_date=None, window=10, dropna=False):
        self.code = code
        self.full_data = self.__scraping_saham(start_date, end_date)
        self.__get_technical_indicators(window)
        if dropna:
            self.full_data = self.full_data.dropna()

        self.articles = self.__get_articles(all_articles, saham, article_saham)
        self.__get_sentiment_score()
        self.__get_sentiment_category()
        self.__get_kurs_rupiah()

    @property
    def data(self):
        selected_variabel = ['close', 'sma', 'wma', 'macd', 'cci', '%k', '%d',
                             'rsi', 'williams_r', 'mfi', 'momentum',
                             'sentiment_score', 'sentiment_category_score', 'kurs']
        return self.full_data[selected_variabel]

    def __get_articles(self, all_articles, saham, article_saham):
        saham_id = saham.loc[saham.code == self.code, "id"].to_list()[0]
        selected_article = article_saham[article_saham.saham_id == saham_id]

        articles = all_articles[all_articles.id.isin(
            selected_article.article_id.to_list())]
        articles.loc[:, 'date'] = articles.loc[:,
                                               'published_at'].dt.strftime("%Y-%m-%d")
        return articles

    def __scraping_saham(self, start_date="2000-01-01", end_date=None):
        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = dt.datetime.now() if end_date is None else dt.datetime.strptime(
            end_date, "%Y-%m-%d")

        data = (pdr.get_data_yahoo(self.code + '.JK', start_date, end_date)
                .rename(columns={"Adj Close": "adj_close"})
                .rename_axis('date')
                .reset_index())

        data.columns = data.columns.str.lower()
        data.loc[:, "date"] = data.date.astype(str)
        return data.set_index('date')

    def __momentum(self, close, window=10):
        def calculate(x):
            x = x.to_list()
            return x[window] - x[0]

        return close.rolling(window + 1).apply(calculate)

    def __acc_dist_oscilator(self, high, low, close):
        return (high - close.shift(1)) / (high - low)

    def __get_technical_indicators(self, window=10):
        self.full_data['sma'] = ta.trend.sma_indicator(
            self.full_data.close, window=window)
        self.full_data['wma'] = ta.trend.wma_indicator(
            self.full_data.close, window=window)
        self.full_data['macd'] = ta.trend.macd(self.full_data.close)
        self.full_data['cci'] = ta.trend.cci(
            self.full_data.high, self.full_data.low, self.full_data.close)
        self.full_data['%k'] = ta.momentum.stoch(
            self.full_data.high, self.full_data.low, self.full_data.close)
        self.full_data['%d'] = ta.momentum.stoch_signal(
            self.full_data.high, self.full_data.low, self.full_data.close)
        self.full_data['rsi'] = ta.momentum.rsi(self.full_data.close)
        self.full_data['williams_r'] = ta.momentum.williams_r(
            self.full_data.high, self.full_data.low, self.full_data.close)
        self.full_data['mfi'] = ta.volume.money_flow_index(
            self.full_data.high, self.full_data.low, self.full_data.close, self.full_data.volume)
        self.full_data['momentum'] = self.__momentum(
            self.full_data.close, window=window)
        self.full_data['a/d'] = self.__acc_dist_oscilator(
            self.full_data.high, self.full_data.low, self.full_data.close)

    def __get_sentiment_score(self):
        sentiment_article = (self.articles
                             .groupby('date')['mean_compound']
                             .mean()
                             .to_frame()
                             .reset_index()
                             .rename(columns={"mean_compound": "sentiment"}))

        new_df = self.full_data[['close']].copy().reset_index()
        new_df['date'] = new_df.date.astype(str)
        sentiment_close = (pd.merge(new_df, sentiment_article, on='date', how='outer')
                           .sort_values("date")
                           .reset_index(drop=True))
        sentiment_close['sentiment'] = sentiment_close.sentiment.fillna(0)

        # where the close price is null, meaning that there is no trading on that day
        # so the sentiment on that day will be averaged over the next trading day
        close_null = sentiment_close[sentiment_close.close.isnull(
        )].index.to_list()
        index_close_null = 0
        index_curr = -1
        sentiment = 0
        count_consecutive_day = 0

        while index_close_null <= len(close_null) - 1:

            # first day without trading
            index_curr = close_null[index_close_null]
            sentiment = sentiment_close.sentiment[index_curr]
            count_consecutive_day = 1
            index_curr += 1

            # where index curr not in close null, meaning there are
            # trading on that day
            while index_curr in close_null:
                sentiment += sentiment_close.sentiment[index_curr]
                count_consecutive_day += 1
                index_curr += 1
                index_close_null += 1

            try:
                if sentiment_close.sentiment[index_curr] != 0:
                    sentiment += sentiment_close.sentiment[index_curr]
                    count_consecutive_day += 1

                sentiment_close.loc[index_curr,
                                    "sentiment"] = sentiment / count_consecutive_day
            except:
                pass
            finally:
                index_close_null += 1

        sentiment_close = (sentiment_close[sentiment_close.close.notnull()]
                           .set_index('date')[['sentiment']]
                           .rename(columns={'sentiment': 'sentiment_score'}))

        self.full_data = self.full_data.join(sentiment_close).fillna(0)

    def __get_sentiment_category(self):
        sentiment_category = (self.articles
                              .groupby(['date', 'sentiment_category'])['sentiment_category']
                              .count()
                              .to_frame()
                              .rename(columns={"sentiment_category": 'jumlah'})
                              .reset_index()
                              .pivot(index='date', columns='sentiment_category', values='jumlah')
                              .fillna(0)
                              .reset_index()
                              .rename_axis(None, axis=1))
        sentiment_category.columns = sentiment_category.columns.str.lower()

        df = self.full_data[['close']].copy().reset_index()
        df = (pd.merge(df, sentiment_category, on='date', how='outer')
              .sort_values("date")
              .reset_index(drop=True))

        df.negative = df.negative.fillna(0)
        df.positive = df.positive.fillna(0)
        df.netral = df.netral.fillna(0)

        # where the close price is null, meaning that there is no trading on that day
        # so the sentiment on that day will be averaged over the next trading day
        close_null = df[df.close.isnull()].index.to_list()
        index_close_null = 0
        index_curr = -1
        pos = net = neg = 0

        while index_close_null <= len(close_null) - 1:
            # first day without trading
            index_curr = close_null[index_close_null]
            pos = df.positive[index_curr]
            neg = df.negative[index_curr]
            net = df.netral[index_curr]
            index_curr += 1

            # where index curr not in close null, meaning there are
            # trading on that day
            while index_curr in close_null:
                pos += df.positive[index_curr]
                neg += df.negative[index_curr]
                net += df.netral[index_curr]
                index_curr += 1
                index_close_null += 1

            try:
                df.loc[index_curr, "positive"] += pos
                df.loc[index_curr, "negative"] += neg
                df.loc[index_curr, "netral"] += net
            except:
                pass
            finally:
                index_close_null += 1

        df = df[df.close.notnull()].set_index('date').drop('close', axis=1)
        self.full_data = self.full_data.join(df).fillna(0)
        self.full_data['sentiment_category_score'] = (
            self.full_data.positive - self.full_data.negative) / (self.full_data.positive + self.full_data.negative + 1)

    def __get_kurs_rupiah(self):
        kurs = (pd.read_csv('data/kurs.csv')
                .loc[:, ["Date", "Price"]]
                .rename(columns={"Date": "date", "Price": "kurs"}))

        kurs['date'] = pd.to_datetime(kurs.date).astype(str)
        kurs['kurs'] = kurs.kurs.str.replace(',', '').astype(float)
        kurs = kurs.set_index('date')
        self.full_data = self.full_data.join(kurs)
