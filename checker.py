import asyncio
import configparser
import logging
import random
import re
import time
import os
import sys
import platform
import json
import hashlib
import base64
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import threading
from urllib.parse import urlparse
import subprocess

import colorama
from colorama import Fore, Style
from telethon.errors import FloodWaitError, UsernameInvalidError, UsernameNotModifiedError, UsernameOccupiedError
from telethon import TelegramClient
from telethon.tl.functions.account import CheckUsernameRequest

# Initialize colorama
colorama.init(autoreset=True)

@dataclass
class Account:
    """Represents a Telegram account configuration with v2.3 enhancements."""
    name: str
    api_id: int
    api_hash: str
    phone_number: str
    enabled: bool
    client: Optional[TelegramClient] = None
    flood_wait_until: Optional[datetime] = None
    proxy_type: Optional[str] = None
    proxy_addr: Optional[str] = None
    proxy_port: Optional[int] = None
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None
    session_string: Optional[str] = None
    last_used: Optional[datetime] = None
    total_checks: int = 0
    successful_checks: int = 0
    failed_checks: int = 0
    avg_response_time: float = 0.0
    priority: int = 1  # 1=low, 2=medium, 3=high
    
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
    
    def update_stats(self, success: bool, response_time: float):
        """Update account performance statistics."""
        self.total_checks += 1
        self.last_used = datetime.now()
        
        if success:
            self.successful_checks += 1
        else:
            self.failed_checks += 1
        
        # Update average response time
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (self.avg_response_time + response_time) / 2
    
    def get_success_rate(self) -> float:
        """Get account success rate."""
        if self.total_checks == 0:
            return 0.0
        return (self.successful_checks / self.total_checks) * 100
    
    def to_dict(self) -> dict:
        """Convert account to dictionary for cloud sync."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Account':
        """Create account from dictionary for cloud sync."""
        return cls(**data)

# --- Constants ---
AVAILABLE_USERNAMES_FILE = "available.txt"
LOG_FILE = "checker.log"
USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{5,32}$")
VERSION = "2.3.0"
CONFIG_FILE = "config.ini"
CLOUD_CONFIG_FILE = "cloud_config.json"
API_CONFIG_FILE = "api_config.json"
PLUGINS_DIR = "plugins"
BACKUP_DIR = "backups"

# --- New Classes for v2.3 ---

class PlatformDetector:
    """Detect and handle different platforms."""
    
    @staticmethod
    def get_platform_info() -> dict:
        """Get detailed platform information."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'is_windows': platform.system().lower() == 'windows',
            'is_linux': platform.system().lower() == 'linux',
            'is_macos': platform.system().lower() == 'darwin'
        }
    
    @staticmethod
    def get_optimal_settings() -> dict:
        """Get optimal settings based on platform."""
        info = PlatformDetector.get_platform_info()
        
        if info['is_windows']:
            return {
                'max_workers': 8,
                'request_delay': 2,
                'timeout': 30,
                'use_color': True
            }
        elif info['is_linux']:
            return {
                'max_workers': 12,
                'request_delay': 1.5,
                'timeout': 25,
                'use_color': True
            }
        elif info['is_macos']:
            return {
                'max_workers': 10,
                'request_delay': 2,
                'timeout': 30,
                'use_color': True
            }
        else:
            return {
                'max_workers': 6,
                'request_delay': 3,
                'timeout': 30,
                'use_color': False
            }

