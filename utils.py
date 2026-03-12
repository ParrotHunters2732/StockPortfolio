import database as db
import api
import psycopg2
import urllib3.exceptions as urllet

def add(symbol,quantity):
    conn = None
    try:
        symbol_validation = api.symbol_exist(symbol)
        if not symbol_validation:
            print(f"The given symbol '{symbol}' doesnt have data base!")
            return
        elif symbol_validation and quantity > 0:
            conn = db.get_connection()
            current = api.get_symbol_data(symbol)
            db.write_data_sql(conn,symbol,current,quantity)
            conn.commit()
            conn.close()
            print("Successfully Inserted the transaction")
        else:
            print("Failed | Quantity MUST be above 0.")
    except psycopg2.OperationalError:
        if conn:
            conn.rollback()
            print("Connection To DataBase [ Failed ]")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
            print(f"Error in psycopg2: {e}")
    except urllet.ConnectionError:
        if conn:
            conn.rollback()
            print("No Internet / API unreachable")
    except urllet.TimeoutError:
        if conn:
            conn.rollback()
            print("API Request Took too long")
    except urllet.MaxRetryError:
        if conn:
            conn.rollback()
            print("Connection Retry Limit Hit")
    except urllet.HTTPError as e:
        if conn:
            conn.rollback()
            print(f"Error in Urllib3 : {e}")
    except KeyError:
        if conn:
            conn.rollback()
            print("Unexpect API response")
    except Exception as e:
        if conn:
            conn.rollback()
            print(f"Error in Python : {e}")

def remove_stock():
    conn = None
    try:
        conn = db.get_connection()
        data = db.get_all_stock(conn)
        new_data = [stock[0] for stock in data]
        print(f"| {'-' * 49} |")
        print(f"| {"Stock":^15}|{"Transactions":^14}|{"Transaction History":^14}|")
        print(f"| {'-' * 49} |")
        for stock in new_data:
            count1 , count2 = db.show_count(conn,stock)
            print(f"| {stock:^15}|{count1:^14}|{count2:^18} |")
        print(f"| {'-' * 49} |")
        while True:
            input_stock = input("Enter the stock you want to remove from above [q to quit]: ").replace(" ","").upper()
            if input_stock == "Q":
                    print("Quited")
                    break
            for stock in data:
                if f'{input_stock}' == stock[0]:
                    counts = db.show_count(conn,stock)
                    db.delete_symbol_transactions(conn,stock)
                    db.delete_symbol_transactions_data(conn,stock)
                    api.store_stock_current_price(conn)
                    stocks_sum , total_portfilio_data , percentage , total_invested , total_current = db.load_all_data_sql(conn)
                    total_qty = 0
                    portfolio_summarized_data = total_portfilio_data,total_qty,percentage,total_invested,total_current
                    new_uuid = db.write_portfolio_sum_sql(conn,portfolio_summarized_data)
                    for stockrow in stocks_sum:
                        symbol , current_price , bought_price , qty , pnl , diff, change_percentage , TTSPS , TTCPPS = stockrow
                        total_qty += qty
                        transactions_data = symbol,current_price,bought_price,diff,change_percentage,pnl,TTSPS,TTCPPS,qty,new_uuid
                        db.write_transactions_data_sql(conn,transactions_data)
                        db.update_port_sum_qty(conn,total_qty,new_uuid)
                    db.delete_stock(conn,stock)
                    print(f"There are {counts[0]} transactions and {counts[1]} transactions's history")
                    while True:    
                        decision = input("[ DELETED ] data can **NOT be retrieve. Do you still intend to move forward?[Y/n]:  ").replace(" ","").lower()
                        if decision == "n":
                            conn.rollback()
                            print("Quited")
                            break
                        elif decision == "y":
                            conn.commit()
                            print("successfully removed")
                            break
                    break
            else:
                print(f"{input_stock} does **NOT have a data")
                continue
            break
    except psycopg2.OperationalError:
        if conn:
            conn.rollback()
            print("Connection To DataBase [ Failed ]")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
            print(f"Error in psycopg2: {e}")
    except urllet.ConnectionError:
        if conn:
            conn.rollback()
            print("No Internet / API unreachable")
    except urllet.TimeoutError:
        if conn:
            conn.rollback()
            print("API Request Took too long")
    except urllet.MaxRetryError:
        if conn:
            conn.rollback()
            print("Connection Retry Limit Hit")
    except urllet.HTTPError as e:
        if conn:
            conn.rollback()
            print(f"Error in Urllib3 : {e}")
    except KeyError:
        if conn:
            conn.rollback()
            print("Unexpect API response")
    except Exception as e:
        if conn:
            conn.rollback()
            print(f"Error in Python : {e}")
    finally:
        conn.close()

