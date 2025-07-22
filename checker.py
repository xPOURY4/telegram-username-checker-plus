import asyncio
import configparser
import logging
import random
import re
import time
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta

import colorama
from colorama import Fore, Style
from telethon.errors import FloodWaitError, UsernameInvalidError, UsernameNotModifiedError, UsernameOccupiedError
from telethon import TelegramClient
from telethon.tl.functions.account import CheckUsernameRequest

# Initialize colorama
colorama.init(autoreset=True)

@dataclass
class Account:
    """Represents a Telegram account configuration."""
    name: str
    api_id: int
    api_hash: str
    phone_number: str
    enabled: bool
    client: Optional[TelegramClient] = None
    flood_wait_until: Optional[datetime] = None
    
    def is_available(self) -> bool:
        """Check if account is available (not in flood wait)."""
        if not self.enabled:
            return False
        if self.flood_wait_until and datetime.now() < self.flood_wait_until:
            return False
        return True
    
    def set_flood_wait(self, seconds: int):
        """Set flood wait time for this account."""
        self.flood_wait_until = datetime.now() + timedelta(seconds=seconds)

# --- Constants ---
AVAILABLE_USERNAMES_FILE = "available.txt"
LOG_FILE = "checker.log"
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{5,32}$")

# --- Logging Setup ---
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
log_handler.setFormatter(log_formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)

# --- Helper Functions ---

def print_success(message: str):
    print(f"{colorama.Fore.GREEN}{message}")

def print_info(message: str):
    print(f"{colorama.Fore.YELLOW}{message}")

def print_error(message: str):
    print(f"{colorama.Fore.RED}{message}")

def print_cyan(message: str):
    print(f"{colorama.Fore.CYAN}{message}")

