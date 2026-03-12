import argparse as ap
import utils

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

ls_cmd = sub_parsers.add_parser("ls", help="List all transactions made base on given stock.")
ls_cmd.add_argument("symbol")

ls_a_cmd = sub_parsers.add_parser("ls+" , help="List **ALL of the stocks and transactions")

clear_pf_cmd = sub_parsers.add_parser("clear", help="Clear all the user portfolio **the data will be erase**")

current_wl_deep= sub_parsers.add_parser("current-wl++" , help="Calculate Deep data of Current Portfolio's Profit and Loss. base on given symbol")

current_wl_stocks= sub_parsers.add_parser("current-wl+" , help="Calculate Current Portfolio's Profit and Loss. base on given symbol")

current_wl_stock = sub_parsers.add_parser("current-wl", help="Calculate Current Portfolio's Profit and Loss. Off of **ALL transactions")

get_stock_cmd = sub_parsers.add_parser("get-info", help="Get infomations about the given stock")
get_stock_cmd.add_argument("symbol")

args = parser.parse_args()

#-------------------------------------------------------------------------------------
match args.command:
    case "add": #add stocks info and transactions info
        utils.add(args.symbol,args.quantity)
    case "remove-stock": #remove data and transaction of a chosen stock
        utils.remove_stock()
    case "remove-transaction":#remove single transaction off of a stock + 2 step verification
        utils.remove_transaction()
    case "ls": #show a list within an individual stocks
        utils.ls_stock(args.symbol)
    case "ls+": #show every list within the database
        utils.ls_stocks()
    case "current-wl": #show the calculated data of individual stock
        utils.current_wl_stock()
    case "current-wl+": #show a brief infomation about stocks
        utils.current_wl_stocks()
    case "current-wl++": #show insite and deep data about stocks 
        utils.current_wl_deep()
    case "get-info": #get symbol's if symbol has company's data then it print com pany data if not it doesnt
        utils.get_info(args.symbol)
    case "clear": #remove all the data inside transactions 2 step verification
        utils.clear()