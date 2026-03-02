import urllib3 as urll
import os 
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("finnhub_api")

http = urll.PoolManager()

def get_symbol_data(user_symbol): #get the data of currencies
    user_symbol = user_symbol.replace(" ","").upper()
    base_url = "https://finnhub.io/api/v1/quote"
    params={
        "symbol": user_symbol,
        "token": api_key
    }
    response = http.request("GET",base_url, fields=params)

    data = response.json()
    
    filtered_data = data['c'] #custom filter data here
    return filtered_data

def get_company_data(symbol): #get all the company data 
    symbol = symbol.replace(" ","").upper()
    base_url = "https://finnhub.io/api/v1/stock/profile2"
    params={
        "symbol": symbol,
        "token": api_key
    }
    response = http.request("GET", base_url , fields=params )

    data = response.json()
    if not data:
        return data , False
    else:
        return data , True

def symbol_exist(user_symbol): #check if the symbol exist if yes return true and else
    user_symbol = user_symbol.replace(" ","").upper()
    base_url = "https://finnhub.io/api/v1/search"
    params={
        "q": user_symbol,
        "token": api_key }
    response = http.request("GET", base_url, fields=params)

    data = response.json()
    
    for item in data['result']:
        if item['symbol'] == user_symbol: 
            print(f"The symbol '{user_symbol}' Exists")
            return True

    else:
        print(f"The symbol '{user_symbol}' does *NOT Exists")
        return False

def store_stock_current_price(connection): #storing all stock current prices for further calculation
    with connection.cursor() as cur:
        cur.execute("""SELECT symbol
                    FROM stocks;
""")
        symbols = [row[0] for row in cur.fetchall()] #name of the stocks in db
        upload = []
        base_url = "https://finnhub.io/api/v1/quote"
        for symbol in symbols:
            params={
            "symbol": symbol,
            "token": api_key}
            response = http.request("GET", base_url ,fields=params)
            data = response.json()
            price = data.get('c')
            if price:
                upload.append((price, symbol))
        sql = "UPDATE stocks SET current_market_price = %s WHERE symbol = %s"
        cur.executemany(sql, upload)
        connection.commit()
    return symbols