def remove_transaction():
    conn = None
    try:
        conn = db.get_connection()
        data = db.get_all_stock(conn)
        data = [stock[0] for stock in data]
        print(f"| {'-' * 49} |")
        print(f"| {"Stock":^15}|{"Transactions":^14}|{"Transaction History":^14}|")
        print(f"| {'-' * 49} |")
        for stock in data:
            count1 , count2 = db.show_count(conn,stock)
            print(f"| {stock:^15}|{count1:^14}|{count2:^18} |")
        print(f"| {'-' * 49} |")
        while True:
            chosen_stock = input("Select a stock from the list above[q to quit]: ").replace(" ","").upper()
            if chosen_stock == "Q":
                print("Quited")
                break
            elif chosen_stock in data:
                data = db.load_individual_stock_transaction(conn,chosen_stock)
                id_list = []
                print(f"| {'-' * 60} |")
                print(f"| {"ID":^15}|{"Stock":^14}|{"Holdings":^14}|{"quantity":^14} |")
                print(f"| {'-' * 60} |")
                for transaction in data:
                    id , symbol , holdings , quantity = transaction
                    print(f"| {id:^15}|{symbol:^14}|{holdings:^14}|{quantity:^14} |")
                    id_list.append(str(id))
                print(f"| {'-' * 60} |")
                while True:
                    selected_transaction = input("Select The ID of the transaction your would like to remove[q to quit]: ")
                    if selected_transaction == "q" or selected_transaction == "Q":
                        print("Quited")
                        break
                    elif str(selected_transaction) in id_list:
                        db.delete_transaction_base_id(conn,int(selected_transaction))
                        stocks_sum , total_portfilio_data , percentage , total_invested , total_current = db.load_all_data_sql(conn)
                        total_qty = 0
                        portfolio_summarized_data = total_portfilio_data,total_qty,percentage,total_invested,total_current
                        new_uuid = db.write_portfolio_sum_sql(conn,portfolio_summarized_data)
                        for stockrow in stocks_sum:
                            symbol , current_price , bought_price , qty , pnl , diff, change_percentage , TTSPS , TTCPPS = stockrow
                            total_qty += qty
                            transactions_data = symbol,current_price,bought_price,diff,change_percentage,pnl,TTSPS,TTCPPS,qty,new_uuid
                            db.write_transactions_data_sql(conn,transactions_data)
                        db.update_port_sum_qty(conn,total_qty,new_uuid)
                        while True:
                            decision = input(f"Would you like to delete the transaction #id '{selected_transaction}' [Y/n]: ").replace(" ","").lower()
                            if decision == "n":
                                conn.rollback()
                                print(f"Removal of Transaction #ID {selected_transaction} has been Canceled")
                                break
                            elif decision == "y":
                                conn.commit()
                                print(f"Successfully Removed Transaction #ID {selected_transaction} !")
                                break
                            else:
                                print(f"'{decision}' was **NOT Valid! [Y/n] only")
                                continue
                        break
                    else:
                        print(f"'{selected_transaction}' was **NOT a valid ID try again!")
                break
            else:
                print(f"There is not related data to the symbol '{chosen_stock}' Try again!")
    except psycopg2.OperationalError:
        if conn:
            conn.rollback()
            print("Connection To DataBase [ Failed ]")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
            print(f"Error in psycopg2: {e}")
    except urllet.ConnectionError:
        if conn:
            conn.rollback()
            print("No Internet / API unreachable")
    except urllet.TimeoutError:
        if conn:
            conn.rollback()
            print("API Request Took too long")
    except urllet.MaxRetryError:
        if conn:
            conn.rollback()
            print("Connection Retry Limit Hit")
    except urllet.HTTPError as e:
        if conn:
            conn.rollback()
            print(f"Error in Urllib3 : {e}")
    except KeyError:
        if conn:
            conn.rollback()
            print("Unexpect API response")
    except Exception as e:
        if conn:
            conn.rollback()
            print(f"Error in Python : {e}")
    finally:
        conn.close()

