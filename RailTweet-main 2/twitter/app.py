from helpers.aws_boto_helpers import aws_comprehend
from helpers.twint_helpers import config_twint
from helpers.twint_helpers import twint_to_pandas
from helpers.twint_helpers import run_twitter_parse
from helpers.twint_helpers import twitter_query_builder
from helpers.twint_helpers import available_columns
import pandas as pd
import twint
import time
import requests
import random
from bs4 import BeautifulSoup as bs

def get_session(proxies):
    # construct an HTTP session
    session = requests.Session()
    # choose one random proxy
    proxy = random.choice(proxies)
    print(proxy)
    session.proxies = {"http": proxy, "https": proxy}
    return session


def get_free_proxies():
    url = "https://free-proxy-list.net/"
    # get the HTTP response and construct soup object
    soup = bs(requests.get(url).content, "html.parser")
    proxies=[]
    for row in soup.find("table", attrs={"id": "proxylisttable"}).find_all("tr")[1:]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except IndexError:
            continue
    return proxies

tweet_limit = 100
required_search = ["Pepsi Max UK", "Ferrero"]
optional_search = [""]
negative_search = None #[""]
near = "paris"
geo = "55.3781°,3.4360°"
since = "2020-12-01"
until = "2021-15-02"

search = twitter_query_builder(required_search=required_search,
                               optional_search=optional_search,
                               negative_search=negative_search
                               )
print("generated query: " + search)
# get a twitter config from twint
config = config_twint(search=search,
                      tweet_limit=tweet_limit,
                      near=near,
                      geo=geo,
                      since=since,
                      until=until,
                      )

# run twitter parsing using twint
run_twitter_parse(config)
#
# a =available_columns()
# print(a)
# # get specified columns from parsed twitter data
df_pd = twint_to_pandas(["id", "username", "tweet","hashtags", "nlikes","near","date"])
# #

# # scrape only tweets from parsing
tweets = df_pd["tweet"]
print(tweets.head())
#
user_list = df_pd['username']
# print(user_list)
for i in user_list:
    try:
        proxies = get_free_proxies()
        s = get_session(proxies)
        c = twint.Config()
        c.Username = i
        c.Format = "{username},{followers}"
        c.Output = "followers.csv"
        twint.run.Lookup(c)
        time.sleep(2)
    except Exception as e:
        print(e)


follower_data = pd.read_csv("followers.csv",header=None)
follower_data.columns =['username','no of followers']
print(follower_data.head(5))

data = pd.concat([df_pd, follower_data], axis=1)
print(data.head(5))
# aws comprehend
senti_df = aws_comprehend(tweets)

new_df = pd.concat([df_pd,senti_df,follower_data['no of followers']], axis=1, sort=False)
new_df.to_csv('out.csv')
#
