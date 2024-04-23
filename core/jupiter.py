import random, base64, json, asyncio
from solders.transaction import VersionedTransaction
from solders.message import to_bytes_versioned
from solana.rpc.commitment import Processed
from solana.rpc.types import TxOpts
from utils.config import *
from utils.tools import *
from utils.vars import *
from .client import Client
import httpx




class JupiterSwap(Client):


    async def get_coin_quote(self, token_from_contract, token_to_contract, amount):
        url = f'http://quote-api.jup.ag/v6/quote?inputMint={token_from_contract}&outputMint={token_to_contract}&amount={amount}&slippage={SLIPPAGE_BPS}'
        async with httpx.AsyncClient(proxies=self.proxy) as client:
            r = await client.get(url, timeout=10.0)
            return r.json()


    async def get_coin_swap_quote(self, quoteResponse): 
        async with httpx.AsyncClient(proxies=self.proxy) as client:
            r = await client.post(
                url='http://quote-api.jup.ag/v6/swap',
                json={
                        'quoteResponse': quoteResponse,
                        'userPublicKey': str(self.keypair.pubkey()),
                        'wrapUnwrapSOL': False,
                        'dynamicComputeUnitLimit': True, 
                        'prioritizationFeeLamports': 60000
                    },
                    timeout=10.0
                )
            return r.json()


    @retry
    async def swap(self, token_from, token_to, amount):
        address_token_from, address_token_to = TOKENS[token_from], TOKENS[token_to]
        
        quoteResponse = await self.get_coin_quote(address_token_from, address_token_to, amount)
        transaction_data = await self.get_coin_swap_quote(quoteResponse)
        
        raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data['swapTransaction']))
        signature = self.keypair.sign_message(to_bytes_versioned(raw_transaction.message))
        signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])
        opts = TxOpts(skip_preflight=False, preflight_commitment=Processed, skip_confirmation=True)
        result = await self.rpc.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
        transaction_id = json.loads(result.to_json())['result']
        
        logger.info(f"{self.id_account} | Transaction sent: https://solscan.io/tx/{transaction_id}")
        
        status = await self.wait_tx_status(transaction_id)

        if status == True:
            return
        else:
            logger.error(f'{self.id_account} | https://solscan.io/tx/{transaction_id}')
            raise ValueError("Transaction did not complete")
            
        

async def start_swap(delay_before_start, id_account, account, proxy):
    if delay_before_start >= 0:
        delay_before_start = delay_before_start * random.randint(NEXT_ADDRESS_WAIT_TIME[0], NEXT_ADDRESS_WAIT_TIME[1])
        logger.info(f"{id_account} | Sleep {delay_before_start}s before start", 'blue')
        await asyncio.sleep(delay_before_start)

    jup = JupiterSwap(account, proxy, id_account)

    tx_count = random.randint(TX_COUNT[0], TX_COUNT[1])
    logger.info(f"{id_account} | Jupiter | {jup.keypair.pubkey()} | {tx_count} txs")

    
    for c in range(tx_count):
        if c > 0:
            duration = random.randint(NEXT_TX_WAIT_TIME[0], NEXT_TX_WAIT_TIME[1]) 
            logger.info(f"{id_account} | Jupiter | SWAP | Sleep between tx...")
            await asyncio.sleep(duration)
        token_from, token_to, balance = None, None, 0
        for token in SWAP_FROM:
            balance = await jup.check_token_balance(token)
            logger.info(f"{id_account} | Get balance | {jup.keypair.pubkey()} - {balance} {token}")
            if balance >= BALANCE_MIN_AMOUNT:
                token_from = token
                swap_amount = balance
                
                list_swap_to = list(SWAP_TO)
                if token_from in list_swap_to:
                    list_swap_to.remove(token_from)
                token_to = random.choice(list_swap_to)
                
                break
        if token_from is None or token_to is None:
            logger.error(f'{id_account} | Jupiter | {jup.keypair.pubkey()} | Can\'t find any token with at least {BALANCE_MIN_AMOUNT} balance')
            break
        
        swap_amount *= random.uniform(SWAP_AMOUNT_PERCENT[0], SWAP_AMOUNT_PERCENT[1]) / 100.0
        logger.info(f"{id_account} | Jupiter | SWAP | {round(swap_amount, 4)} {token_from} -> {token_to}")
        
        swap_amount = decimal_to_int(swap_amount, TOKEN_DECIMALS[token_from])
        
        await jup.swap(token_from, token_to, swap_amount)
        