def ls_stock(symbol):
    conn = None
    try:
        symbol = symbol.replace(" ","").upper()
        decision = api.symbol_exist(symbol)
        if decision:
            conn = db.get_connection()
            data = db.load_raw_data_sql(conn,(symbol).replace(" ","").upper())
            i = 0
            print(f"| {'-' * 47} |")
            print(f"| {"Indexes":^9}|{"Stocks":^10}|{"Bought":^10}|{"Quantity":^16}|")
            print(f"| {'-' * 47} |")
            for price , quantity in data:
                i += 1
                print(f"| {i:^8} | {symbol:^8} | {price:>+8} | {quantity:^15}|")
            print(f"| {'-' * 47} |")
        else:
            print(f"the given symbol **{symbol}** doesnt have a database")
    except psycopg2.OperationalError:
        if conn:
            print("Connection To DataBase [ Failed ]")
    except psycopg2.Error as e:
        if conn:
            print(f"Error in psycopg2: {e}")
    except urllet.ConnectionError:
        if conn:
            print("No Internet / API unreachable")
    except urllet.TimeoutError:
        if conn:
            print("API Request Took too long")
    except urllet.MaxRetryError:
        if conn:
            print("Connection Retry Limit Hit")
    except urllet.HTTPError as e:
        if conn:
            print(f"Error in Urllib3 : {e}")
    except KeyError:
        if conn:
            print("Unexpect API response")
    except Exception as e:
        if conn:
            print(f"Error in Python : {e}")
    finally:
        conn.close()

def ls_stocks():
    conn = None
    try:
        conn = db.get_connection()
        data = db.load_all_transactions_sql(conn)
        i = 0
        print(f"| {'-' * 47} |")
        print("|  Indexes |    Stocks    |  Bought  |  Quantity  |")
        print(f"| {'-' * 47} |")
        for stocks , price , quantity in data:
            i += 1
            print(f"| {i:^8} | {stocks:>12} | {price:>8} | {quantity:^11}|")
        print(f"| {'-' * 47} |")
    except psycopg2.OperationalError:
        if conn:
            print("Connection To DataBase [ Failed ]")
    except psycopg2.Error as e:
        if conn:
            print(f"Error in psycopg2: {e}")
    except urllet.ConnectionError:
        if conn:
            print("No Internet / API unreachable")
    except urllet.TimeoutError:
        if conn:
            print("API Request Took too long")
    except urllet.MaxRetryError:
        if conn:
            print("Connection Retry Limit Hit")
    except urllet.HTTPError as e:
        if conn:
            print(f"Error in Urllib3 : {e}")
    except KeyError:
        if conn:
            print("Unexpect API response")
    except Exception as e:
        if conn:
            print(f"Error in Python : {e}")
    finally:
        conn.close()

