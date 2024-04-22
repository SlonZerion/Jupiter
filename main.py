import asyncio
from utils.tools import get_accounts_data, logger
from modules.swap import start_swap_accounts

        
    
if __name__ == "__main__":
    accounts_dict = get_accounts_data()
    logger.success(f"✅ {len(accounts_dict)} pairs of accounts were successfully uploaded\n")
    asyncio.run(start_swap_accounts(accounts_dict))