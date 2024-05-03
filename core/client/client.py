import asyncio
import json
from solana_py_proxy.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.signature import Signature
from solana_py_proxy.rpc.types import TokenAccountOpts
from utils.tools import *
from utils.config import *
from solana_py_proxy.rpc.core import RPCException, UnconfirmedTxError
from solana_py_proxy.exceptions import SolanaRpcException
from solders.pubkey import Pubkey
from utils.logger import logger
from utils.vars import TOKENS, TOKEN_DECIMALS


class Client():
    def __init__(self, private_key, proxy, id_account) -> None:
        self.id_account = id_account
        self.keypair = Keypair.from_base58_string(private_key)
        self.proxy = f'http://{proxy}'
        self.rpc = AsyncClient(SOL_RPC_URL, proxy=self.proxy)
        
    # async def wait_tx_status(self, transaction_id) -> bool:
    #     sig = Signature.from_string(transaction_id)
    #     logger.info(f"{self.id_account} | Wait tx status... (max 240s)")
    #     for _ in range(40):
    #         await asyncio.sleep(6)
    #         try:
    #             status = json.loads((await self.rpc.get_transaction(tx_sig=sig, max_supported_transaction_version=0)).to_json())['result']['meta']['status']
    #             if status['Ok'] is None:
    #                 logger.success(f'{self.id_account} | Transaction https://solscan.io/tx/{transaction_id} is success finalized')
    #                 return True
    #         except Exception as e:
    #             pass
    #     return False
        
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