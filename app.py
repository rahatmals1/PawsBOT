from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from colorama import *
from datetime import datetime, timedelta
from fake_useragent import FakeUserAgent
import asyncio, json, os, sys

class Paws:
    def __init__(self) -> None:
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Host': 'api.paws.community',
            'Origin': 'https://app.paws.community',
            'Pragma': 'no-cache',
            'Priority': 'u=3, i',
            'Referer': 'https://app.paws.community/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': FakeUserAgent().random
        }

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_timestamp(self, message):
        print(
            f"{Fore.BLUE + Style.BRIGHT}[ {datetime.now().astimezone().strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{message}",
            flush=True
        )

    async def user(self, token: str):
        url = 'https://api.paws.community/v1/user'
        headers = {
            **self.headers,
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers, ssl=False) as response:
                    response.raise_for_status()
                    return await response.json()
        except ClientResponseError as error:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Project Verify Task: {str(error)} ]{Style.RESET_ALL}")
            return None
        except Exception as error:
            self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Project Verify Task: {str(error)} ]{Style.RESET_ALL}")
            return None

    async def quests_list(self, token: str):
        url = 'https://api.paws.community/v1/quests/list'
        headers = {
            **self.headers,
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers, ssl=False) as response:
                    if response.status in [500, 502, 503, 520]:
                        return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Paws Down While Fetching Quests List ]{Style.RESET_ALL}")
                    response.raise_for_status()
                    quests_list = await response.json()
                    for quest in quests_list['data']:
                        await self.quests_completed(token=token, quest_id=quest['_id'], quest_title=quest['title'], quest_reward=quest['rewards'][0]['amount'])
        except ClientResponseError as error:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Project Verify Task: {str(error)} ]{Style.RESET_ALL}")
        except Exception as error:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Project Verify Task: {str(error)} ]{Style.RESET_ALL}")

    async def quests_completed(self, token: str, quest_id: str, quest_title: str, quest_reward: str):
        url = 'https://api.paws.community/v1/quests/completed'
        data = json.dumps({'questId':quest_id})
        headers = {
            **self.headers,
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                    if response.status in [500, 502, 503, 520]:
                        return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Paws Down While Completed {quest_title} ]{Style.RESET_ALL}")
                    response.raise_for_status()
                    quests_completed = await response.json()
                    if quests_completed['success'] and quests_completed['data']:
                        return await self.quests_claim(token=token, quest_id=quest_id, quest_title=quest_title, quest_reward=quest_reward)
        except ClientResponseError as error:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Project Verify Task: {str(error)} ]{Style.RESET_ALL}")
        except Exception as error:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Project Verify Task: {str(error)} ]{Style.RESET_ALL}")

    async def quests_claim(self, token: str, quest_id: str, quest_title: str, quest_reward: str):
        url = 'https://api.paws.community/v1/quests/claim'
        data = json.dumps({'questId':quest_id})
        headers = {
            **self.headers,
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                    if response.status in [500, 502, 503, 520]:
                        self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ Server Paws Down While Claim {quest_title} ]{Style.RESET_ALL}")
                    response.raise_for_status()
                    quests_claim = await response.json()
                    if quests_claim['success'] and quests_claim['data']:
                        return self.print_timestamp(f"{Fore.GREEN + Style.BRIGHT}[ You\'ve Got {quest_reward} From {quest_title} ]{Style.RESET_ALL}")
        except ClientResponseError as error:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An HTTP Error Occurred While Project Verify Task: {str(error)} ]{Style.RESET_ALL}")
        except Exception as error:
            return self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ An Unexpected Error Occurred While Project Verify Task: {str(error)} ]{Style.RESET_ALL}")

    async def generate_token(self, query: str):
        url = 'https://api.paws.community/v1/user/auth'
        data = json.dumps({'data':query,'referralCode':'2A6XEyqW'})
        headers = {
            **self.headers,
            'Content-Length': str(len(data)),
            'Content-Type': 'application/json'
        }
        while True:
            try:
                async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                    async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                        if response.status in [500, 502, 503, 520]:
                            self.print_timestamp(f"{Fore.YELLOW + Style.BRIGHT}[ Server Paws Down While Generate Token ]{Style.RESET_ALL}")
                        else:
                            response.raise_for_status()
                            generate_token = await response.json()
                            return (generate_token['data'][1]['userData']['firstname'], generate_token['data'][0])
            except (Exception, ClientResponseError) as error:
                self.print_timestamp(
                    f"{Fore.YELLOW + Style.BRIGHT}[ Failed To Process {query} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}[ {str(error)} ]{Style.RESET_ALL}"
                )
                return None

    async def generate_tokens(self, queries):
        tasks = [self.generate_token(query) for query in queries]
        results = await asyncio.gather(*tasks)
        return [result for result in results if result is not None]

    async def main(self):
        while True:
            try:
                queries = [line.strip() for line in open('queries.txt') if line.strip()]
                if not queries:
                    raise FileNotFoundError("Fill Your Query In 'queries.txt'")
                accounts = await self.generate_tokens(queries)
                total_balance = 0

                for (name, token) in accounts:
                    self.print_timestamp(
                        f"{Fore.WHITE + Style.BRIGHT}[ Quests ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}[ {name} ]{Style.RESET_ALL}"
                    )
                    await self.quests_list(token=token)

                for (name, token) in accounts:
                    user = await self.user(token=token)
                    total_balance += user['data']['gameData']['balance'] if user is not None else 0

                self.print_timestamp(
                    f"{Fore.CYAN + Style.BRIGHT}[ Total Account {len(accounts)} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT}[ Total Balance {total_balance} ]{Style.RESET_ALL}"
                )
                self.print_timestamp(f"{Fore.CYAN + Style.BRIGHT}[ Restarting At {(datetime.now().astimezone() + timedelta(seconds=3600)).strftime('%x %X %Z')} ]{Style.RESET_ALL}")

                await asyncio.sleep(3600)
                self.clear_terminal()
            except Exception as e:
                self.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
                continue

if __name__ == '__main__':
    try:
        init(autoreset=True)
        paws = Paws()
        asyncio.run(paws.main())
    except (ValueError, IndexError, FileNotFoundError) as e:
        paws.print_timestamp(f"{Fore.RED + Style.BRIGHT}[ {str(e)} ]{Style.RESET_ALL}")
    except KeyboardInterrupt:
        sys.exit(0)