def print_magenta(message: str):
    print(f"{colorama.Fore.MAGENTA}{message}")

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print application banner."""
    banner = f"""{colorama.Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🔍 TELEGRAM USERNAME CHECKER PLUS v1.0 🔍         ║
║                      GitHub : xPOURY4                        ║
║                    Multi-Account Edition                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{colorama.Style.RESET_ALL}
    """
    print(banner)

def show_menu() -> int:
    """Display main menu and get user choice."""
    print_cyan("\n" + "="*50)
    print_cyan("         TELEGRAM USERNAME CHECKER PLUS")
    print_cyan("="*50)
    print(f"{Fore.WHITE}1. {Fore.CYAN}🚀 Start Username Checking")
    print(f"{Fore.WHITE}2. {Fore.GREEN}📊 View Account Status")
    print(f"{Fore.WHITE}3. {Fore.YELLOW}⚙️  Manage Accounts")
    print(f"{Fore.WHITE}4. {Fore.MAGENTA}🔧 Settings")
    print(f"{Fore.WHITE}5. {Fore.RED}❌ Exit")
    print_cyan("="*50)
    
    try:
        choice = int(input(f"{Fore.CYAN}Enter your choice (1-5): {Style.RESET_ALL}").strip())
        return choice
    except ValueError:
        return 0

def show_account_menu() -> int:
    """Display account management menu."""
    print_cyan("\n" + "="*40)
    print_cyan("        ACCOUNT MANAGEMENT")
    print_cyan("="*40)
    print(f"{Fore.WHITE}1. {Fore.GREEN}🔄 Enable/Disable Accounts")
    print(f"{Fore.WHITE}2. {Fore.CYAN}➕ Add New Account")
    print(f"{Fore.WHITE}3. {Fore.RED}🔙 Back to Main Menu")
    print_cyan("="*40)
    
    try:
        choice = int(input(f"{Fore.CYAN}Enter your choice (1-3): {Style.RESET_ALL}").strip())
        return choice
    except ValueError:
        return 0

def load_accounts() -> List[Account]:
    """Load all accounts from config.ini."""
    config = configparser.ConfigParser()
    if not Path("config.ini").exists():
        print_error("Error: config.ini not found!")
        logger.error("config.ini not found.")
        exit(1)
    config.read("config.ini")
    
    accounts = []
    for section_name in config.sections():
        if section_name.startswith('account'):
            try:
                account = Account(
                    name=section_name,
                    api_id=int(config[section_name]['api_id']),
                    api_hash=config[section_name]['api_hash'],
                    phone_number=config[section_name]['phone_number'],
                    enabled=config[section_name].getboolean('enabled', True)
                )
                accounts.append(account)
            except (KeyError, ValueError) as e:
                print_error(f"Error loading account {section_name}: {e}")
                logger.error(f"Error loading account {section_name}: {e}")
    
    if not accounts:
        print_error("No valid accounts found in config.ini!")
        exit(1)
    
    return accounts

def load_config() -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Load proxy and settings configuration from config.ini."""
    config = configparser.ConfigParser()
    
    if not os.path.exists('config.ini'):
        print_error("config.ini file not found!")
        return None, None
    
    try:
        config.read('config.ini', encoding='utf-8')
        
        # Load proxy settings
        proxy_config = None
        if 'proxy' in config and config.getboolean('proxy', 'enabled', fallback=False):
            proxy_config = {
                'enabled': True,
                'proxy_type': config.get('proxy', 'proxy_type', fallback='socks5'),
                'addr': config.get('proxy', 'addr', fallback='127.0.0.1'),
                'port': config.get('proxy', 'port', fallback='1080'),
                'username': config.get('proxy', 'username', fallback=''),
                'password': config.get('proxy', 'password', fallback='')
            }
        
        # Load settings
        settings_config = {
            'max_concurrency': config.getint('settings', 'max_concurrency', fallback=6)
        }
        
        return proxy_config, settings_config
        
    except Exception as e:
        print_error(f"Error reading config.ini: {e}")
        logger.error(f"Error reading config.ini: {e}")
        return None, None

def display_accounts(accounts: List[Account]):
    """Display account status."""
    print_cyan("\n" + "="*80)
    print_cyan("                              ACCOUNT STATUS")
    print_cyan("="*80)
    print(f"{colorama.Fore.WHITE}{'Name':<12} {'Phone':<15} {'Status':<10} {'Flood Wait':<15} {'API ID':<10}")
    print_cyan("-"*80)
    
    for account in accounts:
        status = f"{colorama.Fore.GREEN}Enabled" if account.enabled else f"{colorama.Fore.RED}Disabled"
        flood_status = "None"
        if account.flood_wait_until:
            remaining = account.flood_wait_until - datetime.now()
            if remaining.total_seconds() > 0:
                flood_status = f"{colorama.Fore.RED}{int(remaining.total_seconds())}s"
            else:
                flood_status = f"{colorama.Fore.GREEN}Ready"
        else:
            flood_status = f"{colorama.Fore.GREEN}Ready"
        
        print(f"{colorama.Fore.WHITE}{account.name:<12} {account.phone_number:<15} {status:<20} {flood_status:<25} {account.api_id}")
    
    print_cyan("="*80)

def is_valid_username(username: str) -> bool:
    """Checks if a username has a valid format."""
    return bool(USERNAME_REGEX.match(username))

def load_proxies() -> list:
    """Loads proxies from proxies.txt file."""
    proxies = []
    proxy_file = Path("proxies.txt")
    
    if not proxy_file.exists():
        print_info("No proxies.txt file found. Running without proxy.")
        return proxies
    
    try:
        with open(proxy_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    parts = line.split(':')
                    if len(parts) < 3:
                        print_error(f"Invalid proxy format at line {line_num}: {line}")
                        continue
                    
                    proxy_type = parts[0].lower()
                    addr = parts[1]
                    port = int(parts[2])
                    username = parts[3] if len(parts) > 3 and parts[3] else None
                    password = parts[4] if len(parts) > 4 and parts[4] else None
                    
                    proxies.append({
                        'type': proxy_type,
                        'addr': addr,
                        'port': port,
                        'username': username,
                        'password': password
                    })
                    
                except (ValueError, IndexError) as e:
                    print_error(f"Error parsing proxy at line {line_num}: {line} - {e}")
                    continue
        
        print_info(f"Loaded {len(proxies)} proxies from proxies.txt")
        return proxies
        
    except Exception as e:
        print_error(f"Error reading proxies.txt: {e}")
        return []

async def check_username_with_account(account: Account, username: str, semaphore: asyncio.Semaphore) -> bool:
    """Check a single username using a specific account."""
    async with semaphore:
        try:
            if not account.is_available():
                return False
            
            result = await account.client(CheckUsernameRequest(username))
            if not result:  # False means username is available/free
                print_success(f"[+] Username '{username}' is available! (Account: {account.name})")
                logger.info(f"Username '{username}' is available. (Account: {account.name})")
                with open(AVAILABLE_USERNAMES_FILE, "a", encoding="utf-8") as f:
                    f.write(f"{username}\n")
                return True
            else:
                # True means username is taken/occupied
                print_error(f"[-] Username '{username}' is taken. (Account: {account.name})")
                logger.info(f"Username '{username}' is taken. (Account: {account.name})")
                return True
                
        except FloodWaitError as e:
            print_error(f"Flood wait error for '{username}' on {account.name}. Waiting {e.seconds} seconds...")
            logger.warning(f"Flood wait for {e.seconds}s on username '{username}' (Account: {account.name}).")
            account.set_flood_wait(e.seconds + random.randint(5, 15))  # Add extra buffer
            return False
            
        except (UsernameInvalidError, UsernameNotModifiedError, UsernameOccupiedError):
            # These are expected errors for invalid/taken usernames, no need to log as errors.
            logger.info(f"Username '{username}' is invalid or occupied. (Account: {account.name})")
            return True
            
        except Exception as e:
            print_error(f"An unexpected error occurred for '{username}' on {account.name}: {e}")
            logger.error(f"Unexpected error for '{username}' (Account: {account.name}): {e}", exc_info=True)
            return False
            
        finally:
            # Smart delay based on account count
            delay = random.uniform(3, 6)  # Reduced delay for multi-account
            await asyncio.sleep(delay)

class UsernameDistributor:
    """Distributes usernames among available accounts."""
    
    def __init__(self, accounts: List[Account]):
        self.accounts = accounts
        self.username_queue = asyncio.Queue()
        self.results = []
        
    async def add_usernames(self, usernames: List[str]):
        """Add usernames to the queue."""
        for username in usernames:
            await self.username_queue.put(username)
    
    async def worker(self, account: Account, semaphore: asyncio.Semaphore):
        """Worker function for each account."""
        while True:
            try:
                # Get username from queue with timeout
                username = await asyncio.wait_for(self.username_queue.get(), timeout=1.0)
                
                if not account.is_available():
                    # Put username back in queue if account is not available
                    await self.username_queue.put(username)
                    await asyncio.sleep(5)  # Wait before trying again
                    continue
                
                result = await check_username_with_account(account, username, semaphore)
                self.results.append((username, result, account.name))
                self.username_queue.task_done()
                
            except asyncio.TimeoutError:
                # No more usernames in queue
                break
            except Exception as e:
                logger.error(f"Worker error for account {account.name}: {e}")
                await asyncio.sleep(5)

async def setup_accounts(accounts: List[Account], proxy_config: dict = None) -> List[Account]:
    """Setup and authenticate all accounts."""
    active_accounts = []
    
    for account in accounts:
        if not account.enabled:
            continue
            
        try:
            print_info(f"Setting up account: {account.name}")
            
            # Create client with proxy support
            if proxy_config:
                import socks
                proxy_type = socks.SOCKS5 if proxy_config['type'].lower() == 'socks5' else socks.HTTP
                proxy = (proxy_type, proxy_config['addr'], int(proxy_config['port']))
                if proxy_config.get('username') and proxy_config.get('password'):
                    proxy = (proxy_type, proxy_config['addr'], int(proxy_config['port']), 
                            True, proxy_config['username'], proxy_config['password'])
                account.client = TelegramClient(f'{account.name}_session', account.api_id, 
                                              account.api_hash, proxy=proxy)
            else:
                account.client = TelegramClient(f'{account.name}_session', account.api_id, 
                                              account.api_hash)
            
            # Start the client
            await account.client.start(phone=account.phone_number)
            print_success(f"✓ Account {account.name} connected successfully!")
            active_accounts.append(account)
            
        except Exception as e:
            print_error(f"✗ Failed to setup account {account.name}: {e}")
            logger.error(f"Failed to setup account {account.name}: {e}")
    
    return active_accounts

async def run_username_checker(accounts: List[Account], usernames_file: str):
    """Run the username checker with multi-account support."""
    try:
        # Read usernames from file
        try:
            with open(usernames_file, "r", encoding="utf-8") as f:
                usernames = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print_error(f"File '{usernames_file}' not found.")
            return
        except Exception as e:
            print_error(f"Error reading file '{usernames_file}': {e}")
            return

        # Filter valid usernames
        valid_usernames = [username for username in usernames if is_valid_username(username)]
        invalid_count = len(usernames) - len(valid_usernames)
        
        if invalid_count > 0:
            print_info(f"Filtered out {invalid_count} invalid usernames.")
        
        if not valid_usernames:
            print_error("No valid usernames to check.")
            return

        print_info(f"Checking {len(valid_usernames)} usernames with {len(accounts)} accounts...")
        
        # Load configuration for settings
        _, settings_config = load_config()
        max_concurrency = int(settings_config.get('max_concurrency', 6))
        
        # Create distributor and add usernames
        distributor = UsernameDistributor(accounts)
        await distributor.add_usernames(valid_usernames)
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrency)
        
        # Start workers for each account
        tasks = []
        for account in accounts:
            task = asyncio.create_task(distributor.worker(account, semaphore))
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Wait for queue to be empty
        await distributor.username_queue.join()
        
        # Disconnect all clients
        for account in accounts:
            if account.client:
                await account.client.disconnect()
        
        # Show results
        available_count = 0
        if Path(AVAILABLE_USERNAMES_FILE).exists():
            with open(AVAILABLE_USERNAMES_FILE, 'r', encoding='utf-8') as f:
                available_count = len(f.readlines())
        
        print_success(f"\n✓ Username checking completed!")
        print_info(f"Total checked: {len(valid_usernames)}")
        print_success(f"Available usernames: {available_count}")
        print_info(f"Check '{AVAILABLE_USERNAMES_FILE}' for available usernames.")
        
    except KeyboardInterrupt:
        print_error("\nOperation cancelled by user.")
        # Disconnect all clients
        for account in accounts:
            if account.client:
                await account.client.disconnect()
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
        logger.error(f"Unexpected error in run_username_checker: {e}", exc_info=True)

async def main():
    """Main function with beautiful menu system."""
    clear_screen()
    print_banner()
    
    try:
        # Load accounts and configuration
        accounts = load_accounts()
        if not accounts:
            print_error("No accounts found in config.ini. Please configure at least one account.")
            input("\nPress Enter to exit...")
            return
        
        proxy_config, _ = load_config()
        
        # Load proxy settings
        proxy_settings = None
        if proxy_config and proxy_config.get('addr'):
            proxy_settings = {
                'type': proxy_config.get('proxy_type', 'socks5'),
                'addr': proxy_config.get('addr'),
                'port': proxy_config.get('port', 1080),
                'username': proxy_config.get('username'),
                'password': proxy_config.get('password')
            }
        else:
            # Try to load from proxies.txt if no proxy in config
            proxies = load_proxies()
            if proxies:
                proxy_settings = proxies[0]  # Use first proxy from list
        
        while True:
            clear_screen()
            print_banner()
            
            choice = show_menu()
            
            if choice == 1:
                # Start Username Checking
                clear_screen()
                print_banner()
                print_cyan("🔧 Setting up accounts...")
                
                active_accounts = await setup_accounts(accounts, proxy_settings)
                
                if not active_accounts:
                    print_error("No accounts could be set up. Please check your configuration.")
                    input("\nPress Enter to continue...")
                    continue
                
                print_success(f"\n✓ {len(active_accounts)} accounts ready!")
                
                # Ask for usernames file
                usernames_file = input("\nEnter usernames file path (default: usernames.txt): ").strip()
                if not usernames_file:
                    usernames_file = "usernames.txt"
                
                await run_username_checker(active_accounts, usernames_file)
                input("\nPress Enter to continue...")
                
            elif choice == 2:
                # View Account Status
                clear_screen()
                print_banner()
                display_accounts(accounts)
                input("\nPress Enter to continue...")
                
            elif choice == 3:
                # Manage Accounts
                clear_screen()
                print_banner()
                account_choice = show_account_menu()
                
                if account_choice == 1:
                    # Enable/Disable Accounts
                    clear_screen()
                    print_banner()
                    display_accounts(accounts)
                    try:
                        account_num = int(input("\nEnter account number to toggle (0 to cancel): "))
                        if 1 <= account_num <= len(accounts):
                            account = accounts[account_num - 1]
                            account.enabled = not account.enabled
                            print_success(f"Account {account.name} {'enabled' if account.enabled else 'disabled'}!")
                        elif account_num != 0:
                            print_error("Invalid account number.")
                    except ValueError:
                        print_error("Please enter a valid number.")
                    input("\nPress Enter to continue...")
                
                elif account_choice == 2:
                    # Add New Account (placeholder)
                    print_info("Add new account feature coming soon!")
                    input("\nPress Enter to continue...")
                
            elif choice == 4:
                # Settings
                print_info("Settings menu coming soon!")
                input("\nPress Enter to continue...")
                
            elif choice == 5:
                # Exit
                print_cyan("\n👋 Goodbye!")
                break
                
    except KeyboardInterrupt:
        print_error("\nOperation cancelled by user.")
    except Exception as e:
        print_error(f"An unexpected error occurred: {e}")
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (ValueError, configparser.NoSectionError, configparser.NoOptionError) as e:
        print_error(f"Configuration Error: Please check your config.ini. Details: {e}")
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        print_error(f"An unexpected error occurred during execution: {e}")
        logger.critical(f"Unhandled exception: {e}", exc_info=True)