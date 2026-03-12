import argparse as ap
import api
import database as db

parser = ap.ArgumentParser(
    prog="SPC",
    description="Stocks Portfolio Calculator.",
)

sub_parsers = parser.add_subparsers(
    dest="command", 
    required=True
    )

add_cmd = sub_parsers.add_parser("add", help="Add a stock to the portfolio.")
add_cmd.add_argument("symbol")
add_cmd.add_argument("quantity", type=int)

remove_stock_cmd = sub_parsers.add_parser("remove-stock", help="Remove a stock from the portfolio.")

remove_transaction_cmd = sub_parsers.add_parser("remove-transaction", help="remove a specific transaction you can select after the system display ** ALL transaction")

check_symbol_cmd = sub_parsers.add_parser("check_symbol", help="check symbol of the given symbol")
check_symbol_cmd.add_argument("target_symbol")

ls_cmd = sub_parsers.add_parser("ls", help="List all transactions made base on given stock.")
ls_cmd.add_argument("symbol")

ls_a_cmd = sub_parsers.add_parser("ls+" , help="List **ALL of the stocks and transactions")

clear_pf_cmd = sub_parsers.add_parser("clear", help="Clear all the user portfolio **the data will be erase**")

current_wl = sub_parsers.add_parser("current-wl++" , help="Calculate Deep data of Current Portfolio's Profit and Loss. base on given symbol")

current_wl = sub_parsers.add_parser("current-wl+" , help="Calculate Current Portfolio's Profit and Loss. base on given symbol")

current_pf_cmd = sub_parsers.add_parser("current-wl", help="Calculate Current Portfolio's Profit and Loss. Off of **ALL transactions")

get_stock_cmd = sub_parsers.add_parser("get-info", help="Get infomations about the given stock")
get_stock_cmd.add_argument("stock")

args = parser.parse_args()

#-------------------------------------------------------------------------------------

if args.command == "add": #add stocks info and transactions info
    symbol_validation = api.symbol_exist(args.symbol)
    if symbol_validation == False:
        print(f"The given symbol '{args.symbol}' doesnt have data base!")
        
    elif symbol_validation:
        conn = db.get_connection()
        current = api.get_symbol_data(args.symbol)
        db.write_data_sql(conn,args.symbol,current,args.quantity)
        conn.commit()
        print("Successfully Inserted the data")
                
elif args.command == "remove-stock": 
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
                for data in stocks_sum:
                    symbol , current_price , bought_price , qty , pnl , diff, change_percentage , TTSPS , TTCPPS = data
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
            
elif args.command == "remove-transaction":
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
                    for data in stocks_sum:
                        symbol , current_price , bought_price , qty , pnl , diff, change_percentage , TTSPS , TTCPPS = data
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

elif args.command == "ls": #show a list within an individual stocks
    symbol = args.symbol.replace(" ","").upper()
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

elif args.command == "ls+": #show every list within the database
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

elif args.command == "current-wl": #show the calculated data of individual stock ***unfinish
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
            for data in stocks_sum:
                symbol , current_price , bought_price , qty , pnl , diff, change_percentage , TTSPS , TTCPPS = data
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

elif args.command == "current-wl+": #show a brief infomation about stocks
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
    conn.commit()
    print(f"| {'-' * 47} |")
    print(f"| { 'NET PROFIT / LOSS':<26} : {f'{total_portfilio_data:+.2f} $':^18} |")
    print(f"| { 'TOTAL QUANTITY':<26} : {total_qty:^18} |")
    print(f"| { 'TOTAL Inc / Dec %':<26} : {f'{percentage:+.2f} %':^19}|")
    print(f"| {'-' * 47} |")
    print(f"| { 'TOTAL INVESTED':<26} : {f'{total_invested:.2f} $':^18} |")
    print(f"| { 'CURRENT MARKET VALUE':<26} : {f'{total_current:.2f} $':^18} |")
    print(f"| {'-' * 47} |")

elif args.command == "current-wl++": #show insite and deep data about stocks 
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
    conn.commit()
    print(f"| {'-' * 89} |")
    print(f"| { 'NET PROFIT / LOSS':<26} : {f'{total_portfilio_data:+.2f} $':^17}|")
    print(f"| { 'TOTAL QUANTITY':<26} : {total_qty:^17}|")
    print(f"| { 'TOTAL Inc / Dec %':<26} : {f'{percentage:+.2f} %':^17}|")
    print(f"|{'-' * 47}|")
    print(f"| { 'TOTAL INVESTED':<26} : {f'{total_invested:.2f} $':^17}|")
    print(f"| { 'CURRENT MARKET VALUE':<26} : {f'{total_current:.2f} $':^17}|")
    print(f"| {'-' * 89} |")

elif args.command == "get-info": #get symbol's if symbol has company's data then it print com pany data if not it doesnt
    company_data , has_company_data = api.get_company_data(args.stock)
    if company_data:
        price = api.get_symbol_data(args.stock)
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
        is_symbol_exist = api.symbol_exist(args.stock)
        if is_symbol_exist:
            print(f"{args.stock} Does Exist But Doesnt have a Company Profile")
        else:
            print(f"It Seems like Your Symbol {args.stock} **DOES NOT** have Company DataBase")
        print(f"| {'-' * 47} |")

elif args.command == "clear": #remove all the data inside transactions 2 step verification
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