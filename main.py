import asyncio
import ctypes
import random
import sys
import traceback
import time


from art import text2art
from termcolor import colored, cprint

from better_proxy import Proxy

from core import Grass
from core.autoreger import AutoReger
from core.utils import logger, file_to_list
from core.utils.accounts_db import AccountsDB
from core.utils.exception import EmailApproveLinkNotFoundException
from core.utils.generate.person import Person
from data.config import ACCOUNTS_FILE_PATH, PROXIES_FILE_PATH, REGISTER_ACCOUNT_ONLY, THREADS, REGISTER_DELAY, \
    CLAIM_REWARDS_ONLY, APPROVE_EMAIL, APPROVE_WALLET_ON_EMAIL, MINING_MODE, CONNECT_WALLET, \
    WALLETS_FILE_PATH, SEND_WALLET_APPROVE_LINK_TO_EMAIL, SINGLE_IMAP_ACCOUNT, DBCONFIG_FILE_PATH

import argparse

## account = "email:password"
## proxy = "auto-generated"
## wallet = "private key"
parser = argparse.ArgumentParser(description='Grass Auto')
parser.add_argument('--account', type=str, help='Path to accounts file')
parser.add_argument('--proxy', type=str, help='Path to proxies file')
parser.add_argument('--wallet', type=str, help='Path to proxies file')



def bot_info(name: str = ""):
    cprint(text2art(name), 'green')

    if sys.platform == 'win32':
        ctypes.windll.kernel32.SetConsoleTitleW(f"{name}")

    print(
        f"{colored('EnJoYeR <crypto/> moves:', color='light_yellow')} "
        f"{colored('https://t.me/+tdC-PXRzhnczNDli', color='light_green')}"
    )


async def worker_task(_id, account: str, proxy: str = None, wallet: str = None, db: AccountsDB = None):
    consumables = account.split(":")[:3]
    imap_pass = None
    
    if SINGLE_IMAP_ACCOUNT:
        consumables.append(SINGLE_IMAP_ACCOUNT.split(":")[1])

    if len(consumables) == 1:
        email = consumables[0]
        password = Person().random_string(8)
    elif len(consumables) == 2:
        email, password = consumables
    else:
        email, password, imap_pass = consumables

    grass = None

    try:
        grass = Grass(_id, email, password, proxy, db)
        await grass.enter_account()
        user_info = await grass.retrieve_user()
        print(user_info)
        if user_info['result']['data'].get("isVerified"):
            logger.info(f"{grass.id} | {grass.email} email already verified!")
        else:
            await asyncio.sleep(5)
            await grass.confirm_email()

        if user_info['result']['data'].get("walletAddress"):
                logger.info(f"{grass.id} | {grass.email} wallet already linked!")
        else:
            await asyncio.sleep(5)
            await grass.link_wallet(wallet)

        if user_info['result']['data'].get("isWalletAddressVerified"):
            logger.info(f"{grass.id} | {grass.email} wallet already verified!")
        else:
            await asyncio.sleep(5)
            await grass.send_approve_link(endpoint="sendWalletAddressEmailVerification")

        await grass.session.close()
        
        # if MINING_MODE:
        #     await asyncio.sleep(random.uniform(1, 2) * _id)
        #     logger.info(f"Starting №{_id} | {email} | {password} | {proxy}")
        # else:
        #     await asyncio.sleep(random.uniform(*REGISTER_DELAY))
        #     logger.info(f"Starting №{_id} | {email} | {password} | {proxy}")

        # if REGISTER_ACCOUNT_ONLY:
        #     await grass.create_account()
        # elif APPROVE_EMAIL or CONNECT_WALLET or SEND_WALLET_APPROVE_LINK_TO_EMAIL or APPROVE_WALLET_ON_EMAIL:
        #     await grass.enter_account()
 
            
        #     await grass.db_connection.db_referralCode(grass.email, user_info['result']['data'].get("referralCode"))

        #     if APPROVE_EMAIL:
        #         if user_info['result']['data'].get("isVerified"):
        #             logger.info(f"{grass.id} | {grass.email} email already verified!")
        #         else:
        #             await grass.confirm_email(imap_pass)

        #     if CONNECT_WALLET:
        #         if user_info['result']['data'].get("walletAddress"):
        #             logger.info(f"{grass.id} | {grass.email} wallet already linked!")
        #         else:
        #             await grass.link_wallet(wallet)

        #     if user_info['result']['data'].get("isWalletAddressVerified"):
        #         logger.info(f"{grass.id} | {grass.email} wallet already verified!")
        #     else:
        #         if SEND_WALLET_APPROVE_LINK_TO_EMAIL:
        #             await grass.send_approve_link(endpoint="sendWalletAddressEmailVerification")
        #         if APPROVE_WALLET_ON_EMAIL:
        #             if imap_pass is None:
        #                 raise TypeError("IMAP password is not provided")
        #             await grass.confirm_wallet_by_email(imap_pass)
        # elif CLAIM_REWARDS_ONLY:
        #     await grass.claim_rewards()
        # else:

        #     await grass.start()

        return True
    # except LoginException as e:
    #     logger.warning(f"LoginException | {_id} | {e}")
    # except NoProxiesException as e:
    #     logger.warning(e)
    except Exception as e:
        msg = f"{_id} | not handled exception | error: {e} {traceback.format_exc()}"
        print(msg)
    finally:
        await grass.db.close_connection()
        exit()