def current_wl_stock():
    conn = None
    try:
        conn = db.get_connection()
        data = db.get_all_stock(conn)
        data = [stock[0] for stock in data]
        print(f"| {'-' * 49} |")
        print(f"| {"Stock":^15}|{"Transactions":^14}|{"Transaction History":^14}|")
        print(f"| {'-' * 49} |")
        for stock in data:
            count1 , count2 = db.show_count(conn,stock)
            print(f"| {stock:^15}|{count1:^14}|{count2:^18} |")
        print(f"| {'-' * 49} |")
        while True:
            chosen_stock = input("select a stock from the list above[q to quit]: ").replace(" ","").upper()
            if chosen_stock == "Q":
                print("Quited")
                break
            elif chosen_stock in data:
                api.store_stock_current_price(conn)
                stocks_sum , total_portfilio_data , percentage , total_invested , total_current = db.load_all_data_sql(conn) #write new data into the data base 
                total_qty = 0
                portfolio_summarized_data = total_portfilio_data,total_qty,percentage,total_invested,total_current
                new_uuid = db.write_portfolio_sum_sql(conn,portfolio_summarized_data)
                for stockrow in stocks_sum:
                    symbol , current_price , bought_price , qty , pnl , diff, change_percentage , TTSPS , TTCPPS = stockrow
                    total_qty += qty
                    transactions_data = symbol,current_price,bought_price,diff,change_percentage,pnl,TTSPS,TTCPPS,qty,new_uuid
                    db.write_transactions_data_sql(conn,transactions_data)
                db.update_port_sum_qty(conn,total_qty,new_uuid)
                conn.commit()
                stock_data1 = db.load_individual_symbol_calculated_transaction(conn,chosen_stock) #return calculated net data off of individual stock
                transactions = db.load_raw_data_sql(conn,(chosen_stock).replace(" ","").upper()) #load raw transactions base off of symbol
                i = 0
                print(f"| {'-' * 59} |")
                print(f"| {"Indexes":^9}|{"Stocks":^10}|{"MarketValue":^10}|{"Bought":^10}|{"Quantity":^16}|")
                print(f"| {'-' * 59} |")
                for price2 , quantity , *_ in transactions:
                    i += 1
                    print(f"| {i:^8} | {chosen_stock:^8} |{stock_data1[0][1]:^11.2f}| {price2:>8} | {quantity:^15}|")
                print(f"| {'-' * 59} |")
                print(f"| {'-' * 59} |")
                print(f"| { 'NET PROFIT / LOSS':<32} : {f'{stock_data1[0][3]:+.2f} $':^24} |")
                print(f"| { 'TOTAL QUANTITY':<32} : {stock_data1[0][2]:^24} |")
                print(f"| { 'TOTAL Inc / Dec %':<32} : {f'{stock_data1[0][5]:+.2f} %':^24} |")
                print(f"| {'-' * 59} |")
                print(f"| { 'TOTAL INVESTED':<32} : {f'{stock_data1[0][6]:.2f} $':^24} |")
                print(f"| { 'CURRENT MARKET VALUE':<32} : {f'{stock_data1[0][7]:.2f} $':^24} |")
                print(f"| {'-' * 59} |")
                break
            else:
                print("there is not related data to the given symbol try again")
    except psycopg2.OperationalError:
        if conn:
            conn.rollback()
            print("Connection To DataBase [ Failed ]")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
            print(f"Error in psycopg2: {e}")
    except urllet.ConnectionError:
        if conn:
            conn.rollback()
            print("No Internet / API unreachable")
    except urllet.TimeoutError:
        if conn:
            conn.rollback()
            print("API Request Took too long")
    except urllet.MaxRetryError:
        if conn:
            conn.rollback()
            print("Connection Retry Limit Hit")
    except urllet.HTTPError as e:
        if conn:
            conn.rollback()
            print(f"Error in Urllib3 : {e}")
    except KeyError:
        if conn:
            conn.rollback()
            print("Unexpect API response")
    except Exception as e:
        if conn:
            conn.rollback()
            print(f"Error in Python : {e}")
    finally:
        conn.close()

