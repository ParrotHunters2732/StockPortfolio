import psycopg2
from datetime import date

def get_connection(): #getting an self-close connection
    return psycopg2.connect(user="x", host="localhost", dbname="portfolio_db", port="5432")

def load_all_data_sql(connection): #load all data and calculate it for finding average cost per stock
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
        -- The Logic: (Total Money Spent) / (Total Shares Owned)
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
    today = date.today()
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
        try:
            cur.execute("INSERT INTO stocks (symbol) VALUES (%s)", (symbol,))
            cur.execute("INSERT INTO transactions (symbol , price , quantity) VALUES (%s , %s , %s)", (symbol,price,quantity,))
        except psycopg2.errors.UniqueViolation:
            connection.rollback()
            cur.execute("INSERT INTO transactions (symbol , price , quantity) VALUES (%s , %s , %s)", (symbol,price,quantity,))
            print("Successfully insert a transaction")
            connection.commit()
        except Exception as e:
            raise e
        else:
            print("successfully insert a Profile and Transaction")

    
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
                    FROM transactions;""")
        data = cur.fetchall()
        return data

def delete_all_data_sql(connection): #remove all data in db (only transactions)
    with connection.cursor() as cur:
        cur.execute("""
        TRUNCATE TABLE transactions;
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