import json
import logging
import secrets
import sqlite3
from coincurve import PublicKey
from sha3 import keccak_256
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, constants
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from web3 import Web3
from web3.logs import DISCARD


con = sqlite3.connect('db.db')
cur = con.cursor()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

k_1 = [
    [
        InlineKeyboardButton("Play", callback_data="play_rsp"),
        InlineKeyboardButton("Balance", callback_data="get_balance"),
        InlineKeyboardButton("Deposit", callback_data="deposite"),
        InlineKeyboardButton("Make wallets", callback_data="gen_wal")
    ]
]

k_2 = [
    [
        InlineKeyboardButton("1", callback_data="1"),
        InlineKeyboardButton("5", callback_data="5"),
        InlineKeyboardButton("10", callback_data="10"),
        InlineKeyboardButton("Return", callback_data="menu")
    ],
]

k_3 = [
    [
        InlineKeyboardButton("🪨 Rock", callback_data="rock"),
        InlineKeyboardButton("✂️ Scissors", callback_data="scissors"),
        InlineKeyboardButton("📄 Paper", callback_data="paper"),
    ],
    [
        InlineKeyboardButton("Return", callback_data="menu")
    ]
]

k_4 = [
    [
        InlineKeyboardButton("Check winner", callback_data="reload")
    ]
]

reply_markup_main = InlineKeyboardMarkup(k_1)
reply_markup_numbers = InlineKeyboardMarkup(k_2)
reply_markup_play = InlineKeyboardMarkup(k_3)
reply_markup_reload = InlineKeyboardMarkup(k_4)

with open('./config.json', 'r') as f:
    config = json.load(f)

proxies = config['proxy']

RPC = config['rpc']
contract = config['contract']
bank_wallet_from = config['bank_wallet_from']
bank_private_key = config['bank_private_key']
url_addr = config['url_addr']
BOT_TOKEN = config['bot_token']
ERC20_ABI = json.loads('''[{"inputs": [],"stateMutability": "nonpayable","type": "constructor"},{"anonymous": false,"inputs": [{"indexed": true,"internalType": "address","name": "owner","type": "address"},{"indexed": true,"internalType": "address","name": "spender","type": "address"},{"indexed": false,"internalType": "uint256","name": "value","type": "uint256"}],"name": "Approval","type": "event"},{"anonymous": false,"inputs": [{"indexed": false,"internalType": "uint256","name": "number","type": "uint256"}],"name": "NumberPlay","type": "event"},{"anonymous": false,"inputs": [{"indexed": true,"internalType": "address","name": "from","type": "address"},{"indexed": true,"internalType": "address","name": "to","type": "address"},{"indexed": false,"internalType": "uint256","name": "value","type": "uint256"}],"name": "Transfer","type": "event"},{"inputs": [{"internalType": "address","name": "owner","type": "address"},{"internalType": "address","name": "spender","type": "address"}],"name": "allowance","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "address","name": "spender","type": "address"},{"internalType": "uint256","name": "amount","type": "uint256"}],"name": "approve","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "address","name": "account","type": "address"}],"name": "balanceOf","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "decimals","outputs": [{"internalType": "uint8","name": "","type": "uint8"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "address","name": "spender","type": "address"},{"internalType": "uint256","name": "subtractedValue","type": "uint256"}],"name": "decreaseAllowance","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "nonpayable","type": "function"},{"inputs": [],"name": "gameCost","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "uint256","name": "id","type": "uint256"}],"name": "gameHistory","outputs": [{"components": [{"internalType": "address","name": "player_1","type": "address"},{"internalType": "address","name": "player_2","type": "address"},{"internalType": "int8","name": "player_1_action","type": "int8"},{"internalType": "int8","name": "player_2_action","type": "int8"},{"internalType": "int8","name": "player_win","type": "int8"}],"internalType": "struct RSP._game[]","name": "","type": "tuple[]"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "gameId","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "address","name": "spender","type": "address"},{"internalType": "uint256","name": "addedValue","type": "uint256"}],"name": "increaseAllowance","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "nonpayable","type": "function"},{"inputs": [],"name": "jackPot","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "name","outputs": [{"internalType": "string","name": "","type": "string"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "players","outputs": [{"internalType": "address payable[]","name": "","type": "address[]"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "uint256","name": "_modulus","type": "uint256"}],"name": "randMod","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "uint256","name": "cost","type": "uint256"}],"name": "setGameCost","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "nonpayable","type": "function"},{"inputs": [],"name": "symbol","outputs": [{"internalType": "string","name": "","type": "string"}],"stateMutability": "view","type": "function"},{"inputs": [],"name": "totalSupply","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "view","type": "function"},{"inputs": [{"internalType": "address","name": "to","type": "address"},{"internalType": "uint256","name": "amount","type": "uint256"}],"name": "transfer","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "address","name": "from","type": "address"},{"internalType": "address","name": "to","type": "address"},{"internalType": "uint256","name": "amount","type": "uint256"}],"name": "transferFrom","outputs": [{"internalType": "bool","name": "","type": "bool"}],"stateMutability": "nonpayable","type": "function"},{"inputs": [{"internalType": "uint256","name": "amount","type": "uint256"},{"internalType": "int8","name": "action","type": "int8"}],"name": "transferPerGame","outputs": [{"internalType": "uint256","name": "","type": "uint256"}],"stateMutability": "nonpayable","type": "function"}]''')

