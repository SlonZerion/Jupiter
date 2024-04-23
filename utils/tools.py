import asyncio
import random
import sys
import pandas as pd
from utils.config import MAX_RETRIES
from utils.logger import logger


def decimal_to_int(d, n):
    return int(d * (10 ** n))


def int_to_decimal(i, n):
    return i / (10 ** n)


def get_accounts_data():
    try:
        with open('Accounts.xlsx', 'rb') as file:
            wb = pd.read_excel(file, sheet_name="Jupiter")
            accounts_data = {}
            for index, row in wb.iterrows():
                account_name = row["Name"] if isinstance(row["Name"], (int, str)) else int(index) + 1
                
                if isinstance(row["Private Key (Solana)"], (str)):
                    account = row["Private Key (Solana)"] 
                    proxy = row['Proxy']
                else:
                    raise ValueError(f"In {int(index) + 1} row the private key in 'Account 1' were entered incorrectly")    
                
                accounts_data[int(index) + 1] = {
                    "account_number": account_name,
                    "account": account,
                    "proxy": proxy,
                }

            return accounts_data
    except Exception as error:
        logger.error(f'\nError in read Exsel file! Error: {error}\n', color='light_red')
        sys.exit()


async def sleep(sleep_from: int, sleep_to: int):
    delay = random.randint(sleep_from, sleep_to)
    logger.info(f"Sleep {delay} s.")
    for _ in range(delay):
        await asyncio.sleep(1)


def retry(func):
    async def wrapper(*args, **kwargs):
        retries = 0
        while retries <= MAX_RETRIES:
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as ex:
                logger.error(f"Error | {ex}")
                await sleep(10, 20)
                retries += 1
    return wrapper
        
        
def get_short_pubkey(pubkey: str) -> str:
    return f"{str(pubkey)[:4]}...{str(pubkey)[-4:]}"

# def get_format_proxy(proxy):
#     address_port, login_password = proxy.split('@')
#     address, port = address_port.split(':')
#     login, password = login_password.split(':')
#     return f'http://{login}:{password}@{address}:{port}'

