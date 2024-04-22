import asyncio
import json
from libs.solana_py_proxy.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.signature import Signature
from libs.solana_py_proxy.rpc.types import TokenAccountOpts
from utils.tools import *
from utils.config import *
from solders.pubkey import Pubkey
from utils import logger
from utils.vars import TOKENS, TOKEN_DECIMALS
# from tenacity import stop_after_attempt, retry, wait_random, retry_if_not_exception_type, retry_if_exception_type


class Client():
    def __init__(self, private_key, proxy, id_account) -> None:
        self.id_account = id_account
        self.keypair = Keypair.from_base58_string(private_key)
        self.proxy_dict = {'http://': f'http://{proxy}'}
        self.rpc = AsyncClient(SOL_RPC_URL, proxy=self.proxy_dict)
        
    async def wait_tx_status(self, transaction_id) -> bool:
        sig = Signature.from_string(transaction_id)
        logger.info(f"{self.id_account} | Wait tx status... (max 120s)")
        for _ in range(60):
            await asyncio.sleep(2)
            try:
                status = json.loads((await self.rpc.get_transaction(tx_sig=sig, max_supported_transaction_version=0)).to_json())['result']['meta']['status']
                print(status)
                if status['Ok'] is None:
                    logger.success(f'Transaction https://solscan.io/tx/{transaction_id} is success finalized')
                    return True
            except Exception as e:
                print(e)
        return False
        
    async def check_token_balance(self, token) -> float:
        token_contract = TOKENS[token]
        if token == "SOL":
            balance = await self.rpc.get_balance(self.keypair.pubkey())
            return int_to_decimal(int(json.loads(balance.to_json())['result']['value']), TOKEN_DECIMALS['SOL'])
        else:
            balance = await self.rpc.get_token_accounts_by_owner_json_parsed(
                Pubkey.from_string(str(self.keypair.pubkey())),
                opts=TokenAccountOpts(mint=Pubkey.from_string(token_contract)), 
            )
            return float(balance.value[0].account.data.parsed['info']["tokenAmount"]["uiAmount"])