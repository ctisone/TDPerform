#************
# Imports
#************
from AppArgParser import AppArgParser as ArgParser
from TdaConfig import TdaConfig
import pymongo
from pymongo import MongoClient as MongoClient
from pymongo.collection import Collection as MongoCollection
from tda import auth as TdaAuth
from tda.client import Client as TdaClient
import sys
import datetime
from datetime import datetime as DateTime
from typing import Any, Dict, List


_MONGO_DATABASE = "TdaDatabase"
_MONGO_TRANSACTION_COLLECTION = "TdaTransactions"
_MONGO_POSITION_COLLECTION = "TdaPositions"

def main(cliArgs: List[str]) -> None:
    """  """

    # Parse the command line arguments and find our config file
    parsedCliArgs = ArgParser(cliArgs[1:])
    config = TdaConfig(parsedCliArgs.settingsFileName)

    # Open the database and get the collections we need
    mongoClient = MongoClient(config.mongoConnectionString)
    try:
        mongoDb = mongoClient.get_database(_MONGO_DATABASE)
        transactions = mongoDb.get_collection(_MONGO_TRANSACTION_COLLECTION)
        positions = mongoDb.get_collection(_MONGO_POSITION_COLLECTION)

        # Delete database collections as specified by the command line args
        if(parsedCliArgs.deleteTransactions):
            positions.drop()
            transactions.drop()

        if(parsedCliArgs.deletePositions):
            positions.drop()

        # Get the TDA client and download any needed transactions
        tdaClient = _getTdaClient(config)
        _downloadTransactions(tdaClient, transactions, config)
    finally:
        mongoClient.close()
    return

def _getTdaClient(cfgFile: TdaConfig) -> TdaClient:
    # Use the oAuth token file to establish a secure connection to TD Ameritrade.  If the oAuth file doesn't exist
    # or the key has expired, an exception will be thrown that will display instructions on how to proceed.
    print("Authorizing brokerage connection via {} file settings...".format(cfgFile.oAuthTokenFileName), end="")
    try:
        tdaClient = TdaAuth.client_from_token_file(cfgFile.oAuthTokenFileName, cfgFile.apiKey)
        print("Success!")

    except FileNotFoundError:
        # Because this was written for a headless linux box, there is no way to automatically direct a browser to TD Ameritrade 
        # to run the oAuth authentication process.  This will display instruction to open a browser, go to a link, etc.
        tdaClient = TdaAuth.client_from_manual_flow(cfgFile.apiKey, cfgFile.redirectUri, cfgFile.oAuthTokenFileName,
                                                    asyncio=False, token_write_func=None)
    return(tdaClient)

def _downloadTransactions(tdaClient: TdaClient, transactions: MongoCollection, cfgFile: TdaConfig) -> None:
    """  """

    # Find the lastest transaction date in the collection.  If there are no transaction, we will start with today and go
    # backwards.  Otherwise we will go forwards starting after the latest transaction date.
    response = transactions.find_one(projection=["transactionDate"], sort=[("transactionDate", pymongo.DESCENDING)])
    if (response is None):
        _downloadBackwards(tdaClient, transactions, cfgFile)
    else:
        _downloadForwards(tdaClient, transactions, _convertFromTdaDateTime(response["transactionDate"]), cfgFile)
    return

def _downloadBackwards(tdaClient: TdaClient, transactions: MongoCollection, cfgFile: TdaConfig) -> None:
    # We will download records month by month moving backwards in time, starting with the month we are in.
    # Keep going backwards until we transition a full year without records.
    end = DateTime.now()
    start = DateTime(end.year, end.month, 1)    # 12AM on the first day of the present month
    nullPeriodCounter = 0

    # Keep looping until we get 12 empty time periods (360 days with no transaction data)
    while(nullPeriodCounter < 12):
        # Get the transactions for the window and convert it to a JSON dictionary
        _printTransactionDownloadWindow(start, end)
        response = tdaClient.get_transactions(cfgFile.accountNumber, transaction_type=TdaClient.Transactions.TransactionType.ALL,
                    symbol="", start_date=start, end_date=end)
        jsonData = response.json()
        _printTransactionDownloadCount(len(jsonData))

        # If we hit an empty time period, increment the counter, otherwise reset it and process the data
        if(len(jsonData) == 0):
            nullPeriodCounter = nullPeriodCounter + 1
        else:
            nullPeriodCounter = 0
            _processTdaTransactions(transactions, jsonData)

        # Walk the time window backwards one month
        end = start
        start = _offsetMonth(end, False)
    return

def _downloadForwards(tdaClient: TdaClient, transactions: MongoCollection, lastTransactionTime: DateTime, cfgFile: TdaConfig) -> None:
    # Starting at the last transaction time, download transactions month by month moving forward in time until we cross today
    start = lastTransactionTime
    if(start.month == 12):
        end = DateTime(start.year + 1, 1, 1)    # 12AM on the first day of the next month
    else:
        end = DateTime(start.year, start.month + 1, 1)

    now = DateTime.now()
    while(True):
        # Get the transactions for the window and convert it to a JSON dictionary
        _printTransactionDownloadWindow(start, end)
        response = tdaClient.get_transactions(cfgFile.accountNumber, transaction_type=TdaClient.Transactions.TransactionType.ALL,
                    symbol="", start_date=start, end_date=end)
        jsonData = response.json()
        _printTransactionDownloadCount(len(jsonData))

        # If there are transactions in the window process them
        if(len(jsonData) > 0):
             _processTdaTransactions(transactions, jsonData)

        # If the end time includes now, we are done.  Otherwise, advance the time one month
        if(end > now):
            break
        else:
            start = end
            end = _offsetMonth(end, True)
    return

def _processTdaTransactions(transactions: MongoCollection, jsonData: List[Dict]) -> None:
    return

def _convertFromTdaDateTime(tdaDateTime: str) -> DateTime:
    # TDA date/time format is 2022-01-06T10:09:40+0000 (+0000 is in milliseconds).  Convert to a proper ISO 8601 string before
    # giving it to the DateTime object (2022-01-06T10:09:40.000000, where decimal is in microseconds)
    timeList = tdaDateTime.split("+")
    iso8601 = "{}.{:06d}".format(timeList[0], int(timeList[1]) * 1000)
    return(DateTime.fromisoformat(iso8601))

def _offsetMonth(date: DateTime, advance: bool) -> DateTime:
    if(advance):
        if(date.month == 12):                               # If December
            result = DateTime(date.year + 1, 1, 1)          # Next month is January of the next year
        else:
            result = DateTime(date.year, date.month + 1, 1) # Otherwise just increment the month  
    else:
        if(date.month == 1):                                # If January
            result = DateTime(date.year - 1, 12, 1)         # Previous month is December of the previous year
        else:
            result = DateTime(date.year, date.month - 1, 1) # Otherwise just decrement the month  
    return(result)

def _printTransactionDownloadWindow(start: DateTime, end: DateTime) -> None:
    print("Downloading records for {}...".format(start.strftime("%B %Y")), end="")
    return

def _printTransactionDownloadCount(count: int) -> None:
    print("{} record{} downloaded".format(count, "" if (count == 1) else "s"))
    return

if __name__ == "__main__":
    main(sys.argv)