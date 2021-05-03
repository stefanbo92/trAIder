from xAPIConnector import *

# enter your login credentials here
userId = 12188475
password = 'xoh18174'


class MyXTB:
	def __init__(self):
		# create & connect to RR socket
		self.client = APIClient()

	def perform_login(self):
		if self.client == None:
			self.client = APIClient()
		# connect to RR socket, login
		loginResponse = self.client.execute(loginCommand(userId=userId, password=password))
		logger.info(str(loginResponse)) 

		# check if user logged in correctly
		if(loginResponse['status'] == False):
			print('Login failed. Error code: {0}'.format(loginResponse['errorCode']))
			exit()

	def buy_stonks(self):
		print("Buying STONKS!")

		# getting data
		self.perform_login()
		curr_symbol = self.client.execute(baseCommand("getSymbol",dict(symbol="DE30")))
		ask_price = curr_symbol["returnData"]["ask"]
		time_price = curr_symbol["returnData"]["time"]+60000
		print("ask_price for buying",ask_price,"time:",time_price)
		
		# Buy order:
		TRADE_TRANS_INFO_BUY={
			"cmd": 0,
			"customComment": "First transaction",
			"expiration": time_price,
			"offset": 0,
			"order": 0,
			"price": ask_price,
			"sl": 0.0,
			"symbol": "DE30",
			"tp": 0.0,
			"type": 0,
			"volume": 0.05
		}

		# execute buy order
		self.client.execute(baseCommand("tradeTransaction",dict(tradeTransInfo=TRADE_TRANS_INFO_BUY)))

		# logout
		self.client.disconnect()
		self.client = None

	def sell_stonks(self):
		print("Selling STONKS!")
		# getting data
		self.perform_login()
		curr_symbol = self.client.execute(baseCommand("getSymbol",dict(symbol="DE30")))
		ask_price = curr_symbol["returnData"]["ask"]
		time_price = curr_symbol["returnData"]["time"]+60000
		print("ask_price for sell",ask_price,"time:",time_price)

		curr_trades = self.client.execute(baseCommand("getTrades",dict(openedOnly=False)))
		print("curr_trades", curr_trades)
		last_order = 0
		if(len(curr_trades["returnData"])>0):
			last_order = curr_trades["returnData"][0]["order"]
			print("last_order:", last_order)

		# close order
		TRADE_TRANS_INFO_CLOSE={
			"cmd": 1,
			"customComment": "First transaction",
			"expiration": time_price,
			"offset": 0,
			"order": last_order,
			"price": ask_price,
			"sl": 0.0,
			"symbol": "DE30",
			"tp": 0.0,
			"type": 2,
			"volume": 0.05
		}

		# execute close order
		if(last_order>0):
			self.client.execute(baseCommand("tradeTransaction",dict(tradeTransInfo=TRADE_TRANS_INFO_CLOSE)))
		
		# logout
		self.client.disconnect()
		self.client = None
	
	def test_func(self):
		# own stuff
		self.client.execute(baseCommand("getSymbol",dict(symbol="DE30")))
		#self.client.execute(baseCommand("getCurrentUserData"))
		#self.client.execute(baseCommand("getMarginTrade",dict(symbol="DE30", volume=1.0)))
		#self.client.execute(baseCommand("getProfitCalculation",dict(closePrice=15150, cmd=0, openPrice=15000, symbol="DE30",volume=0.05))) # cmd 0->buy, 1->sell
		#self.client.execute(baseCommand("getTradeRecords",dict(orders=[273180485])))
		#self.client.execute(baseCommand("getTradesHistory",dict(end=0, start=time_price-60000000)))
		#curr_time = self.client.execute(baseCommand("getServerTime",dict()))
		#print("curr_time:", curr_time["returnData"]["time"])


my_xtb = MyXTB()
my_xtb.buy_stonks()
time.sleep(5)
my_xtb.sell_stonks()

print("finished xtb api")




'''
Streaming stuff
# get ssId from login response
ssid = loginResponse['streamSessionId']

# create & connect to Streaming socket with given ssID
# and functions for processing ticks, trades, profit and tradeStatus
sclient = APIStreamClient(ssId=ssid, tickFun=procTickExample, tradeFun=procTradeExample, profitFun=procProfitExample, tradeStatusFun=procTradeStatusExample)


# subscribe for trades
sclient.subscribeTrades()

# subscribe for prices
sclient.subscribePrices(['DE30'])

# subscribe for profits
sclient.subscribeProfits()

# this is an example, make it run for 5 seconds
time.sleep(5)

# gracefully close streaming socket
sclient.disconnect()

'''