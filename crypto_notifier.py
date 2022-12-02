""""
    Just a simple price notifier that sends out emails.

    Uses Kucoins API to get current prices from Kucoin
    If it hits a certain percentage/threshold it
    sends an email to your email or a phone #.
    
    Future implementations: 
    
    (1) Code cleanup
    
    (2) After a certain amount of time
    or after a newer low point make that the initial price then
    compare to the current price.
    
    (3) Implement algorithmic paper trades.

    (4) Get 24 hour chart price and get the percentage gains/loss of current price

    (5) More functions...
    
    https://python-kucoin.readthedocs.io/en/latest/overview.html#register-on-kucoin
    https://docs.kucoin.com/#general"""

import smtplib
import secretInfo
import base64
import hmac
import hashlib
import time
from datetime import datetime
from requests import Session

#Global variables

ticker = "BTC-USDT"

    
class CMC:
    def __init__(self, token):
        
        #   Defining URL

        self.url = 'https://api.kucoin.com'
        self.now = int(time.time() * 1000)
        self.str_to_sign = str(self.now) + 'GET' + '/api/v1/accounts'

        # Signing 

        self.signature = base64.b64encode(hmac.new(secretInfo.API_SECRET.encode('utf-8'), self.str_to_sign.encode('utf-8'), hashlib.sha256).digest())

        self.passphrase = base64.b64encode(hmac.new(secretInfo.API_SECRET.encode('utf-8'), secretInfo.API_PASSWORD.encode('utf-8'), hashlib.sha256).digest())

        self.headers = {
            "KC-API-SIGN": self.signature,
            "KC-API-TIMESTAMP": str(self.now),
            "KC-API-KEY": secretInfo.API_KEY,
            "KC-API-PASSPHRASE": secretInfo.API_PASSWORD,
            "KC-API-KEY-VERSION": "2"
        }

        # Making a session so I can just add the end points to whatever functions

        self.session = Session()
        self.session.headers.update(self.headers)

    def getInitialPrice(self):

        #Getting the response

        url = self.url + f"/api/v1/market/orderbook/level1?symbol={ticker}"
        
        price = float(self.session.get(url).json()['data']['price'])

        print("getBitcoin() Initial price: " + str(price) +"\n")

        return price
        

    def getCurrentPrice(self):

        #Getting the response

        url = self.url + f"/api/v1/market/orderbook/level1?symbol={ticker}"

        currentPrice = float(self.session.get(url).json()['data']['price'])

        print("getCurrentPrice() Current Price " + str(currentPrice))

        return currentPrice
                

def sendEmail(currentPrice, perc):
    
    email = secretInfo.GMAIL                    # your email
    password = secretInfo.G_PASS                # IF 2FA then input your generated email application password
    host = 'smtp.gmail.com'                     # SMTP server of your email provider
    port = '587'                                # SMTP port
    rcpt = secretInfo.RCPT

    if currentPrice > 0:
        trend = "up"
    else:
        trend = "down"

    # https://stackoverflow.com/questions/35624537/how-to-remove-x-cmae-envelope-from-php-mail
    # Helps remove the X-CMAE-Envelope when adding a colon ":", sending from gmail to a verizon phone #
    
    message = (f"\r\n\r\n{ticker} has gone {trend} at least {perc}% current price: " + str(currentPrice) + "\r\n\r\n")

    # Sending Process
    try:

        server = smtplib.SMTP(host, port)

    except OSError:         # Note to self socket.error is merged as OSError now

        print("Hostname or port is incorrect...")
        server = None

    if server is not None:
        
        server.starttls()                   # TLS encrypt the connection
        
        try:

            login = server.login(email, password)

        except smtplib.SMTPAuthenticationError:

            print("Invalid login credentials, may need to create 'App Password in email settings'...")
            login = None

        # Secure the connection

        if login is not None:

            try:    

                server.sendmail(email,rcpt,message)
                print('Message Sent')
                server.quit()

            except smtplib.SMTPRecipientsRefused:

                print("Check recipients email...")
        else:

            print("Exiting...")
    else:

        print("Exiting...")


"""
    Gets the initial price then waits a few seconds to get 
    the current price and updates it every few seconds.
    Then it calculates the percentage gained or loss.
    If it hits a certain percentage loss or gain then send an email/sms
"""
def startProgram():

    high = 1
    low = -1

    current_time = getCurrentTime()

    print(f"{current_time}:: Getting initial price of {ticker}...")

    initialPrice = cmc.getInitialPrice()

    percentage = 0

    while(1):
        current_time = getCurrentTime()

        print(f"{current_time}:: Getting current price of {ticker}...\n")

        currentPrice = cmc.getCurrentPrice()
        
        percentage = calculatePercentage(initialPrice, currentPrice)

        #between 5 - 10%  or between -5 to -10%
        if((percentage >= 5 or percentage <= -5) and (percentage < 10 and percentage > -10)):
            printGainsLoss(percentage)
            sendEmail(currentPrice, percentage)
            initialPrice = currentPrice
            time.sleep(10)

        #more than -10 or 10%
        elif(percentage >= 10 or percentage <= -10):
            printGainsLoss(percentage)
            sendEmail(currentPrice, percentage)
            initialPrice = currentPrice
            time.sleep(10)

        else:
            printGainsLoss(percentage)
            time.sleep(10)

        
def getCurrentTime():
    fnow = datetime.now()
    current_time = fnow.strftime("%H:%M:%S")

    return current_time

def calculatePercentage(initialPrice, currentPrice):

    percentage = (currentPrice - initialPrice) / initialPrice * 100

    return percentage

def printGainsLoss(percentage):

    if(percentage < 0):

        print("\x1b[1;31;40m" + "Percentage loss: " + str(percentage) + "\x1b[0m" + "\n")

    elif(percentage > 0):

        print("\x1b[1;32;40m" + "Percentage gain: " + str(percentage) + "\x1b[0m" + "\n")
    
    elif(percentage == 0):
        print("\x1b[1;32;40m" + "Percentage did not gain: " + str(percentage) + "\x1b[0m" + "\n")

def main():

    startProgram()

if __name__=="__main__":

    cmc = CMC(secretInfo.API_KEY)

    main()
    
