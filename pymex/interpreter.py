######################################################################################
#@@@@@@@@@@@@@@@@@@@@@##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
#@@@@@@  PyMEX  @@@@@@##@@@@@@@@@@@@@@@@@@@        By: Me         @@@@@@@@@@@@@@@@@@@#
#@@@@@@@@@@@@@@@@@@@@@##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
######################################################################################
import argparse, bitmex, time, json
import __settings__
from bravado import exception
from colorama import init, Fore, Back, Style
init()
LAST_ORDER_ID = ""
LAST_LINK_ID = ""
RATE_LIMIT = 300
RESULT = ""
######################################################################################
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
#@@@@@                         	 	PyMEX 1.0      	                            @@@@@#
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
######################################################################################
class interpreter:
	def __init__(self, verbose = __settings__.verbose, testnet=__settings__.testnet):
		self.CONFIG_VARS = {}
		#include everything else in __settings__
		for x in __settings__.__dict__:
			if x[0:2] != "__":
				self.CONFIG_VARS[x] = __settings__.__dict__[x]
	
		self.client = bitmex.bitmex(test=self.CONFIG_VARS['testnet'], 
									api_key=self.CONFIG_VARS['TEST_API_KEY'] if self.CONFIG_VARS['testnet'] else self.CONFIG_VARS['REAL_API_KEY'], 
									api_secret=self.CONFIG_VARS['TEST_API_SECRET'] if self.CONFIG_VARS['testnet'] else self.CONFIG_VARS['REAL_API_SECRET'])
		self.cparser = argparse.ArgumentParser(prog = "")
		self.subparsers = self.cparser.add_subparsers()
		
		##### Change settings #####
		self.p_network = self.subparsers.add_parser('network', help='Change between live and testnet')
		self.p_networks = self.p_network.add_mutually_exclusive_group(required=True)
		self.p_networks.add_argument('--test','--testnet', action='store_true', default=False)
		self.p_networks.add_argument('--live', action='store_true', default=False)
		self.p_network.set_defaults(func=self.set_network)
		self.p_vars = self.subparsers.add_parser('vars',help='Display some variables')
		self.p_vars.set_defaults(func=self.vars)
		self.p_set = self.subparsers.add_parser('set')
		self.p_set.add_argument("variable",type=str,help="Valid options: " + ", ".join(self.CONFIG_VARS.keys()))
		self.p_set.add_argument("value", type=str)
		self.p_set.set_defaults(func=self.setVar)
		#####
		
		##### Single Commands #####
		self.p_do_nothing = self.subparsers.add_parser('do_nothing')
		self.p_do_nothing.set_defaults(func=self.do_nothing)
		
		self.p_cancel_last = self.subparsers.add_parser('cancel_last',help="Cancel the last order")
		self.p_cancel_last.set_defaults(func=self.cancel_last)
		
		self.p_cancel_last_group = self.subparsers.add_parser('cancel_last_group', help="Cancel the last group of orders, by clOrdLinkID")
		self.p_cancel_last_group.set_defaults(func=self.cancel_last_group)
		
		self.p_cancel_all = self.subparsers.add_parser('cancel_all',help="Cancel all open orders")
		self.p_cancel_all.add_argument("--symbol", "-s",type=str,help="Optionally only cancels orders from SYMBOL")
		self.p_cancel_all.set_defaults(func=self.cancel_all)
		
		self.p_test = self.subparsers.add_parser('test')
		self.p_test.set_defaults(func=self.test)
		
		#####
		
		##### Create a new order #####
		self.p_order_new = self.subparsers.add_parser('new', help='Place a new order')
		self.p_order_new.add_argument("--symbol",'-s',type=str, help='XBTUSD, XBTU17, etc...')
		self.p_order_new.add_argument("--clOrdLinkID",'-lID',type=str, help='Order ID')
		self.p_order_new.add_argument("--clOrdID",'-cloID',type=str, help='Optional Client Order ID')
		self.p_order_new.add_argument("--simpleOrderQty",'--simpleQty', type=float, help='Optional order quantity in units of the underlying instrument (i.e. Bitcoin).')
		self.p_order_new.add_argument("--orderQty", "--quantity", '-q',type=int,help="Optional order quantity in units of the instrument (i.e. contracts).")
		self.p_order_new.add_argument("--price",'-p',type=float, help="Optional limit price for 'Limit', 'StopLimit', and 'LimitIfTouched' orders.")
		self.p_order_new.add_argument("--stopPx", "--stop",type=float, help="Optional trigger price for 'Stop', 'StopLimit', 'MarketIfTouched', and 'LimitIfTouched' orders. Use a price below the current price for stop-sell orders and buy-if-touched orders.")
		self.p_order_new.add_argument("--pegOffsetValue","--trail",type=float, help="Optional trailing offset from the current price for 'Stop', 'StopLimit', 'MarketIfTouched', and 'LimitIfTouched' orders; use a negative offset for stop-sell orders and buy-if-touched orders. Optional offset from the peg price for 'Pegged' orders.")
		self.p_order_new.add_argument("--pegPriceType",choices=['LastPeg', 'MidPricePeg', 'MarketPeg', 'PrimaryPeg', 'TrailingStopPeg'], help="Optional peg price type.")
		self.p_order_new.add_argument("--timeInForce", choices=['Day', 'GoodTillCancel', 'ImmediateOrCancel', 'FillOrKill'], help="Time in force. Defaults to 'GoodTillCancel' for 'Limit', 'StopLimit', 'LimitIfTouched', and 'MarketWithLeftOverAsLimit' orders.")
		self.p_order_new.add_argument("--ordType", choices=['Limit','Market','MarketWithLeftOverAsLimit','Stop','StopLimit','MarketIfTouched','LimitIfTouched'], help="")
		self.p_order_new.add_argument("--text", '-t', type=str, help="Optional amend annotation. e.g. 'Adjust skew'.")
		self.p_order_new.add_argument("--displayQty", '-dq', type=int, help="Optional quantity to display in the book. Use 0 for a fully hidden order.")
		
		self.p_order_new.add_argument("--execInst", nargs='*', help="Optional execution instructions")
		self.p_order_new.add_argument("--PostOnly", action='append_const', const='ParticipateDoNotInitiate', dest='execInst')
		self.p_order_new.add_argument("--AllOrNone`", action='append_const', const='AllOrNone', dest='execInst')
		self.p_order_new.add_argument("--MarkPrice`", action='append_const', const='MarkPrice', dest='execInst')
		self.p_order_new.add_argument("--IndexPrice`", action='append_const', const='IndexPrice', dest='execInst')
		self.p_order_new.add_argument("--LastPrice`", action='append_const', const='LastPrice', dest='execInst')
		self.p_order_new.add_argument("--Close", action='append_const', const='Close', dest='execInst')
		self.p_order_new.add_argument("--ReduceOnly", action='append_const', const='ReduceOnly', dest='execInst')
		self.p_order_new.add_argument("--Fixed", action='append_const', const='Fixed', dest='execInst')
		
		self.p_order_new.add_argument("--contingencyType", choices=['OneCancelsTheOther', 'OneTriggersTheOther', 'OneUpdatesTheOtherAbsolute', 'OneUpdatesTheOtherProportional'], help="Optional contingency type for use with clOrdLinkID.")
		self.p_order_new.add_argument("--oco", action='store_const',dest='contingencyType',const='OneCancelsTheOther',help="One Order Cancels the Other")
		self.p_order_new.add_argument("--oto", action='store_const',dest='contingencyType',const='OneTriggersTheOther',help="One Order Triggers the Other")
		self.p_order_new.add_argument("--ouoa", action='store_const',dest='contingencyType',const='OneUpdatesTheOtherAbsolute',help="One Order Updates the Other Absolute")
		self.p_order_new.add_argument("--ouop", action='store_const',dest='contingencyType',const='OneUpdatesTheOtherProportional',help="One Order Updates the Other Proportional")
		self.p_order_new.set_defaults(func=self.order_new)
		#####
		
		
		##### Place an order with exit and stoploss #####
		self.p_target = self.subparsers.add_parser('enter', help="Enter a position with a predefined target and stop loss")
		self.p_target.add_argument("--target", '-t', type=float, help="Price to take profits")
		self.p_target.add_argument("--stop", '-sm', type=float, help="Price to stop losses")
		self.p_target.add_argument("--trail", '-st', type=float, help="Use to set a trailing stop")
		self.p_target.add_argument("--limit", '-l', type=float, help="Optionally set the entry as a limit order")
		self.p_target.add_argument("--enter", '-e', type=float, help="Optionally set the entry as a stop market order")
		self.p_target.add_argument("--symbol", '-sym','-s', type=str, help='XBTUSD, XBTU17, etc...')
		self.p_target.add_argument("--quantity", '-q',type=int,help="Quantity", required=True)
		self.p_target.add_argument("--ExitOnly",action='store_true',help="Skip the entry order")
		self.p_target.add_argument("--test",action='store_true',help="Do not execute orders")
		self.p_target.add_argument("--LastPrice",action='store_true',help="Stop order triggers on last price")
		self.p_target.add_argument("--IndexPrice",action='store_true',help="Stop order triggers on index price")
		self.p_target.add_argument("--MarkPrice",action='store_true',help="Stop order triggers on mark price")
		self.p_target.set_defaults(func=self.target)
		#####
			
		##
		self.p_spread = self.subparsers.add_parser('spread',help="Execute a long and short position simultaneuously")
		self.p_spread.add_argument("--longSym",'-b',type=str,help="Symbol to long",required=True)
		self.p_spread.add_argument("--shortSym",'-s',type=str,help="Symbol to short",required=True)
		self.p_spread.add_argument("--premium",'-p',type=float,help="Minimum premium to obtain")
		self.p_spread.add_argument("--quantity",'-q',type=int,help="Quantity")
		self.p_spread.add_argument("--wait",'-w',type=int,help="Wait time (seconds)")
		self.p_spread.set_defaults(func=self.spread)
		#
		
	def test(self,args):
		btcprice = self.client.Instrument.Instrument_get(symbol="XBTUSD").result()[0][0]['markPrice']

		print("XBTUSD: " + str(btcprice))
		
	def set_network(self,args):
		if args.live:
			self.CONFIG_VARS['testnet'] = False	
			self.client = bitmex.bitmex(test=False, api_key=self.CONFIG_VARS['REAL_API_KEY'], api_secret=self.CONFIG_VARS['REAL_API_SECRET'])
		if args.test:
			self.CONFIG_VARS['testnet'] = True
			self.client = bitmex.bitmex(test=True, api_key=self.CONFIG_VARS['TEST_API_KEY'], api_secret=self.CONFIG_VARS['TEST_API_SECRET'])
	def vars(self,args):
		for x in self.CONFIG_VARS.keys():
			self.vprint(-2, x + " = " + str(self.CONFIG_VARS[x]))		
		self.vprint(1,"RESULT = " + str(RESULT))
		self.vprint(1,"RateLimit Remaining: " + str(RATE_LIMIT) + "\nOrder ID: " + LAST_ORDER_ID + "\nLink ID: " + LAST_LINK_ID)
	def setVar(self,args):
		if args.variable not in self.CONFIG_VARS.keys():
			self.vprint(2, "Variable not valid: " + args.variable + ".\nChoose from: " + ", ".join(self.CONFIG_VARS.keys()))
			return
		if type(self.CONFIG_VARS[args.variable]) is str:
			self.vprint(2,"Setting string variable")
			self.CONFIG_VARS[args.variable] = args.value
		elif type(self.CONFIG_VARS[args.variable]) is int:
			self.vprint(2,"Setting int variable")
			self.CONFIG_VARS[args.variable] = int(args.value)
		elif type(self.CONFIG_VARS[args.variable]) is bool:
			self.vprint(2,"Setting bool variable")
			self.CONFIG_VARS[args.variable] = True if args.value.lower() == "true" else False	
			
	def do_nothing(self,args):
		return None
	def cancel_last(self,args):
		global RESULT
		RESULT = self.client.Order.Order_cancel(orderID = LAST_ORDER_ID).result()
	def cancel_last_group(self,args):
		global RESULT
		result = self.client.Order.Order_getOrders(filter='{"clOrdLinkID" : "' + LAST_LINK_ID + '"}').result()
		self.vprint(3,result)
		for x in result[0]:
			self.vprint(2,x['orderID'])
			RESULT = self.client.Order.Order_cancel(orderID = x['orderID']).result()
	def cancel_all(self,args):
			global RESULT
			if args.symbol is None:
				RESULT = self.client.Order.Order_cancelAll().result()
			else:
				RESULT = self.client.Order.Order_cancelAll(symbol=args.symbol.upper()).result()
				
	def order_new(self,args):
		order = {}
		args.symbol = self.CONFIG_VARS['default_symbol'] if args.symbol is None else args.symbol.upper()
		for x in vars(args):
			if isinstance(vars(args)[x], list):
				order[x] = ", ".join(str(y) for y in vars(args)[x])        
			elif x in __settings__.__sample_order__.keys():
				if vars(args)[x] is not None:
					order[x] = vars(args)[x]
		self.vprint(1,json.dumps([order]))
		self.order_bulk(orders=[order])
		return None
	def order_bulk(self,orders):
		try:
			try:
				result = self.client.Order.Order_newBulk(orders=json.dumps(orders)).result()
			except exception.HTTPTooManyRequests:
				self.vprint(1,"HTTPTooManyRequests\nSleeping for " + str(self.CONFIG_VARS['sleeptime_HTTPTooManyRequests']) + " seconds...")
				time.sleep(self.CONFIG_VARS['sleeptime_HTTPTooManyRequests'])
				return self.order_bulk(orders)
			except exception.HTTPServiceUnavailable:
				self.vprint(1,"HTTPServiceUnavailable\nSleeping for " + str(self.CONFIG_VARS['sleeptime_HTTPServiceUnavailable']) + " seconds...")
				time.sleep(self.CONFIG_VARS['sleeptime_HTTPServiceUnavailable'])	
				return self.order_bulk(orders)
		except KeyboardInterrupt:
			return None
		global RESULT, RATE_LIMIT, LAST_LINK_ID, LAST_ORDER_ID
		RESULT = result
		self.vprint(4,json.dumps(orders,indent=2))
		self.vprint(3,str(result))
		RATE_LIMIT = result[1].headers['X-RateLimit-Remaining']
		#try:
		#	LAST_ORDER_ID = result[0]['orderID']
		#	LAST_LINK_ID = result[0]['clOrdLinkID'] if result[0]['clOrdLinkID'] is not '' else LAST_LINK_ID
		#	message = result[0]['side'] + " " + str(result[0]['orderQty']) + " " + result[0]['symbol'] + " at " + str(result[0]['price']) + " " + result[0]['currency']
		#except TypeError:
		#self.vprint(5,"TypeError in self.order_bulk")
		LAST_ORDER_ID = result[0][0]['orderID']
		LAST_LINK_ID = result[0][0]['clOrdLinkID'] if result[0][0]['clOrdLinkID'] is not '' else LAST_LINK_ID
		message = result[0][0]['side'] + " " + str(result[0][0]['orderQty']) + " " + result[0][0]['symbol'] + " at " + str(result[0][0]['price']) + " " + result[0][0]['currency']
		
		self.vprint(3,"RateLimit Remaining: " + RATE_LIMIT + "\nOrder ID: " + LAST_ORDER_ID + "\nLink ID: " + LAST_LINK_ID + "\n")
		self.vprint(1,message)	
		return None
		
	def target(self,args):
		self.vprint(2,args)
		orders = []
		linkID = "Current Time: " + str(time.monotonic())
		args.symbol = self.CONFIG_VARS['default_symbol'] if args.symbol is None else args.symbol.upper()
		if args.ExitOnly is False:
			entry = {}
			entry['symbol'] = args.symbol
			entry['clOrdLinkID'] = linkID
			entry['orderQty'] = args.quantity
			if args.limit is not None:
				entry['price'] = args.limit
			if args.stop is not None or args.trail is not None or args.target is not None:
				entry['contingencyType'] = 'OneTriggersTheOther'
			if args.enter is not None: ##entry order is stop
				tickprice = 'IndexPrice' if args.IndexPrice else 'LastPrice' if args.LastPrice else 'MarkPrice' if args.MarkPrice else self.CONFIG_VARS['default_stop_inst']
				entry['execInst'] = tickprice
				entry['stopPx'] = args.enter
				if args.limit is None:
					entry['ordType'] = 'Stop' 
				else:
					entry['ordType'] = 'StopLimit'
			orders.append(entry)
		target = {}
		stop = {}
		if (args.stop is not None) or (args.trail is not None):
			stop['symbol'] = args.symbol
			stop['clOrdLinkID'] = linkID
			stop['orderQty'] = -1*args.quantity
			if args.target is not None:
				stop['contingencyType'] = 'OneUpdatesTheOtherAbsolute'
				target['contingencyType'] = 'OneUpdatesTheOtherAbsolute'
			tickprice = 'IndexPrice' if args.IndexPrice else 'LastPrice' if args.LastPrice else 'MarkPrice' if args.MarkPrice else self.CONFIG_VARS['default_stop_inst']
			stop['execInst'] = 'Close, ' + tickprice
			if args.stop is not None:
				stop['stopPx'] = args.stop
			elif args.trail is not None:
				stop['pegPriceType'] = 'TrailingStopPeg'
				stop['pegOffsetValue'] = args.trail
			stop['ordType'] = 'Stop'
			orders.append(stop)
		if args.target is not None:
			target['symbol'] = args.symbol
			target['clOrdLinkID'] = linkID
			target['orderQty'] = -1*args.quantity
			target['price'] = args.target
			target['clOrdLinkID'] = linkID
			target['execInst'] = 'Close'
			orders.append(target)
		if args.test:
			self.vprint(1,json.dumps(orders,indent=2))
			quotePrice = args.enter if args.enter is not None else args.limit if args.limit is not None else self.quote(symb=args.symbol,quantity=abs(args.quantity))[0] if args.quantity > 0 else self.quote(symb=args.symbol,quantity=abs(args.quantity))[1]
		if args.symbol[3:6] is 'XBT':
			if args.stop is not None:
				self.vprint(1,"Max Loss:\t" + str(abs(args.quantity*(args.stop-quotePrice))))
			if args.target is not None:
				self.vprint(1,"Max Profit:\t" + str(abs(args.quantity*(args.target-quotePrice))))
		if args.test:
			return None
		self.order_bulk(orders=orders)	
		
	def spread(self,args):
		self.vprint(1,"Spread trader")
		self.vprint(1,"Buying " + str(args.quantity) + " of " + args.longSym)
		self.vprint(1,"Selling " + str(args.quantity) + " of " + args.shortSym)
		self.vprint(4,"*******************************************************")
		quote_short = self.quote(args.shortSym,args.quantity)
		self.vprint(4,args.shortSym + " " + str(quote_short))
		quote_long = self.quote(args.longSym,args.quantity)
		self.vprint(4,args.longSym + " " + str(quote_long))
		prem = quote_short[1] - quote_long[0]
		self.vprint(1,"Current premium collected: " + str(prem))
		self.vprint(1,"Minimum premium before collecting: " + str(args.premium))
		while(args.premium is None or args.premium > prem):
			try:
				if args.wait is not None:
					time.sleep(args.wait)
				else:
					time.sleep(self.CONFIG_VARS['sleeptime'])
				quote_short = self.quote(args.shortSym,args.quantity)
				self.vprint(4,args.shortSym + " " + str(quote_short))
				quote_long = self.quote(args.longSym,args.quantity)
				self.vprint(4,args.longSym + " " + str(quote_long))
				prem = quote_short[1] - quote_long[0]
				self.vprint(1,"Current premium collected: " + str(prem))
				self.vprint(1,"Minimum premium before collecting: " + str(args.premium))
			except KeyboardInterrupt:
				self.vprint(1,"Canceling...")
				return
				break
		orders = [{"symbol": args.longSym.upper(), "orderQty": args.quantity}, {"symbol": args.shortSym.upper(), "orderQty": -1*args.quantity}]
		self.vprint(1,"Minimum requirement met. Executing\n" + json.dumps(orders,indent=2))
		self.order_bulk([orders[0]])
		buyprice = RESULT[0][0]['avgPx']
		self.order_bulk([orders[1]])
		sellprice = RESULT[0][0]['avgPx']
		self.vprint(1, "Premium obtained: " + str(sellprice - buyprice))
	def quote(self,symb,quantity,defaultCount=50):
		global RESULT
		symb = symb.upper()
		self.vprint(1,"Quoting " + symb + " x" + str(quantity))
		buyCost = 0
		buyAmt = 0
		sellCost = 0
		sellAmt = 0
		try:
			result = self.client.OrderBook.OrderBook_getL2(symbol=symb, depth=defaultCount).result()
			RESULT = result
		except exception.HTTPTooManyRequests:
			self.vprint(2,"HTTPTooManyRequests\nSleeping for " + str(self.CONFIG_VARS['sleeptime_low_rate_limit']) + " seconds.")
			time.sleep(self.CONFIG_VARS['sleeptime_low_rate_limit'])
			return self.quote(symb=symb,quantity=quantity)
		except exception.HTTPServiceUnavailable:
			self.vprint(2,"HTTPServiceUnavailable\nSleeping for " + str(self.CONFIG_VARS['sleeptime_low_rate_limit']) + " seconds.")
			time.sleep(self.CONFIG_VARS['sleeptime_low_rate_limit'])
			return self.quote(symb=symb,quantity=quantity)
		result = result[0]
		firstBuy = 0
		while(result[firstBuy]['side'] == 'Sell'):
			firstBuy += 1
		i=firstBuy - 1
		self.vprint(3,symb + " " + str(result[i]))
		while(buyAmt < quantity):
			buy = min(result[i]['size'],quantity-buyAmt)
			buyAmt += buy
			buyCost += buy*result[i]['price']
			i -= 1
		i=firstBuy
		self.vprint(3,symb + " " + str(result[i]))
		while(sellAmt < quantity):
			sell = min(result[i]['size'],quantity-sellAmt)
			sellAmt += sell
			sellCost += sell*result[i]['price']
			i += 1
		return (buyCost/quantity,sellCost/quantity)
	def i(self,input):
		self.interpret(input)
	def interpret(self,input): 
		if input is None:
			return
		elif (input == "help" or input == ""):
			self.cparser.print_help()
		elif isinstance(input, str):
			try:
				args = self.cparser.parse_args(input.split())
				multi = args.func(args)
				try:
					self.interpret(multi)
				except SystemExit:
					return None
			except SystemExit:
				return None		
		elif(input == "help" or input == ""):
			self.cparser.print_help()
	def vprint(self,level, stuff,addColor=True):
		if self.CONFIG_VARS['verbose'] >= level:
			if level == 4:
				print(Fore.YELLOW + str(stuff) + Fore.RESET if addColor else str(stuff))				
			elif level == 3:
				print(Fore.MAGENTA + str(stuff) + Fore.RESET if addColor else str(stuff))
			elif level == 2:
				print(Fore.RED + str(stuff) + Fore.RESET if addColor else str(stuff))
			elif level == 1:
				print(Fore.GREEN + str(stuff) + Fore.RESET if addColor else str(stuff))
			else: 
				print(Fore.GREEN + str(stuff) + Fore.RESET if addColor else str(stuff))