import argparse as ap
import decimal
import api
import database as db

file_path = "storage.json"

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
current_pf_cmd.add_argument("symbol")

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
                
elif args.command == "remove-stock": #waiting for dev
    conn = db.get_connection()
    data = db.get_all_stock(conn)
    print(f"|{"Stock":^7}|")
    for stock in data:
        print(stock[0])
    print(f"| {'-' * 89} |")

elif args.command == "remove-transaction":
    pass

elif args.command == "check_symbol": 
    #check if the symbol has a database in finnhub api #devtools
    api.symbol_exist(args.target_symbol)

elif args.command == "ls": #show a list within an individual stocks
    decision = api.symbol_exist(args.symbol)
    if decision:
        conn = db.get_connection()
        data = db.load_raw_data_sql(conn,args.symbol)
        i = 0
        print("- - - - - - - - C U R R E N T | P O R T F O L I O - - - - - - - - - -")
        print(f"| {'-' * 47} |")
        print(f"| {"Indexes":^9}|{"Stocks":^10}|{"Bought":^10}|{"Quantity":^16}|")
        print(f"| {'-' * 47} |")
        for price , quantity in data:
            i += 1
            print(f"| {i:^8} | {args.symbol:^8} | {price:>+8} | {quantity:^15}|")
        print(f"| {'-' * 47} |")
    else:
        print(f"the given symbol **{args.symbol}** doesnt have a database")

elif args.command == "ls+": #show every list within the database
    conn = db.get_connection()
    data = db.load_all_transactions_sql(conn)
    i = 0
    print("- - - - - - - - S T O C K S | O W N E R S H I P E D - - - - - - - - - -")
    print(f"| {'-' * 47} |")
    print("|  Indexes |    Stocks    |  Bought  |  Quantity  |")
    print(f"| {'-' * 47} |")
    for stocks , price , quantity in data:
        i += 1
        print(f"| {i:^8} | {stocks:>12} | {price:>8} | {quantity:^11}|")
    print(f"| {'-' * 47} |")

elif args.command == "current-wl": #show the calculated data of a stock ***unfinish
    decision = api.symbol_exist(args.symbol)

    if decision:
        conn = db.get_connection()
        data = db.load_calculated_data_sql(conn , args.symbol)
        price = data[0][0].quantize(decimal.Decimal('0.01'), rounding = decimal.ROUND_HALF_UP)
        quantity = data[0][1]
        total_invested = data[0][2].quantize(decimal.Decimal('0.01'), rounding = decimal.ROUND_HALF_UP)
        print(f"""Average Price: {price} $
Total Quantity: {quantity}
Total Invested: {total_invested} $
""")
    elif decision == False:
        print(f"The given symbol **{args.symbol}** doesnt have a database")

elif args.command == "current-wl+":
    conn = db.get_connection()
    api.store_stock_current_price(conn)
    stocks_sum , total_portfilio_data , percentage , total_invested , total_current = db.load_all_data_sql(conn)
    total_qty = 0
    print(f"| {'-' * 47} |")
    print("|  Stocks  | Current Price |  Bought  |  Quantity |")
    print(f"| {'-' * 47} |")
    for data in stocks_sum:
        symbol , current_price , bought_price , qty , pnl , diff, change_percentage , TTSPS , TTCPPS = data
        total_qty += qty
        print(f"| {symbol:^8} | {current_price:^10.2f} | {bought_price:^10.2f} | {qty:^11}|")
    print(f"| {'-' * 47} |")
    print(f"| { 'NET PROFIT / LOSS':<26} : {f'{total_portfilio_data:.2f} $':^18} |")
    print(f"| { 'TOTAL QUANTITY':<26} : {total_qty:^18} |")
    print(f"| { 'TOTAL Inc / Dec %':<26} : {f'{percentage:.2f} %':^19}|")
    print(f"| {'-' * 47} |")
    print(f"| { 'TOTAL INVESTED':<26} : {f'{total_invested:.2f} $':^18} |")
    print(f"| { 'CURRENT MARKET VALUE':<26} : {f'{total_current:.2f} $':^18} |")
    print(f"| {'-' * 47} |")

elif args.command == "current-wl++":
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
        print(f"| {symbol:^5} | {current_price:^7.2f} | {bought_price:^7.2f} | {diff:^7.2f}| {change_percentage:^7.2f}| {pnl:^10.2f}|{TTCPPS:^12.2f}|{TTSPS:^12.2f}|{qty:^7}|")
    conn.commit()
    print(f"|{'-' * 89}|")
    print(f"| { 'NET PROFIT / LOSS':<26} : {f'{total_portfilio_data:.2f} $':^17}|")
    print(f"| { 'TOTAL QUANTITY':<26} : {total_qty:^17}|")
    print(f"| { 'TOTAL Inc / Dec %':<26} : {f'{percentage:.2f} %':^17}|")
    print(f"|{'-' * 47}|")
    print(f"| { 'TOTAL INVESTED':<26} : {f'{total_invested:.2f} $':^17}|")
    print(f"| { 'CURRENT MARKET VALUE':<26} : {f'{total_current:.2f} $':^17}|")
    print(f"|{'-' * 47}|{'-' * 42}|")

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
            print("unsuccessful to clear data")
            break
        else:
            print(f"{user_decision} was **NOT a valid input either use Y/N? (N to quit)")