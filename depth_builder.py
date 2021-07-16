import json
import websocket
import collections


class depthsnapshot:
    def __init__(self):
        self.bids = collections.OrderedDict()
        self.asks = collections.OrderedDict()

    @staticmethod
    def updateitems(items, msgside):
        for item in msgside:
            price = item['Price']
            volume = item['Volume']
            if volume > 0:
                items[price] = volume
            else:
                items.pop(price, None)

    def update(self, msg):
        marketdepth = msg['MarketDepth']
        if not marketdepth['IsUpdate']:
            self.bids.clear()
            self.asks.clear()
        depthsnapshot.updateitems(self.bids, marketdepth['Bids'])
        depthsnapshot.updateitems(self.asks, marketdepth['Asks'])
        #print(max(self.bids), ' ', min(self.asks))


    def printstate(self):
        print('bids ', self.bids)
        print('asks ', self.asks)
        print('bestBid/bestAsk', max(self.bids), ' ', min(self.asks))


symbols = ['XBTUSD@BITMEX', 'BTC-PERP@FTX', 'ETH-PERP@FTX', 'LTCUSDT@BINANCE', 'LTCUSDT@BYBIT']


def on_error(ws, error):
    print(error)


def on_open(ws):
    for symbol in symbols:
        depth = json.dumps({'Message': {'MarketDepth': {'Symbol': symbol}}})
        ws.send(depth)
        ws.send(json.dumps({'Message': {'PublicTrades': {'Symbol': symbol}}}))


depths = {}


def on_message(ws, data):
    msg = json.loads(data)
    if 'MarketDepth' in msg:
        symbol = msg['MarketDepth']['Symbol']
        if not symbol in depths:
            depths[symbol] = depthsnapshot()
        depth = depths[symbol]
        depth.update(msg)
        depth.printstate()
        #print(depth.bids, depth.asks)

    elif 'PublicTrade' in msg:
        print(msg)


ws = websocket.WebSocketApp("ws://ws2.mdlz4.com:5550/", on_message=on_message, on_open=on_open, on_error=on_error)

ws.run_forever()