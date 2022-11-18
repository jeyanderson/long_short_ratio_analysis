import ccxt
from math import floor
binance=ccxt.binance({
            "apiKey":'apiKey',
            "secret":'apiSecret',
        })
bybit=ccxt.bybit({
            "apiKey":'apiKey',
            "secret":'apiSecret',
            "options": {'defaultType': 'future' }
        })
symbols=['LINKUSDT','MATICUSDT','ETHUSDT','DOGEUSDT','APTUSDT','ATOMUSDT','DOTUSDT','FTMUSDT','BTCUSDT','SUSHIUSDT','UNIUSDT']
tf='5m'
validRatio=0
netSizes=[]
data=[]
ratios=[]
for i,symbol in enumerate(symbols):
    # bybit.set_leverage(2,symbol)
    orders=bybit.fetch_open_orders(symbol)
    if len(orders):
        bybit.cancel_order(int(orders[0]['info']['id']),symbol)
    position=bybit.fetch_positions([symbol])
    netSize=float(position[0]['info']['size'])
    netSize=netSize if netSize else float(position[1]['info']['size'])*-1
    netSizes.append(netSize if netSize else None)
    positionSide=0
    if netSizes[i]:
        if netSizes[i]<0:
            positionSide=-1
        elif netSizes[i]>0:
            positionSide=1
        netSizes[i]=abs(netSizes[i])
    data.append(binance.fapiDataGetTopLongShortPositionRatio({'symbol':symbol,'period':tf}))
    ratios.append(float(data[i][-1]['longShortRatio']))
    ratio=ratios[i]
    print(ratio)
    if positionSide==0:
        if ratio>=1.15:
            validRatio+=1
        elif ratio<=.85:
            validRatio+=1
    if ratio<1.05 and positionSide==-1:
        bybit.create_market_buy_order(symbols[i],netSizes[i],params={'reduce_only':True})
    elif ratio>.95 and positionSide==1:
        bybit.create_market_sell_order(symbols[i],netSizes[i],params={'reduce_only':True})
if validRatio:
    for i,symbol in enumerate(symbols):
        ratio=ratios[i]
        netSize=netSizes[i]
        if not netSize:
            balance=bybit.fetch_balance()
            balance=float(balance['USDT']['free'])
            portion=floor(balance/validRatio)
            if ratio>=1.15:
                price=bybit.fetch_ticker(symbols[i])
                price=float(price['ask'])
                size=float(bybit.amount_to_precision(symbols[i],portion/price))
                bybit.create_limit_sell_order(symbols[i],size,price)
            elif ratio<=.85:
                price=bybit.fetch_ticker(symbols[i])
                price=float(price['ask'])
                size=float(bybit.amount_to_precision(symbols[i],portion/price))
                bybit.create_limit_buy_order(symbols[i],size,price)
