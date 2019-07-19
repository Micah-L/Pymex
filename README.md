# PyMEX

A python interface for the BitMEX API. Provided without warranty. Use at your own risk. 

## Getting Started

Before installing, open up __settings__.py and enter your live and/or testnet API key. Some other settings may be adjusted.

### Prerequisites

This program requires bitmex and colorama (if using color). Install everything using install.sh or run the following
```
pip3 install bitmex
pip3 install colorama
```

### Installing

Unless you ran the install.sh file, you will run the following:

```
pip3 install -e .
```


### Running

Run the program by entering 
```
pymex
```
in the command prompt

Type
```
help
```
for a list of commands, and 

```
exit
```
to exit.


The interpreter will default to the live network (using REAL_API_KEY). Run the program with 
```
pymex --testnet
```
to default to testnet.


Once the program is running, you can enter various commands to execute trades or get data. For example 

```
spread --longSym XBTUSD --shortSym XBTU19 --premium 200 --quantity 10000 --wait 5
```
will continually try to sell the XBTU19 futures and buy the XBTUSD swaps only when XBTU19 is trading $200 or more higher than XBTUSD. We will try to get 10000 of them, and keep checking every 5 seconds until we can successfully execute the trade.

### Contributing
Feel free. I don't update this code much anymore.