def current_wl_stocks():
    conn = None
    try:
        conn = db.get_connection()
        api.store_stock_current_price(conn)
        stocks_sum , total_portfilio_data , percentage , total_invested , total_current = db.load_all_data_sql(conn)
        total_qty = 0
        print(f"| {'-' * 47} |")
        print("|  Stocks  | Current Price |  Bought  |  Quantity |")
        print(f"| {'-' * 47} |")
        portfolio_summarized_data = total_portfilio_data,total_qty,percentage,total_invested,total_current
        new_uuid = db.write_portfolio_sum_sql(conn,portfolio_summarized_data)
        for data in stocks_sum:
            symbol , current_price , bought_price , qty , pnl , diff, change_percentage , TTSPS , TTCPPS = data
            total_qty += qty
            transactions_data = symbol,current_price,bought_price,diff,change_percentage,pnl,TTSPS,TTCPPS,qty,new_uuid
            db.write_transactions_data_sql(conn,transactions_data)
            print(f"| {symbol:^8} | {current_price:^10.2f} | {bought_price:^10.2f} | {qty:^11}|")
        db.update_port_sum_qty(conn,total_qty,new_uuid)
        print(f"| {'-' * 47} |")
        print(f"| { 'NET PROFIT / LOSS':<26} : {f'{total_portfilio_data:+.2f} $':^18} |")
        print(f"| { 'TOTAL QUANTITY':<26} : {total_qty:^18} |")
        print(f"| { 'TOTAL Inc / Dec %':<26} : {f'{percentage:+.2f} %':^19}|")
        print(f"| {'-' * 47} |")
        print(f"| { 'TOTAL INVESTED':<26} : {f'{total_invested:.2f} $':^18} |")
        print(f"| { 'CURRENT MARKET VALUE':<26} : {f'{total_current:.2f} $':^18} |")
        print(f"| {'-' * 47} |")
    except psycopg2.OperationalError:
        if conn:
            conn.rollback()
            print("Connection To DataBase [ Failed ]")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
            print(f"Error in psycopg2: {e}")
    except urllet.ConnectionError:
        if conn:
            conn.rollback()
            print("No Internet / API unreachable")
    except urllet.TimeoutError:
        if conn:
            conn.rollback()
            print("API Request Took too long")
    except urllet.MaxRetryError:
        if conn:
            conn.rollback()
            print("Connection Retry Limit Hit")
    except urllet.HTTPError as e:
        if conn:
            conn.rollback()
            print(f"Error in Urllib3 : {e}")
    except KeyError:
        if conn:
            conn.rollback()
            print("Unexpect API response")
    except Exception as e:
        if conn:
            conn.rollback()
            print(f"Error in Python : {e}")
    else:
        conn.commit()
    finally:
        conn.close()

def current_wl_deep():
    conn = None
    try:
        conn = db.get_connection()
        api.store_stock_current_price(conn)
        stocks_sum , total_portfilio_data , percentage , total_invested , total_current = db.load_all_data_sql(conn)
        total_qty = 0
        print(f"| {'-' * 89} |")
        print(f"|{"Stock":^7}|{"Value":^9}|{"Owned":^9}|{"Diff":^8}|{"Diff%":^8}|{"Profit&Loss":^5}|{"MarketValue":^12}|{"Holdings":^12}|{"QTY":^7}|")
        print(f"| {'-' * 89} |")
        portfolio_summarized_data = total_portfilio_data,total_qty,percentage,total_invested,total_current
        new_uuid = db.write_portfolio_sum_sql(conn,portfolio_summarized_data)
        for data in stocks_sum:
            symbol , current_price , bought_price , qty , pnl , diff, change_percentage , TTSPS , TTCPPS = data
            total_qty += qty
            transactions_data = symbol,current_price,bought_price,diff,change_percentage,pnl,TTSPS,TTCPPS,qty,new_uuid
            db.write_transactions_data_sql(conn,transactions_data)
            print(f"| {symbol:^5} | {current_price:^7.2f} | {bought_price:^7.2f} | {diff:^+7.2f}| {change_percentage:^+7.2f}| {pnl:^+10.2f}|{TTCPPS:^12.2f}|{TTSPS:^12.2f}|{qty:^7}|")
        db.update_port_sum_qty(conn,total_qty,new_uuid)
        print(f"| {'-' * 89} |")
        print(f"| { 'NET PROFIT / LOSS':<26} : {f'{total_portfilio_data:+.2f} $':^17}|")
        print(f"| { 'TOTAL QUANTITY':<26} : {total_qty:^17}|")
        print(f"| { 'TOTAL Inc / Dec %':<26} : {f'{percentage:+.2f} %':^17}|")
        print(f"|{'-' * 47}|")
        print(f"| { 'TOTAL INVESTED':<26} : {f'{total_invested:.2f} $':^17}|")
        print(f"| { 'CURRENT MARKET VALUE':<26} : {f'{total_current:.2f} $':^17}|")
        print(f"| {'-' * 89} |")
    except psycopg2.OperationalError:
        if conn:
            conn.rollback()
            print("Connection To DataBase [ Failed ]")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
            print(f"Error in psycopg2: {e}")
    except urllet.ConnectionError:
        if conn:
            conn.rollback()
            print("No Internet / API unreachable")
    except urllet.TimeoutError:
        if conn:
            conn.rollback()
            print("API Request Took too long")
    except urllet.MaxRetryError:
        if conn:
            conn.rollback()
            print("Connection Retry Limit Hit")
    except urllet.HTTPError as e:
        if conn:
            conn.rollback()
            print(f"Error in Urllib3 : {e}")
    except KeyError:
        if conn:
            conn.rollback()
            print("Unexpect API response")
    except Exception as e:
        if conn:
            conn.rollback()
            print(f"Error in Python : {e}")
    else:
        conn.commit()
    finally:
        conn.close()

