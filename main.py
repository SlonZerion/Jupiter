import asyncio
from utils.tools import get_accounts_data, logger
from core.jupiter import run_account



async def start_swap_accounts(accounts_dict: dict):
    tasks_list = []
    delay_between_pairs = 0
    for id, v in accounts_dict.items():
        tasks_list.append(asyncio.create_task(run_account(delay_between_pairs, id, v['account'], v['proxy'])))
        delay_between_pairs += 1
    await asyncio.gather(*tasks_list)
    await asyncio.sleep(1)


if __name__ == "__main__":
    accounts_dict = get_accounts_data()
    logger.success(f"✅ {len(accounts_dict)} pairs of accounts were successfully uploaded\n")
    asyncio.get_event_loop().run_until_complete(start_swap_accounts(accounts_dict))