import time

from quixstreams import Application
from constants import COINMARKET_API

from requests import Session
import json 
from pprint import pprint


#funktion av GET request. GET request data från vår API
def get_latest_coin_data(target_symbol = "XRP"):

    API_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"

    target_symbol = "XRP"

    parameters = {
        'symbol': target_symbol,
        'convert':'USD'
    }

    headers = {
    'Accepts': 'application/json', #Accepts: This header tells the server that the client expects a JSON response.
    'X-CMC_PRO_API_KEY': COINMARKET_API, #X-CMC_PRO_API_KEY: This is an API key used to authenticate the request to the CoinMarketCap API. You must have a valid key to access the API.
    }

    session = Session()
    session.headers.update(headers)

    #Making the API Request
    response = session.get(API_URL, params=parameters) #GET request, ADD URL
    return json.loads(response.text)["data"][target_symbol] #return to JSON

    pprint(data)

#Funktion för vår Application, startar app
#Varje 40de sekund kommer while loopen köras för att se uppdateringar, OM man betalar för API:et
def main():
    app = Application(broker_address="localhost:9092", consumer_group="coin_group")
    coins_topic = app.topic(name = "coins", value_serializer="json")
    #PRODUCER
    with app.get_producer() as producer:
        while True:
            coin_latest = get_latest_coin_data("XRP")


            kafka_message = coins_topic.serialize(
                key=coin_latest["symbol"], value=coin_latest
            )
            
            print(
                f"Produce event with key = {kafka_message.key}, price = {coin_latest['quote']['USD']['price']}"
            )

            producer.produce(
                topic=coins_topic.name, key = kafka_message.key, value = kafka_message.value
            )

            time.sleep(40) 


if __name__ == '__main__':
    # coin_data = get_latest_coin_data()
    # pprint(coin_data)
    main()