def get_info(symbol):
    try:
        company_data , has_company_data = api.get_company_data(symbol)
        if has_company_data:
            price = api.get_symbol_data(symbol)
            print(f"| {'-' * 47} |")
            print(f"| { 'Name':<15} : {company_data.get('name'):^29} |")
            print(f"| { 'Ticker Symbol':<15} : {company_data.get('ticker'):^29} |")
            print(f"| { 'Country':<15} : {company_data.get('country'):^29} |")
            print(f"| { 'Currency':<15} : {company_data.get('estimateCurrency'):^29} |")
            print(f"| { 'Current Price':<15} : {price:^29} |")
            print(f"| { 'Market Cap':<15} : {company_data.get('marketCapitalization'):^29} |")
            print(f"| { 'Share Out':<15} : {company_data.get('shareOutstanding'):^29} |")
            print(f"| { 'Catagory':<15} : {company_data.get('finnhubIndustry'):^29} |")
            print(f"| { 'Phone':<15} : {company_data.get('phone'):^29} |")
            print(f"| { 'Website':<15} : {company_data.get('weburl'):^29} |")
            print(f"| {'-' * 47} |")
        else:
            print(f"| {'-' * 47} |")
            is_symbol_exist = api.symbol_exist(symbol)
            if is_symbol_exist:
                print(f"{symbol} Does Exist But Doesnt have a Company Profile")
            else:
                print(f"It Seems like Your Symbol {symbol} **DOES NOT** have Company DataBase")
            print(f"| {'-' * 47} |")
    except urllet.ConnectionError:
            print("No Internet / API unreachable")
    except urllet.TimeoutError:
            print("API Request Took too long")
    except urllet.MaxRetryError:
            print("Connection Retry Limit Hit")
    except urllet.HTTPError as e:
            print(f"Error in Urllib3 : {e}")
    except KeyError:
            print("Unexpect API response")
    except Exception as e:
            print(f"Error in Python : {e}")

def clear():
    conn = None
    try:
        while True:
            user_decision = input("Would you like to clear all the data within the portfolio? Y/N: ").lower()
            if user_decision == "y":
                conn = db.get_connection()
                db.delete_all_data_sql(conn)
                print("successfully cleared data")
                conn.commit()
                break
            elif user_decision == "n":
                print("Quited")
                break
            else:
                print(f"{user_decision} was **NOT a valid input either use y/n?")
    except psycopg2.OperationalError:
        if conn:
            conn.rollback()
            print("Connection To DataBase [ Failed ]")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
            print(f"Error in psycopg2: {e}")
    except urllet.ConnectionError:
        if conn:
            conn.rollback()
            print("No Internet / API unreachable")
    except urllet.TimeoutError:
        if conn:
            conn.rollback()
            print("API Request Took too long")
    except urllet.MaxRetryError:
        if conn:
            conn.rollback()
            print("Connection Retry Limit Hit")
    except urllet.HTTPError as e:
        if conn:
            conn.rollback()
            print(f"Error in Urllib3 : {e}")
    except KeyError:
        if conn:
            conn.rollback()
            print("Unexpect API response")
    except Exception as e:
        if conn:
            conn.rollback()
            print(f"Error in Python : {e}")
    finally:
        conn.close()