async def main(account: str = None, proxy: str = None, wallet:str=None):
    # accounts = file_to_list(ACCOUNTS_FILE_PATH)
    # accounts = [account]
    # proxies = [Proxy.from_str(proxy).as_url]
    # proxies = [Proxy.from_str(proxy).as_url for proxy in file_to_list(PROXIES_FILE_PATH)]

    db = AccountsDB(DBCONFIG_FILE_PATH)
    await db.connect()

    # for i, account in enumerate(accounts):
    #     account = account.split(":")[0]
    #     proxy = proxies[i] if len(proxies) > i else None

    #     if await db.proxies_exist(proxy) or not proxy:
    #         continue

    #     await db.add_account(account, proxy)

    # await db.delete_all_from_extra_proxies()
    # await db.push_extra_proxies(proxies[len(accounts):])

    # autoreger = AutoReger.get_accounts(
    #     (ACCOUNTS_FILE_PATH, PROXIES_FILE_PATH, WALLETS_FILE_PATH),
    #     with_id=True,
    #     static_extra=(db, )
    # )

    # threads = THREADS

    # if REGISTER_ACCOUNT_ONLY:
    #     msg = "__REGISTER__ MODE"
    # elif APPROVE_EMAIL or CONNECT_WALLET or SEND_WALLET_APPROVE_LINK_TO_EMAIL or APPROVE_WALLET_ON_EMAIL:
    #     if CONNECT_WALLET:
    #         wallets = file_to_list(WALLETS_FILE_PATH)
    #         if len(wallets) == 0:
    #             logger.error("Wallet file is empty")
    #             return
    #         elif len(wallets) != len(accounts):
    #             logger.error("Wallets count != accounts count")
    #             return
    #     msg = "__APPROVE__ MODE"
    # elif CLAIM_REWARDS_ONLY:
    #     msg = "__CLAIM__ MODE"
    # else:
    #     msg = "__MINING__ MODE"
    #     threads = len(autoreger.accounts)

    # logger.info(msg)

    # await autoreger.start(worker_task, threads)
    await worker_task(1,account=account,proxy=proxy,wallet=wallet,db=db)
    await db.close_connection()



if __name__ == "__main__":

    

    bot_info("GRASS_AUTO")

    if sys.platform == 'win32':

        current = time.time()
        
        args = parser.parse_args()
        email = args.account
        proxy = args.proxy
        wallet = args.wallet

        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main(email,proxy,wallet))

        result = time.time()-current
        print(result)
    else:
        asyncio.run(main())