w3 = Web3(Web3.HTTPProvider(RPC,request_kwargs={"proxies":proxies}))
coin = w3.eth.contract(contract, abi=ERC20_ABI)
gasLimit = 210000



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        first_name = update.message.chat.first_name
        last_name = update.message.chat.last_name
        user_name = update.message.chat.username
        user_id = update.message.chat.id
        row = cur.execute("SELECT * FROM users WHERE id_tg = '%s'" % user_id).fetchone()
        if row:
            await update.message.reply_text(f"You are already registered!", parse_mode=constants.ParseMode.HTML)
            await update.message.reply_text("Please choose:", reply_markup=reply_markup_main)
            return False
        private_key = keccak_256(secrets.token_bytes(32)).digest()
        public_key = PublicKey.from_valid_secret(private_key).format(compressed=False)[1:]
        address = keccak_256(public_key).digest()[-20:]
        new_address = Web3.toChecksumAddress("0x"+str(address.hex()))
        await update.message.reply_text(f"Hi Bro\! you are here for the first time, \
    so I created a wallet for you, it will be useful for you to interact\. Write \
    down your private key and don't share it with anyone\!\n\n\
        *Wallet address\:* {new_address}\n\
        *Private key\:* ||{private_key.hex()}||", parse_mode=constants.ParseMode.MARKDOWN_V2)
        await update.message.reply_text(f"And now I will transfer 10 tokens to your wallet so that you can start spending them...\n\n Just wait 5 second...", 
        parse_mode=constants.ParseMode.HTML)
        transaction = {
            'chainId': 137,
            'to': new_address,
            'from': bank_wallet_from,
            'value': Web3.toWei(0.1, 'ether'),
            'nonce': w3.eth.getTransactionCount(bank_wallet_from),
            'gas': gasLimit,
            'gasPrice': w3.eth.gas_price * 2
        }
        signed_txn = w3.eth.account.sign_transaction(transaction, bank_private_key)
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        native_hash = txn_hash.hex()
        dict_transaction = {
            'chainId': 137,
            'from': bank_wallet_from,
            'gas': gasLimit,
            'gasPrice': w3.eth.gas_price * 2,
            'nonce': w3.eth.getTransactionCount(bank_wallet_from) + 1,
        }
        coin_decimals = coin.functions.decimals().call()
        one_coin = 10 * 10 ** coin_decimals
        transaction = coin.functions.transfer(new_address, one_coin).buildTransaction(dict_transaction)
        signed_txn = w3.eth.account.sign_transaction(transaction, bank_private_key)
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        await update.message.reply_text(f"Alright, bro! I sent you <b>10 RSP</b> native tokens and <b>0.01 MATIC</b> for transaction.\n\n\n\
RSP transaction hash: <a href='{url_addr}{txn_hash.hex()}'>{txn_hash.hex()}</a>\n\n\
MATIC transaction hash: <a href='{url_addr}{native_hash}'>{native_hash}</a>", 
        parse_mode=constants.ParseMode.HTML, disable_web_page_preview=True)
        cur.execute(f"INSERT INTO users (first_name, last_name, user_name, id_tg, address, private_key, balance, win, lose, dt_create) VALUES ('{first_name}','{last_name}','{user_name}','{user_id}' ,'{new_address}', '{private_key.hex()}', 10, 0,0,'2022-05-19');")
        con.commit()
        await update.message.reply_text("Please choose:", reply_markup=reply_markup_main)
    except Exception as e:
        print(e)
        await update.message.reply_text("Something wrong... Try again command /start")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    user_id = update.callback_query.from_user.id
    if query.data == "play_rsp":
        await query.answer()
        row = cur.execute("SELECT * FROM users WHERE id_tg = '%s'" % user_id).fetchone()
        if row:
            cost_play = coin.functions.gameCost().call() / (10**18)
            reward = cost_play * 2 * .9
            if row[4] >= cost_play:
                await query.edit_message_text(f"The game costs {str(cost_play)} RSP tokens, if you win, you will take {str(reward)} RSP tokens", reply_markup=reply_markup_play)
                return None
            else:
                await query.edit_message_text(f"Sorry, but need more RSP tokens", reply_markup=reply_markup_main)
                return None
    elif query.data == "get_balance":
        row = cur.execute("SELECT * FROM users WHERE id_tg = '%s'" % user_id).fetchone()
        if row:
            msg = f"*Your balance:* {row[4]} RSP"
        else:
            msg = f"*Your balance:* \-\-\- RSP"
    elif query.data == "deposite":
        row = cur.execute("SELECT * FROM users WHERE id_tg = '%s'" % user_id).fetchone()
        if row:
            await query.edit_message_text(f"I will transfer 5 tokens to your address\n Just wait 5 second...\n", 
            parse_mode=constants.ParseMode.HTML)
            dict_transaction = {
                'chainId': 137,
                'from': bank_wallet_from,
                'gas': gasLimit,
                'gasPrice': w3.eth.gas_price * 2,
                'nonce': w3.eth.getTransactionCount(bank_wallet_from),
            }
            coin_decimals = coin.functions.decimals().call()
            one_coin = 5 * 10 ** coin_decimals
            transaction = coin.functions.transfer(row[2], one_coin).buildTransaction(dict_transaction)
            signed_txn = w3.eth.account.sign_transaction(transaction, bank_private_key)
            txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
            await query.message.reply_text(f"Alright! I sent you 5 RSP. Transaction hash <a href='{url_addr}{txn_hash.hex()}'>{txn_hash.hex()}</a>", 
            parse_mode=constants.ParseMode.HTML)
            new_balance = row[4] + 5
            cur.execute(f"UPDATE users SET balance={new_balance} where id={row[0]};")
            con.commit()
        await query.answer()
        await query.message.reply_text("Please choose:", reply_markup=reply_markup_main)
        return True
    elif query.data == "gen_wal":
        await query.answer()
        await query.edit_message_text("How many?:", reply_markup=reply_markup_numbers)
        return None
    elif query.data == "menu":
        msg=''
    elif query.data == "rock":
        try:
            await query.answer()
            await query.edit_message_text(text="Your choice is accepted, the transaction is being executed...")
            row = cur.execute("SELECT * FROM users WHERE id_tg = '%s'" % user_id).fetchone()
            if row:
                cost_play = coin.functions.gameCost().call()
                dict_transaction = coin.functions.transferPerGame(cost_play,1).buildTransaction({
                    'chainId': 137,
                    'from': row[2],
                    'gas': gasLimit,
                    'gasPrice': w3.eth.gas_price * 2,
                    'nonce': w3.eth.getTransactionCount(row[2])
                }) 
                signed_txn = w3.eth.account.signTransaction(dict_transaction, private_key=row[3])
                txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                receipt = w3.eth.wait_for_transaction_receipt(txn_hash,timeout=120, poll_latency=0.1)
                logs = coin.events.NumberPlay().processReceipt(receipt, errors=DISCARD)
                number = logs[0]['args']['number']
                msg = f"Your playID: {number}\n Push the button and check winner!"
        except Exception as e:
            msg = e
        finally:
            new_balance = row[4] - (cost_play / 10**18)
            cur.execute(f"UPDATE users SET balance={new_balance}, last_game={int(number)} where id={row[0]};")
            con.commit()
            await query.edit_message_text(msg, reply_markup=reply_markup_reload)
            return None
    elif query.data == "scissors":
        try:
            await query.answer()
            await query.edit_message_text(text="Your choice is accepted, the transaction is being executed...")
            row = cur.execute("SELECT * FROM users WHERE id_tg = '%s'" % user_id).fetchone()
            if row:
                cost_play = coin.functions.gameCost().call()
                dict_transaction = coin.functions.transferPerGame(cost_play,2).buildTransaction({
                    'chainId': 137,
                    'from': row[2],
                    'gas': gasLimit,
                    'gasPrice': w3.eth.gas_price * 2,
                    'nonce': w3.eth.getTransactionCount(row[2])
                }) 
                signed_txn = w3.eth.account.signTransaction(dict_transaction, private_key=row[3])
                txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                receipt = w3.eth.wait_for_transaction_receipt(txn_hash,timeout=120, poll_latency=0.1)
                logs = coin.events.NumberPlay().processReceipt(receipt, errors=DISCARD)
                number = logs[0]['args']['number']
                msg = f"Your playID: {number}\n Push the button and check winner!"
        except Exception as e:
            msg = e
        finally:
            new_balance = row[4] - (cost_play / 10**18)
            cur.execute(f"UPDATE users SET balance={new_balance}, last_game={int(number)} where id={row[0]};")
            con.commit()
            await query.edit_message_text(msg, reply_markup=reply_markup_reload)
            return None
    elif query.data == "paper":
        try:
            await query.answer()
            await query.edit_message_text(text="Your choice is accepted, the transaction is being executed...")
            row = cur.execute("SELECT * FROM users WHERE id_tg = '%s'" % user_id).fetchone()
            if row:
                cost_play = coin.functions.gameCost().call()
                dict_transaction = coin.functions.transferPerGame(cost_play,3).buildTransaction({
                    'chainId': 137,
                    'from': row[2],
                    'gas': gasLimit,
                    'gasPrice': w3.eth.gas_price * 2,
                    'nonce': w3.eth.getTransactionCount(row[2])
                }) 
                signed_txn = w3.eth.account.signTransaction(dict_transaction, private_key=row[3])
                txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                receipt = w3.eth.wait_for_transaction_receipt(txn_hash,timeout=120, poll_latency=0.1)
                logs = coin.events.NumberPlay().processReceipt(receipt, errors=DISCARD)
                number = logs[0]['args']['number']
                msg = f"Your playID: {number}\n Push the button and check winner!"
        except Exception as e:
            msg = e
        finally:
            new_balance = row[4] - (cost_play / 10**18)
            cur.execute(f"UPDATE users SET balance={new_balance}, last_game={int(number)} where id={row[0]};")
            con.commit()
            await query.edit_message_text(msg, reply_markup=reply_markup_reload)
            return None
    elif query.data == "reload":
        await query.answer()
        row = cur.execute("SELECT * FROM users WHERE id_tg = '%s'" % user_id).fetchone()
        if row:
            history = coin.functions.gameHistory(row[12]).call()
            if row[2] == history[0][0]:
                if history[0][4] == 0:
                    cost_play = coin.functions.gameCost().call()
                    new_balance = row[4] + ((cost_play / 10**18) * 2 / 100 * 90)
                    msg = f"Congratulations!!!\nYou Won!!! Your balance is increased and now equal {new_balance} RSP"
                    cur.execute(f"UPDATE users SET balance={new_balance} where id={row[0]};")
                elif history[0][4] == 1:
                    msg = "You lost, but next time you will be lucky!!!"
                else:
                    msg = "No one won in this game, the cost is returned"
            elif row[2] == history[0][1]:
                if history[0][4] == 1:
                    cost_play = coin.functions.gameCost().call()
                    new_balance = row[4] + ((cost_play / 10**18) * 2 / 100 * 90)
                    msg = f"Congratulations!!!\nYou Won!!! Your balance is increased and now equal {new_balance} RSP"
                    cur.execute(f"UPDATE users SET balance={new_balance} where id={row[0]};")
                elif history[0][4] == 0:
                    msg = "You lost, but next time you will be lucky!!!"
                else:
                    msg = "No one won in this game, the cost is returned"
            print(history)
    elif int(query.data) > 0:
        msg = "<b>ADDRESS:PRIVATE_KEY</b>\n\n"
        for i in range(0,int(query.data)):
            private_key = keccak_256(secrets.token_bytes(32)).digest()
            public_key = PublicKey.from_valid_secret(private_key).format(compressed=False)[1:]
            address = keccak_256(public_key).digest()[-20:]
            msg += f"<code>{address.hex()}:{private_key.hex()}</code>\n\n"

    await query.answer()
    if msg:
        await query.edit_message_text(text=msg, parse_mode=constants.ParseMode.HTML)
        await query.message.reply_text("Please choose:", reply_markup=reply_markup_main)
    else:
        await query.edit_message_text("Please choose:", reply_markup=reply_markup_main)

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == "__main__":
    main()