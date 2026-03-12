import psycopg2
import datetime

def get_connection(): #getting an self-close connection
    return psycopg2.connect(user="x", host="localhost", dbname="portfolio_db", port="5432")

def load_individual_symbol_calculated_transaction(connection,symbol): #load all data and return all the calculated data
    with connection.cursor() as cur:
        cur.execute("""
       SELECT
    s.current_market_price,
    t.avg_cost,
    t.total_quantity
FROM stocks s
JOIN (
    SELECT
        symbol, 
        SUM(quantity) AS total_quantity,
        SUM(price * quantity) / SUM(quantity) AS avg_cost
    FROM transactions
    GROUP BY symbol
) t
ON s.symbol = t.symbol
WHERE s.symbol = %s;
""", (symbol,))
        data = cur.fetchall()
        return_data = []
        for row in data:
            current_price , spent , qty = float(row[0]) , float(row[1]) , row[2]
            diff = current_price - spent
            pnl = diff * qty 
            change_percentage = (diff / spent)*100
            TTSPS = spent * qty
            TTCPPS = current_price * qty
            data = current_price , spent , qty , pnl , diff, change_percentage , TTSPS , TTCPPS 
            return_data.append(data)
        return return_data

def load_all_data_sql(connection): #load all data and return all the calculated data
    with connection.cursor() as cur:
        cur.execute("""SELECT
    s.symbol,
    s.current_market_price,
    t.avg_cost,
    t.total_quantity
FROM stocks s
JOIN (
    SELECT
        symbol, 
        SUM(quantity) AS total_quantity,
        SUM(price * quantity) / SUM(quantity) AS avg_cost
    FROM transactions
    GROUP BY symbol
) t
ON s.symbol = t.symbol;
""")
        data = cur.fetchall()
        return_data = []
        total_portfolio_pnl = 0
        total_spent = 0
        total_current = 0
        for row in data:
            symbol , current_price , spent , qty = row[0] , float(row[1]) , float(row[2]) , row[3]
            diff = current_price - spent
            pnl = diff * qty 
            total_spent += spent * qty
            total_portfolio_pnl += pnl
            total_current += current_price * qty
            change_percentage = (diff / spent)*100
            TTSPS = spent * qty #total spent per stock
            TTCPPS = current_price * qty
            data = symbol , current_price , spent , qty , pnl , diff, change_percentage , TTSPS , TTCPPS 
            return_data.append(data)
        percentage = ((total_current - total_spent) / total_spent)* 100
        return return_data ,total_portfolio_pnl , percentage , total_spent , total_current

def write_transactions_data_sql(connection,data): #commit outer scope
    with connection.cursor() as cur:
        cur.execute("""
        INSERT INTO transactions_data (symbol,market_value,holdings,difference,difference_percentages,profitnloss,total_holdings,total_market_value_ps,quantity,summary_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (data))

def write_portfolio_sum_sql(connection,data): #commit outer scope
    today = datetime.datetime.now()
    new_data = data + (today,)
    with connection.cursor() as cur:
        cur.execute("""
        INSERT INTO portfolio_summary (net_profitnloss,total_quantity,total_percentage,total_invested,total_mv,date)
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING id 
        """,(new_data))
        new_uuid = cur.fetchone()[0]
        return new_uuid

def write_data_sql(connection , symbol , price , quantity): #write data of transaction in db
    symbol = f'{symbol.replace(" ","").upper()}'
    with connection.cursor() as cur:
        cur.execute("""
            INSERT INTO stocks (symbol, current_market_price)
            VALUES (%s,%s)
            ON CONFLICT (symbol) DO NOTHING;
            
            INSERT INTO transactions (symbol , price , quantity)
            VALUES (%s,%s,%s);
""",(symbol,price,symbol,price,quantity))
    
def load_calculated_data_sql(connection , symbol): #get calculated db off of induvidual stock
    with connection.cursor() as cur:
        cur.execute("""SELECT
                        SUM(quantity * price) / SUM(quantity) AS average_costs,
                        SUM(quantity) AS total_quantity,
                        SUM(quantity * price) AS total_spent
                        FROM transactions
                        WHERE symbol = %s;""" , (symbol,))
        data = cur.fetchall()
        return data
    
def load_raw_data_sql(connection , symbol): #get db off of induvidual transaction
    with connection.cursor() as cur:
        cur.execute("""SELECT price,quantity
                       FROM transactions
                       where symbol = %s
                                    """ , (symbol,))
        data = cur.fetchall()
        return data

def load_all_transactions_sql(connection): #get db off of all transactions
    with connection.cursor() as cur:
        cur.execute("""SELECT symbol , price , quantity
                    FROM transactions
                    ORDER BY symbol;""")
        data = cur.fetchall()
        return data

def delete_all_data_sql(connection): #remove all data in db (only transactions)
    with connection.cursor() as cur:
        cur.execute("""
        TRUNCATE TABLE transactions , transactions_data , portfolio_summary , stocks;
""")
        
def get_all_stock(connection):
    with connection.cursor() as cur:
        cur.execute("""
        SELECT symbol FROM stocks;
""")
        data = cur.fetchall()
        return data

def delete_stock(connection, stock):
    with connection.cursor() as cur:
        cur.execute("""
        DELETE FROM stocks WHERE symbol = %s;
""",(stock))

def delete_symbol_transactions(connection,symbol):
    with connection.cursor() as cur:
        cur.execute("""
        DELETE FROM transactions WHERE symbol = %s;
""", (symbol,))

def delete_symbol_transactions_data(connection,symbol):
    with connection.cursor() as cur:
        cur.execute("""
        DELETE FROM transactions_data WHERE symbol = %s;
""", (symbol,))

def delete_transaction_base_id(connection,id):
    with connection.cursor() as cur:
        cur.execute("""
        DELETE FROM transactions WHERE id = %s;
""", (id,))

def update_port_sum_qty(connection,qty,uuid):
    with connection.cursor() as cur:
        cur.execute("""
        UPDATE portfolio_summary 
        SET total_quantity = %s
        WHERE id = %s
""", (qty,uuid))

def show_count(connection,symbol):
    with connection.cursor() as cur:
        cur.execute("""SELECT
        (SELECT COUNT(t.id) FROM transactions t WHERE t.symbol = %s) AS transactions_counts,
        (SELECT COUNT(td.id) FROM transactions_data td WHERE td.symbol = %s) AS transactions_data_counts;
""", (symbol,symbol,))
        
        respond = cur.fetchone()
        return respond
    
def load_individual_stock_transaction(connection,symbol):
    with connection.cursor() as cur:
        cur.execute("""
    SELECT * FROM transactions WHERE symbol = %s
""", (symbol,))
        data = cur.fetchall()
        return data

conn = get_connection()
#print(load_individual_symbol_calculated_transaction(conn,'AAPL'))
