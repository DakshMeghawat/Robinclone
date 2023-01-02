import json
from flask import Flask, redirect, url_for, request
import pymongo
import requests
#from models import Stock, User

app = Flask(__name__)


class Stock():
    
    def __init__(self,name,sym,nos,value):
        self.name=name
        self.sym=sym
        self.nos=nos
        self.value=value
    
    @classmethod
    def get_instance(cls, d: dict):
        return cls(**d)

    #def getname():
     #   return (name)

class Marketpalce():
    def __init__(self,los):
        self.los=los

class User():
    
    def __init__(self,balance,username,stocks_own):
        self.balance=balance
        self.username=username
        self.stocks_own=stocks_own
        stocks_own=[]

    @classmethod
    def get_instance(cls, d: dict):
        return cls(**d)

    def add_stocks(self,own):
        self.stocks_own.append(own)

myclient = pymongo.MongoClient("mongodb://0.0.0.0:27017/")
mydb = myclient["local"]


# DATABASE FUNCTIONS


def UpdateFund(username,amount):
    mycol=mydb["Users"]
    mycol.find_one_and_update({'username':username},
                        { '$set': { "balance" : amount} })

def CreateUser(user):
    mycol=mydb["Users"]
    x=mycol.insert_one(user.__dict__)


def GetUser(username):
    mycol=mydb["Users"]
    return(mycol.find_one({"username": username},{'_id': False}))
    

def GetStock(sym):
    mycol=mydb["Marketplace"]
    return(mycol.find_one({"sym": sym},{'_id': False }))

def InsertStockInMarket(stock):
    mycol=mydb["Marketplace"]
    #stock_json = json.dumps(stock.__dict__)
    #print(stock_json)
    x=mycol.insert_one(stock.__dict__)

def UpdateStockInMarket(sym,Nvalue):
    mycol=mydb["Marketplace"]
    mycol.find_one_and_update({'sym':sym},
                        { '$set': { "nos" : Nvalue} })

def UpdateBalanceInUser(username,bal):
    mycol=mydb["Users"]
    mycol.find_one_and_update({'username':username},
                        { '$set': { "balance" : bal} })

def CheckIfStockInUser (username,sym):
    mycol=mydb["Users"]
    if (mycol.count_documents({'username':username, 'stocks_own.sym': sym}) > 0) :
        return True
    else:
        return False
            
def AddNewStockInUser(username,stock,sym):
    mycol=mydb["Users"]
    #mycol.find_one_and_update({'username': username}, {'$push': {'stocks_own': stock.__dict__}})
    mycol.update_one({'username': username}, {'$push': {'stocks_own': stock.__dict__}})
    #mycol.insert_one({'username': username}, {'$push': {'stocks_own': stock.__dict__}})

#def RemoveStockInUser(username,sym)


def UpdateStockInUser(username,sym,nos):
    mycol=mydb["Users"]
    mycol.update_one( { 'username': username, 'stocks_own.sym': sym }, { '$set': {"stocks_own.$.nos": nos}})

def RemoveStockInMarket():
    None

# REST API FUNCTIONS

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/withdrawfund", methods = ['POST'])
def WithdrawFundRoute():
    data=request.get_json()
    print(data)
    username=data['username']
    amount=data['amount']
    WithdrawFundM(username,amount)
    return "<p>Hello, World!</p>"

@app.route("/depositfund", methods = ['POST'])
def DepositFundRoute():
    data=request.get_json()
    print(data)
    username=data['username']
    amount=data['amount']
    DepositFundM(username,amount)
    return "<p>Hello, World!</p>"

@app.route("/insertstock", methods = ['POST'])
def InsertStockInMarketRoute():
    data = request.get_json()
    print(data)
    s_3=Stock(name=data['name'], sym=data['sym'], nos=data['nos'],value=data['value'])
    InsertStockInMarket(s_3)
    #return data
    return "<p>Hello, World!</p>"


@app.route("/test", methods=['POST'])
def tst():
    return "<p>Hello, Anshu!</p>"

@app.route("/updatestock", methods=['POST'])
def UpdateStockInMarketRoute():
    data = request.get_json()
    print(data)
    sym=data['sym']
    value=data['value']
    UpdateStockInMarket(sym,value)
    #return data
    return "<p>Hello, World!</p>"

