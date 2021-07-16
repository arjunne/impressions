import logging, os, boto3, json, datetime
from fastapi import FastAPI, Request, Response, HTTPException
from models import TradeType, Strategy
from db import dynamodbcrud
import random, string
from models.search import TradeSearch
from mangum import Mangum

log_level=os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=logging.INFO)
LOG=logging.getLogger()
LOG.setLevel(log_level)

TABLE = os.getenv('DYNAMODB_TABLE', 'impressions')


app = FastAPI(docs_url="/impressions/docs", openapi_url="/impressions/api/v1/openapi.json", root_path="/v1/")


def id_generator(size=4, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

today = datetime.datetime.today().strftime('%Y-%b-%d')
day_of_the_week = datetime.datetime.today().strftime('%A')
pk = datetime.datetime.today().strftime('%d%m%Y')


handler = Mangum(app)


@app.post("/add/trades")
async def add_trades(tradetype: TradeType, strategy: Strategy, lots:int, ce_entry_price:float, ce_exit_price:float, pe_entry_price:float, pe_exit_price:float):
    response_item = dict()
    response_item['date'] = today
    response_item['lots'] = lots
    profit = ((ce_entry_price - ce_exit_price) + (pe_entry_price - pe_exit_price))
    if tradetype == 'Nifty':
        response_item['instrument'] = tradetype.nifty
        response_item['profit_per_lot'] = profit * 50
        profit = profit * lots * 50
        response_item['total_profit'] = profit
        if strategy == strategy.first:
            response_item['id'] = f'{pk}#nf1'
        else:
            response_item['id'] = f'{pk}#nf2'
    else:
        response_item['instrument'] = tradetype.banknifty
        response_item['profit_per_lot'] = profit * 25
        profit = profit * lots * 25
        response_item['total_profit'] = profit
        if strategy == strategy.second:
            response_item['id'] = f'{pk}#bnf1'
        else:
            response_item['id'] = f'{pk}#bnf2'


    response_item['day'] = day_of_the_week
    LOG.info(type(response_item))

    try:
        dynamodbcrud.put_item(TABLE, item=response_item)
        return response_item
        print(response_item)
    except Exception as e:
        return e

@app.get("/trades/search")
async def search_trades(id):
    item = {'tracker_id': id}
    try:
        get_trade = dynamodbcrud.get_item(TABLE, item=item)
        return get_trade
    except Exception as e:
        return e