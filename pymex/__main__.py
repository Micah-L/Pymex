######################################################################################
#@@@@@@@@@@@@@@@@@@@@@##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
#@@@@@@@ PyMEX @@@@@@@##@@@@@@@@@@@@@@@@@@@        By: Me         @@@@@@@@@@@@@@@@@@@#
#@@@@@@@@@@@@@@@@@@@@@##@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
######################################################################################
import sys, argparse, json, time, bitmex
from colorama import init, Fore, Back, Style
init()
#Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.
#Style: DIM, NORMAL, BRIGHT, RESET_ALL
import pymex.interpreter as interpreter
import __settings__

def main():
	parser = argparse.ArgumentParser(description='BitMex Python Interface')
	parser.add_argument('--test', action='store_true', default=False, help='Use BitMex testnet')
	parser.add_argument('--verbose','-v',type=int,help='-1=silent, 0=normal, 1=extra info, 2=debug')
	args = parser.parse_args()
	print(str(args))
	message = Fore.GREEN + "Testnet" + Fore.RESET if args.test else Fore.MAGENTA + "Live Trading" + Fore.RESET
	print("Connecting to " + Fore.RED + "Bit" + Fore.BLUE + "MEX " + message)
	global interp
	interp = interpreter.interpreter(verbose=args.verbose if args.verbose is not None else __settings__.verbose,testnet=args.test if args.test is not None else __settings__.testnet)
	interactive()
def interactive():
	print(Fore.MAGENTA + Style.BRIGHT + "\n\nWelcome" + Fore.GREEN, end='')
	user_input = "do_nothing"
	while(user_input != "exit"):
		interp.i(user_input)
		print(Fore.MAGENTA + Style.BRIGHT + "\n\n>>>" + Fore.GREEN, end='')
		try:
			user_input = input(" ")
		except KeyboardInterrupt:
			try:
				print(Fore.YELLOW + Style.BRIGHT + "Exit? (Y/n): " + Style.RESET_ALL ,end='')
				user_input = input(" ")
				user_input = "exit" if user_input.lower()[0] is 'y' else "do_nothing"
			except KeyboardInterrupt:
				user_input = "do_nothing"
	print("Good bye ;)")
if __name__ == '__main__':
	main()