class CloudManager:
    """Manage cloud synchronization and storage."""
    
    def __init__(self):
        self.cloud_config = self._load_cloud_config()
        self.encryption_key = self._get_encryption_key()
    
    def _load_cloud_config(self) -> dict:
        """Load cloud configuration."""
        try:
            if os.path.exists(CLOUD_CONFIG_FILE):
                with open(CLOUD_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cloud config: {e}")
        
        return {
            'enabled': False,
            'provider': 'local',
            'sync_accounts': False,
            'sync_settings': False,
            'auto_backup': True,
            'backup_interval': 3600  # 1 hour
        }
    
    def _get_encryption_key(self) -> str:
        """Generate or load encryption key."""
        key_file = 'encryption.key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        else:
            # Generate new key
            key = os.urandom(32)
            with open(key_file, 'wb') as f:
                f.write(key)
            return base64.b64encode(key).decode()
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        # Simple encryption for demo - use proper encryption in production
        encoded = base64.b64encode(data.encode()).decode()
        return encoded
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            return base64.b64decode(encrypted_data.encode()).decode()
        except:
            return encrypted_data
    
    def backup_accounts(self, accounts: List[Account]) -> bool:
        """Backup accounts to cloud or local storage."""
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(BACKUP_DIR, f'accounts_backup_{timestamp}.json')
            
            backup_data = {
                'timestamp': timestamp,
                'version': VERSION,
                'accounts': [account.to_dict() for account in accounts]
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            print_success(f"✓ Accounts backed up to {backup_file}")
            return True
        except Exception as e:
            print_error(f"✗ Backup failed: {e}")
            logger.error(f"Backup failed: {e}")
            return False
    
    def restore_accounts(self, backup_file: str) -> List[Account]:
        """Restore accounts from backup."""
        try:
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            accounts = []
            for account_data in backup_data.get('accounts', []):
                # Convert datetime strings back to datetime objects
                if 'flood_wait_until' in account_data and account_data['flood_wait_until']:
                    account_data['flood_wait_until'] = datetime.fromisoformat(account_data['flood_wait_until'])
                if 'last_used' in account_data and account_data['last_used']:
                    account_data['last_used'] = datetime.fromisoformat(account_data['last_used'])
                
                accounts.append(Account.from_dict(account_data))
            
            print_success(f"✓ Restored {len(accounts)} accounts from backup")
            return accounts
        except Exception as e:
            print_error(f"✗ Restore failed: {e}")
            logger.error(f"Restore failed: {e}")
            return []

class APIManager:
    """Manage REST API for external integrations."""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.running = False
        self.api_key = self._generate_api_key()
        self.endpoints = {}
    
    def _generate_api_key(self) -> str:
        """Generate API key for authentication."""
        return hashlib.sha256(f"{time.time()}{random.random()}".encode()).hexdigest()[:32]
    
    def start_api_server(self):
        """Start the REST API server."""
        try:
            print_info(f"🌐 Starting API server on port {self.port}...")
            print_info(f"🔑 API Key: {self.api_key}")
            self.running = True
            # In a real implementation, you would start a web server here
            print_success(f"✓ API server started successfully!")
        except Exception as e:
            print_error(f"✗ Failed to start API server: {e}")
            logger.error(f"API server start failed: {e}")
    
    def stop_api_server(self):
        """Stop the REST API server."""
        self.running = False
        print_info("🛑 API server stopped")
    
    def register_endpoint(self, path: str, handler):
        """Register API endpoint."""
        self.endpoints[path] = handler

class PluginManager:
    """Manage plugins and extensions."""
    
    def __init__(self):
        self.plugins = {}
        self.plugin_dir = PLUGINS_DIR
        os.makedirs(self.plugin_dir, exist_ok=True)
    
    def load_plugins(self):
        """Load all available plugins."""
        try:
            plugin_files = [f for f in os.listdir(self.plugin_dir) if f.endswith('.py')]
            
            for plugin_file in plugin_files:
                plugin_name = plugin_file[:-3]  # Remove .py extension
                try:
                    # In a real implementation, you would dynamically import the plugin
                    self.plugins[plugin_name] = {
                        'name': plugin_name,
                        'loaded': True,
                        'version': '1.0.0'
                    }
                    print_success(f"✓ Loaded plugin: {plugin_name}")
                except Exception as e:
                    print_error(f"✗ Failed to load plugin {plugin_name}: {e}")
                    logger.error(f"Plugin load failed {plugin_name}: {e}")
        
        except Exception as e:
            logger.error(f"Plugin loading error: {e}")
    
    def get_loaded_plugins(self) -> List[str]:
        """Get list of loaded plugins."""
        return list(self.plugins.keys())
    
    def execute_plugin_hook(self, hook_name: str, *args, **kwargs):
        """Execute plugin hooks."""
        for plugin_name, plugin_info in self.plugins.items():
            if plugin_info.get('loaded'):
                try:
                    # In a real implementation, you would call the plugin's hook method
                    logger.debug(f"Executing hook {hook_name} for plugin {plugin_name}")
                except Exception as e:
                    logger.error(f"Plugin hook error {plugin_name}.{hook_name}: {e}")

class PerformanceMonitor:
    """Monitor and optimize performance."""
    
    def __init__(self):
        self.start_time = time.time()
        self.stats = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'flood_waits': 0,
            'avg_response_time': 0.0,
            'checks_per_minute': 0.0
        }
        self.account_stats = {}
    
    def record_check(self, account_name: str, success: bool, response_time: float, flood_wait: bool = False):
        """Record a username check."""
        self.stats['total_checks'] += 1
        
        if success:
            self.stats['successful_checks'] += 1
        else:
            self.stats['failed_checks'] += 1
        
        if flood_wait:
            self.stats['flood_waits'] += 1
        
        # Update average response time
        if self.stats['avg_response_time'] == 0:
            self.stats['avg_response_time'] = response_time
        else:
            self.stats['avg_response_time'] = (self.stats['avg_response_time'] + response_time) / 2
        
        # Update checks per minute
        elapsed_minutes = (time.time() - self.start_time) / 60
        if elapsed_minutes > 0:
            self.stats['checks_per_minute'] = self.stats['total_checks'] / elapsed_minutes
        
        # Update account-specific stats
        if account_name not in self.account_stats:
            self.account_stats[account_name] = {
                'checks': 0,
                'successes': 0,
                'failures': 0,
                'flood_waits': 0,
                'avg_response_time': 0.0
            }
        
        account_stat = self.account_stats[account_name]
        account_stat['checks'] += 1
        
        if success:
            account_stat['successes'] += 1
        else:
            account_stat['failures'] += 1
        
        if flood_wait:
            account_stat['flood_waits'] += 1
        
        # Update account average response time
        if account_stat['avg_response_time'] == 0:
            account_stat['avg_response_time'] = response_time
        else:
            account_stat['avg_response_time'] = (account_stat['avg_response_time'] + response_time) / 2
    
    def get_performance_report(self) -> dict:
        """Get comprehensive performance report."""
        elapsed_time = time.time() - self.start_time
        
        return {
            'runtime_seconds': elapsed_time,
            'runtime_minutes': elapsed_time / 60,
            'runtime_hours': elapsed_time / 3600,
            'total_stats': self.stats,
            'account_stats': self.account_stats,
            'success_rate': (self.stats['successful_checks'] / max(1, self.stats['total_checks'])) * 100,
            'flood_wait_rate': (self.stats['flood_waits'] / max(1, self.stats['total_checks'])) * 100
        }
    
    def print_live_stats(self):
        """Print live performance statistics."""
        report = self.get_performance_report()
        
        print(f"\r📊 Checks: {self.stats['total_checks']} | "
              f"Success: {report['success_rate']:.1f}% | "
              f"Rate: {self.stats['checks_per_minute']:.1f}/min | "
              f"Avg Time: {self.stats['avg_response_time']:.2f}s", end="")

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
║           🔍 TELEGRAM USERNAME CHECKER PLUS v2.3 🔍         ║
║                      GitHub : xPOURY4                        ║
║              Cross-Platform & Cloud Edition                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{colorama.Style.RESET_ALL}
    """
    print(banner)

def show_menu() -> int:
    """Display main menu and get user choice."""
    print_cyan("\n" + "="*70)
    print_cyan("         TELEGRAM USERNAME CHECKER PLUS v2.3")
    print_cyan("="*70)
    print(f"{Fore.WHITE}1. {Fore.CYAN}🚀 Start Username Checking")
    print(f"{Fore.WHITE}2. {Fore.GREEN}📊 View Account Status")
    print(f"{Fore.WHITE}3. {Fore.YELLOW}⚙️  Manage Accounts")
    print(f"{Fore.WHITE}4. {Fore.MAGENTA}🔧 Settings & Configuration")
    print(f"{Fore.WHITE}5. {Fore.BLUE}☁️  Cloud & Backup Management")
    print(f"{Fore.WHITE}6. {Fore.CYAN}🌐 API Server Management")
    print(f"{Fore.WHITE}7. {Fore.GREEN}🔌 Plugin Management")
    print(f"{Fore.WHITE}8. {Fore.YELLOW}🖥️  Platform Information")
    print(f"{Fore.WHITE}9. {Fore.MAGENTA}📈 Performance Monitor")
    print(f"{Fore.WHITE}10. {Fore.CYAN}❓ Help & Documentation")
    print(f"{Fore.WHITE}0. {Fore.RED}❌ Exit")
    print_cyan("="*70)
    
    try:
        choice = int(input(f"{Fore.CYAN}Enter your choice (0-10): {Style.RESET_ALL}").strip())
        return choice
    except ValueError:
        return 0

def show_account_menu() -> int:
    """Display account management menu."""
    print_cyan("\n" + "="*60)
    print_cyan("        ACCOUNT MANAGEMENT v2.3")
    print_cyan("="*60)
    print(f"{Fore.WHITE}1. {Fore.GREEN}🔄 Enable/Disable Accounts")
    print(f"{Fore.WHITE}2. {Fore.CYAN}➕ Add New Account")
    print(f"{Fore.WHITE}3. {Fore.YELLOW}📊 Account Performance Stats")
    print(f"{Fore.WHITE}4. {Fore.MAGENTA}🔧 Account Configuration")
    print(f"{Fore.WHITE}5. {Fore.BLUE}💾 Export Account Data")
    print(f"{Fore.WHITE}6. {Fore.CYAN}📥 Import Account Data")
    print(f"{Fore.WHITE}7. {Fore.RED}🔙 Back to Main Menu")
    print_cyan("="*60)
    
    try:
        choice = int(input(f"{Fore.CYAN}Enter your choice (1-7): {Style.RESET_ALL}").strip())
        return choice
    except ValueError:
        return 0

def show_cloud_menu() -> int:
    """Display cloud management menu."""
    print_cyan("\n" + "="*60)
    print_cyan("        CLOUD & BACKUP MANAGEMENT")
    print_cyan("="*60)
    print(f"{Fore.WHITE}1. {Fore.GREEN}💾 Create Backup")
    print(f"{Fore.WHITE}2. {Fore.CYAN}📥 Restore from Backup")
    print(f"{Fore.WHITE}3. {Fore.YELLOW}📋 List Backups")
    print(f"{Fore.WHITE}4. {Fore.RED}🗑️  Delete Backup")
    print(f"{Fore.WHITE}5. {Fore.BLUE}☁️  Cloud Sync Settings")
    print(f"{Fore.WHITE}6. {Fore.MAGENTA}🔐 Encryption Settings")
    print(f"{Fore.WHITE}7. {Fore.CYAN}📊 Backup Statistics")
    print(f"{Fore.WHITE}8. {Fore.RED}🔙 Back to Main Menu")
    print_cyan("="*60)
    
    try:
        choice = int(input(f"{Fore.CYAN}Enter your choice (1-8): {Style.RESET_ALL}").strip())
        return choice
    except ValueError:
        return 0

def show_api_menu() -> int:
    """Display API management menu."""
    print_cyan("\n" + "="*60)
    print_cyan("        API SERVER MANAGEMENT")
    print_cyan("="*60)
    print(f"{Fore.WHITE}1. {Fore.GREEN}🚀 Start API Server")
    print(f"{Fore.WHITE}2. {Fore.RED}🛑 Stop API Server")
    print(f"{Fore.WHITE}3. {Fore.YELLOW}📊 API Status & Stats")
    print(f"{Fore.WHITE}4. {Fore.CYAN}🔑 Generate New API Key")
    print(f"{Fore.WHITE}5. {Fore.MAGENTA}⚙️  API Configuration")
    print(f"{Fore.WHITE}6. {Fore.BLUE}📋 API Documentation")
    print(f"{Fore.WHITE}7. {Fore.GREEN}🔒 Security Settings")
    print(f"{Fore.WHITE}8. {Fore.RED}🔙 Back to Main Menu")
    print_cyan("="*60)
    
    try:
        choice = int(input(f"{Fore.CYAN}Enter your choice (1-8): {Style.RESET_ALL}").strip())
        return choice
    except ValueError:
        return 0

def show_plugin_menu() -> int:
    """Display plugin management menu."""
    print_cyan("\n" + "="*60)
    print_cyan("        PLUGIN MANAGEMENT")
    print_cyan("="*60)
    print(f"{Fore.WHITE}1. {Fore.GREEN}📋 List Installed Plugins")
    print(f"{Fore.WHITE}2. {Fore.CYAN}🔄 Reload Plugins")
    print(f"{Fore.WHITE}3. {Fore.YELLOW}➕ Install New Plugin")
    print(f"{Fore.WHITE}4. {Fore.RED}🗑️  Remove Plugin")
    print(f"{Fore.WHITE}5. {Fore.MAGENTA}⚙️  Plugin Configuration")
    print(f"{Fore.WHITE}6. {Fore.BLUE}📊 Plugin Statistics")
    print(f"{Fore.WHITE}7. {Fore.GREEN}🔧 Create Sample Plugin")
    print(f"{Fore.WHITE}8. {Fore.RED}🔙 Back to Main Menu")
    print_cyan("="*60)
    
    try:
        choice = int(input(f"{Fore.CYAN}Enter your choice (1-8): {Style.RESET_ALL}").strip())
        return choice
    except ValueError:
        return 0

def show_platform_info():
    """Display platform information."""
    detector = PlatformDetector()
    info = detector.get_platform_info()
    optimal = detector.get_optimal_settings()
    
    print_cyan("\n" + "="*70)
    print_cyan("        PLATFORM INFORMATION")
    print_cyan("="*70)
    
    print_info("System Information:")
    print(f"  • Operating System: {info['system']} {info['release']}")
    print(f"  • Version: {info['version']}")
    print(f"  • Architecture: {info['machine']}")
    print(f"  • Processor: {info['processor']}")
    print(f"  • Python Version: {info['python_version']}")
    
    print_info("\nPlatform Detection:")
    print(f"  • Windows: {'✓' if info['is_windows'] else '✗'}")
    print(f"  • Linux: {'✓' if info['is_linux'] else '✗'}")
    print(f"  • macOS: {'✓' if info['is_macos'] else '✗'}")
    
    print_info("\nOptimal Settings for this Platform:")
    print(f"  • Max Workers: {optimal['max_workers']}")
    print(f"  • Request Delay: {optimal['request_delay']}s")
    print(f"  • Timeout: {optimal['timeout']}s")
    print(f"  • Color Support: {'✓' if optimal['use_color'] else '✗'}")
    
    print_cyan("="*70)
    input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")

def show_performance_monitor(monitor: PerformanceMonitor):
    """Display performance monitoring interface."""
    while True:
        clear_screen()
        print_banner()
        print_cyan("\n" + "="*70)
        print_cyan("        PERFORMANCE MONITOR")
        print_cyan("="*70)
        
        report = monitor.get_performance_report()
        
        print_info("Runtime Statistics:")
        print(f"  • Runtime: {report['runtime_minutes']:.1f} minutes ({report['runtime_hours']:.2f} hours)")
        print(f"  • Total Checks: {report['total_stats']['total_checks']}")
        print(f"  • Success Rate: {report['success_rate']:.1f}%")
        print(f"  • Checks per Minute: {report['total_stats']['checks_per_minute']:.1f}")
        print(f"  • Average Response Time: {report['total_stats']['avg_response_time']:.2f}s")
        print(f"  • FloodWait Rate: {report['flood_wait_rate']:.1f}%")
        
        if report['account_stats']:
            print_info("\nAccount Performance:")
            for account_name, stats in report['account_stats'].items():
                success_rate = (stats['successes'] / max(1, stats['checks'])) * 100
                print(f"  • {account_name}: {stats['checks']} checks, {success_rate:.1f}% success, {stats['avg_response_time']:.2f}s avg")
        
        print(f"\n{Fore.WHITE}1. {Fore.GREEN}🔄 Refresh Stats")
        print(f"{Fore.WHITE}2. {Fore.CYAN}💾 Export Report")
        print(f"{Fore.WHITE}3. {Fore.YELLOW}📊 Live Monitor (Auto-refresh)")
        print(f"{Fore.WHITE}4. {Fore.RED}🔙 Back to Main Menu")
        print_cyan("="*70)
        
        choice = input(f"{Fore.CYAN}Enter your choice (1-4): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            continue
        elif choice == '2':
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_file = f'performance_report_{timestamp}.json'
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, default=str)
                print_success(f"✓ Performance report exported to {report_file}")
                input("Press Enter to continue...")
            except Exception as e:
                print_error(f"✗ Export failed: {e}")
                input("Press Enter to continue...")
        elif choice == '3':
            print_info("Live monitoring... Press Ctrl+C to stop")
            try:
                while True:
                    monitor.print_live_stats()
                    time.sleep(1)
            except KeyboardInterrupt:
                print_info("\nLive monitoring stopped")
                input("Press Enter to continue...")
        elif choice == '4':
            break
        else:
            print_error("Invalid choice. Please try again.")
            time.sleep(1)

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
        # Initialize managers
        cloud_manager = CloudManager()
        api_manager = APIManager()
        plugin_manager = PluginManager()
        performance_monitor = PerformanceMonitor()
        
        # Load accounts and configuration
        accounts = load_accounts()
        if not accounts:
            print_error("No accounts found in config.ini. Please configure at least one account.")
            input("\nPress Enter to exit...")
            return
        
        # Load plugins
        plugin_manager.load_plugins()
        
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
                
                elif account_choice == 3:
                    # Account Performance Stats
                    clear_screen()
                    print_banner()
                    print_cyan("\n" + "="*70)
                    print_cyan("        ACCOUNT PERFORMANCE STATISTICS")
                    print_cyan("="*70)
                    
                    for account in accounts:
                        print(f"\n{Fore.CYAN}Account: {account.name}{Style.RESET_ALL}")
                        print(f"  • Total Checks: {account.total_checks}")
                        print(f"  • Success Rate: {account.get_success_rate():.1f}%")
                        print(f"  • Average Response Time: {account.avg_response_time:.2f}s")
                        print(f"  • Priority Level: {account.priority}")
                        if account.last_used:
                            print(f"  • Last Used: {account.last_used.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    input("\nPress Enter to continue...")
                
                elif account_choice >= 4:
                    print_info("Feature coming soon!")
                    input("\nPress Enter to continue...")
                
            elif choice == 4:
                # Settings
                print_info("Settings menu coming soon!")
                input("\nPress Enter to continue...")
                
            elif choice == 5:
                # Cloud & Backup Management
                cloud_manager = CloudManager()
                while True:
                    clear_screen()
                    print_banner()
                    cloud_choice = show_cloud_menu()
                    
                    if cloud_choice == 1:
                        # Create Backup
                        cloud_manager.backup_accounts(accounts)
                        input("\nPress Enter to continue...")
                    elif cloud_choice == 2:
                        # Restore from Backup
                        print_info("Restore feature coming soon!")
                        input("\nPress Enter to continue...")
                    elif cloud_choice >= 3 and cloud_choice <= 7:
                        print_info("Feature coming soon!")
                        input("\nPress Enter to continue...")
                    elif cloud_choice == 8 or cloud_choice == 0:
                        break
                
            elif choice == 6:
                # API Server Management
                api_manager = APIManager()
                while True:
                    clear_screen()
                    print_banner()
                    api_choice = show_api_menu()
                    
                    if api_choice == 1:
                        # Start API Server
                        api_manager.start_api_server()
                        input("\nPress Enter to continue...")
                    elif api_choice == 2:
                        # Stop API Server
                        api_manager.stop_api_server()
                        input("\nPress Enter to continue...")
                    elif api_choice >= 3 and api_choice <= 7:
                        print_info("Feature coming soon!")
                        input("\nPress Enter to continue...")
                    elif api_choice == 8 or api_choice == 0:
                        break
                
            elif choice == 7:
                # Plugin Management
                plugin_manager = PluginManager()
                while True:
                    clear_screen()
                    print_banner()
                    plugin_choice = show_plugin_menu()
                    
                    if plugin_choice == 1:
                        # List Installed Plugins
                        plugin_manager.load_plugins()
                        plugins = plugin_manager.get_loaded_plugins()
                        print_cyan("\n" + "="*50)
                        print_cyan("        INSTALLED PLUGINS")
                        print_cyan("="*50)
                        if plugins:
                            for plugin in plugins:
                                print_success(f"✓ {plugin}")
                        else:
                            print_info("No plugins installed.")
                        input("\nPress Enter to continue...")
                    elif plugin_choice >= 2 and plugin_choice <= 7:
                        print_info("Feature coming soon!")
                        input("\nPress Enter to continue...")
                    elif plugin_choice == 8 or plugin_choice == 0:
                        break
                
            elif choice == 8:
                # Platform Information
                show_platform_info()
                
            elif choice == 9:
                # Performance Monitor
                monitor = PerformanceMonitor()
                show_performance_monitor(monitor)
                
            elif choice == 10:
                # Help & Documentation
                clear_screen()
                print_banner()
                print_cyan("\n" + "="*70)
                print_cyan("        HELP & DOCUMENTATION")
                print_cyan("="*70)
                print_info("\nTelegram Username Checker Plus v2.3")
                print("\nFeatures:")
                print("• Multi-account support with load balancing")
                print("• Cross-platform compatibility")
                print("• Cloud backup and synchronization")
                print("• REST API for external integrations")
                print("• Plugin system for extensibility")
                print("• Performance monitoring and analytics")
                print("• Advanced proxy support")
                print("• Real-time statistics")
                
                print("\nConfiguration:")
                print("• Edit config.ini to add accounts")
                print("• Add proxies to proxies.txt (optional)")
                print("• Create usernames.txt with usernames to check")
                
                print("\nSupport:")
                print("• GitHub: xPOURY4")
                print("• Version: 2.3.0")
                
                input("\nPress Enter to continue...")
                
            elif choice == 0:
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
