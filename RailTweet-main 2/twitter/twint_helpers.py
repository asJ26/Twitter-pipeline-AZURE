import twint


def config_twint(search,
                 tweet_limit,
                 near=None,
                 lang='en',
                 verified=False,
                 since=None,
                 until=None,
                 geo=None,
                 output=None
                 ):
    """
    This method will be used to config twitter search parameters for twint package
    :param search: (str) Search terms
    :param tweet_limit: (int) Number of Tweets to pull (Increments of 100)
    :param near: str) Near a certain City (Example: london)
    :param lang: (str) Compatible language codes: https://github.com/twintproject/twint/wiki/Langauge-codes
    :param verified: (bool) Set to True to only show Tweets by _verified_ users
    :return:
    """

    c = twint.Config()
    c.Search = search
    c.Debug = False
    c.Limit = tweet_limit
    c.Filter_retweets = True
    c.Pandas = True
    c.Count = True
    c.Hide_output = True
    c.Near = near
    c.Lang = lang
    c.Verified = verified
    c.Since = since
    c.Until = until
    c.Geo = geo
    c.Output = output

    return c


def run_twitter_parse(config):
    """
    This method will trigger twitter parsing using twint
    :param config: (obj) config object which is extracted from config_twint()
    :return: None
    """

    twint.run.Search(config)


def available_columns():
    """
    This method will return all possible columns that we fetched during twitter parsing
    :return: list of column names
    """
    return twint.output.panda.Tweets_df.columns


def twint_to_pandas(columns):
    """
    This method will return the filtered list of columns
    :param columns: (list) list of column names we required for analysis
    :return: parsed tweets with the filtered list of columns
    """
    return twint.output.panda.Tweets_df[columns]


def twitter_query_builder(required_search,
                          optional_search=None,
                          negative_search=None):
    """
    This method will return the search query for twitter parsing
    :param required_search: mandatory keywords for twitter search
    :param optional_search: optional keywords for twitter search
    :param negative_search: optional keywords which are not supposed to be in the query
    :return: query string with the combination of required_search, optional_search and negative_search
    """
    query = ''
    try:
        if required_search is None:
            raise Exception

        for i in range(len(required_search)):
            if len(required_search) == 1:
                query = required_search[i]
                break

            if i == len(required_search) - 1:
                query = query + required_search[i]

            else:
                query = query + required_search[i] + " AND "

        if optional_search is not None:
            for i in range(len(optional_search)):
                if len(optional_search) == 1:
                    query = query + " OR " + optional_search[i]
                    break

                if i == len(optional_search) - 1:
                    query = query + optional_search[i]
                else:
                    query = query + " OR " + optional_search[i] + " OR "

        if negative_search is not None:
            for i in range(len(negative_search)):
                if len(negative_search) == 1:
                    query = query + " -" + negative_search[i]
                    break

                if i == len(negative_search) - 1:
                    query = query + negative_search[i]
                else:
                    query = query + " -" + negative_search[i] + " -"

        return query

    except Exception as e:
        print(e)