@app.route("/createuser", methods = ['POST'])
def CreateNewUserRoute():
    data = request.get_json()
    print(data)
    U_1=User(username=data['username'], balance=data['balance'],stocks_own=data['stocks'])
    CreateUser(U_1)
    #return data
    return "<p>Hello, World!</p>"

@app.route("/buynewstock", methods = ['POST'])
def BuyNewStockRoute():
    data = request.get_json()
    print(data)
    username=data['username']
    sym=data['sym']
    nos=data['nos']
    BuyNewStock(username,sym,nos)
    return "<p>Hello, World!</p>"

@app.route("/sellstock", methods = ['POST'])
def SellStockRoute():
    data = request.get_json()
    print(data)
    username=data['username']
    sym=data['sym']
    nos=data['nos']
    SellStock(username,sym,nos)
    return "<p>Hello, World!</p>"

@app.route("/showbalanace",methods=['POST'])
def ShowBalanceRoute():
    data = request.get_json()
    username=data['username']
    b=ShowBalanceM(username)
    return "<p> Hello, World!</p>"

@app.route("/Showlist",methods=['POST'])
def ShowListRoute():
    mycol=mydb["Marketplace"]
    cursor=mycol.find({})
    for doc in cursor:
        print(doc)
    return "<p> Hello, World!</p>"
# Middleware Functions


def BuyNewStock(username,sym,nos):
    stock_d = GetStock(sym)
    stock = Stock.get_instance(stock_d)

    user_d = GetUser(username)
    user = User.get_instance(user_d)
    user.balance=user.balance-nos*stock.value
    stock.nos=stock.nos-nos
    UpdateStockInMarket(sym,stock.nos)
    print(stock.nos)
    if(CheckIfStockInUser(username,sym)):
        new_nos = 0
        for stock in user.stocks_own:
            if stock['sym'] == sym:
                new_nos=nos + stock['nos']
        UpdateStockInUser(username,sym,new_nos)
    
    elif not (CheckIfStockInUser(username,sym)):
        print("hello")
        stock.nos=nos
        AddNewStockInUser(username,stock,sym)
   #print(user.stocks_own['sym'])
    #print(user.stocks_own.update('sym':))
    UpdateBalanceInUser(username,user.balance)
    
def SellStock(username,sym,nos):
    stock_d = GetStock(sym)
    stock = Stock.get_instance(stock_d)
    user_d = GetUser(username)
    user = User.get_instance(user_d)
    user.balance=user.balance+nos*stock.value
    stock.nos=stock.nos+nos
    print(stock.nos)
    UpdateStockInMarket(sym,stock.nos)
   # print(user.stocks_own['sym'])
    #print(user.stocks_own.update('sym':))
    if(CheckIfStockInUser(username,sym)):
        new_nos = 0
        for stock in user.stocks_own:
            if stock['sym'] == sym:
                new_nos=stock['nos']-nos
        UpdateStockInUser(username,sym,new_nos)
    
    #stock.nos=user.stocks_own['nos']-nos
    UpdateBalanceInUser(username,user.balance)
    #AddNewStockInUser(username,stock)


def WithdrawFundM(username,amount):
    user_d=GetUser(username)
    user=User.get_instance(user_d)
    user.balance=user.balance-amount
    UpdateFund(user.username,user.balance)

def DepositFundM(username,amount):
    user_d=GetUser(username)
    user=User.get_instance(user_d)
    user.balance=user.balance+amount
    UpdateFund(user.username,user.balance)

def ShowBalanceM(username):
    user_d=GetUser(username)
    user=User.get_instance(user_d)
    print(user.balance)
    return(user.balance)


# Main


def main():
    pass
    #S_1=Stock("APPLE","APL",1000,10)
    
    #S_2=Stock("META","META",1000,20)
    #U_1=User(10000,"Daksh",[])
   # U_1.add_stocks(S_1)
    #U_1.add_stocks(S_2)

    #print(S_2.name)
    #print(U_1.stocks_own[0].name)

    #InsertStockInMarket(S_1)


if __name__=="__main__":
    main()
    app.run(host='0.0.0.0', port=8080)
 