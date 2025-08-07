# 🚀 Telegram Username Checker Plus v2.3

**The Ultimate Cross-Platform Multi-Account Telegram Username Availability Checker with Cloud Integration & API**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Telethon](https://img.shields.io/badge/Telethon-1.35%2B-green.svg)](https://github.com/LonamiWebs/Telethon)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.3.0-red.svg)](https://github.com/xPOURY4/telegram-username-checker)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/xPOURY4/telegram-username-checker)
[![API](https://img.shields.io/badge/API-REST%20v1-orange.svg)](https://github.com/xPOURY4/telegram-username-checker)
[![Cloud](https://img.shields.io/badge/Cloud-AWS%20%7C%20GCP%20%7C%20Azure-blue.svg)](https://github.com/xPOURY4/telegram-username-checker)

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🎯 What's New in v2.3](#-whats-new-in-v23)
- [📊 Performance](#-performance)
- [🔧 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🚀 Usage](#-usage)
- [🔄 Multi-Account Setup](#-multi-account-setup)
- [🌐 Proxy Support](#-proxy-support)
- [☁️ Cloud Integration](#️-cloud-integration)
- [🌐 REST API](#-rest-api)
- [🔌 Plugin System](#-plugin-system)
- [📈 Performance Tuning](#-performance-tuning)
- [🖥️ Cross-Platform Support](#️-cross-platform-support)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [📞 Support](#-support)

---

## ✨ Features

### 🔥 Core Features
- **🌍 Cross-Platform Support**: Windows, Linux, and macOS compatibility
- **👥 Multi-Account Support**: Use multiple Telegram accounts simultaneously
- **⚡ High-Speed Checking**: Optimized for maximum performance with platform-specific tuning
- **🧠 Smart FloodWait Management**: AI-powered rate limit handling
- **📊 Real-time Statistics**: Live performance monitoring with advanced analytics
- **🌐 Proxy Support**: SOCKS5, SOCKS4, HTTP, and MTProxy compatibility
- **🎨 Professional UI**: Clean and intuitive command-line interface
- **📝 Detailed Logging**: Comprehensive logging system with multiple levels
- **🔄 Error Recovery**: Automatic retry mechanisms with exponential backoff

### 🚀 Advanced Features v2.3
- **☁️ Cloud Integration**: AWS S3, Google Cloud, Azure Blob Storage support
- **🌐 REST API**: Full-featured API for external integrations
- **🔌 Plugin System**: Extensible architecture with custom plugins
- **🔐 Advanced Security**: End-to-end encryption for sensitive data
- **📈 Performance Monitor**: Real-time performance analytics and optimization
- **🤖 Auto-Optimization**: Platform-specific performance tuning
- **💾 Smart Backup**: Automated cloud backup with versioning
- **🔄 Load Balancing**: Intelligent distribution across accounts and platforms
- **📊 Advanced Analytics**: Comprehensive performance metrics and reporting
- **🛡️ Session Security**: Enhanced session management with encryption
- **🎯 Batch Processing**: Efficient bulk username checking with queue management
- **📤 Export Capabilities**: Multiple output formats (JSON, CSV, XML)
- **🔧 Hot Configuration**: Runtime configuration updates without restart

## 🎯 What's New in v2.3

### 🌍 Cross-Platform Revolution
- **Full Linux Support**: Native compatibility with all major Linux distributions
- **macOS Integration**: Seamless operation on macOS with optimized performance
- **Platform Detection**: Automatic detection and optimization for each platform
- **Universal Installer**: Single installation process across all platforms

### ☁️ Cloud & Enterprise Features
- **Multi-Cloud Support**: AWS S3, Google Cloud Storage, Azure Blob Storage
- **Automated Backups**: Scheduled backups with retention policies
- **Data Encryption**: AES-256 encryption for all sensitive data
- **Sync Across Devices**: Seamless configuration and data synchronization

### 🌐 REST API & Integration
- **RESTful API**: Complete API for external application integration
- **Webhook Support**: Real-time notifications and event handling
- **Rate Limiting**: Built-in API rate limiting and security
- **Documentation**: Comprehensive API documentation with examples

### 🔌 Plugin Ecosystem
- **Plugin Architecture**: Extensible plugin system for custom functionality
- **Hook System**: Pre and post-processing hooks for custom logic
- **Sample Plugins**: Ready-to-use plugins for common tasks
- **Plugin Manager**: Easy installation and management of plugins

### 📈 Advanced Analytics
- **Performance Monitoring**: Real-time performance metrics and analytics
- **Predictive Analysis**: AI-powered FloodWait prediction
- **Custom Reports**: Detailed performance reports with export options
- **Live Dashboard**: Real-time monitoring dashboard

### 🔐 Security Enhancements
- **Enhanced Encryption**: Improved encryption for session data
- **Secure API**: API authentication and authorization
- **Audit Logging**: Comprehensive audit trails
- **Security Policies**: Configurable security policies

## 📋 Prerequisites

- Python 3.11+ (64-bit)
- Telegram account
- API credentials from [my.telegram.org](https://my.telegram.org)

## 🚀 Installation & Setup

### 1. Clone the Project
```bash
git clone https://github.com/xPOURY4/telegram-username-checker-plus.git
cd telegram-username-checker-plus
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Get API Credentials
1. Go to [my.telegram.org](https://my.telegram.org)
2. Login with your phone number
3. Click on "API development tools"
4. Create a new application
5. Copy your `api_id` and `api_hash`

### 4. Configuration

#### Multi-Account Setup

Edit the `config.ini` file to add multiple Telegram accounts:

```ini
[account1]
api_id = YOUR_API_ID_1
api_hash = YOUR_API_HASH_1
phone_number = YOUR_PHONE_NUMBER_1
enabled = true

[account2]
api_id = YOUR_API_ID_2
api_hash = YOUR_API_HASH_2
phone_number = YOUR_PHONE_NUMBER_2
enabled = true

[account3]
api_id = YOUR_API_ID_3
api_hash = YOUR_API_HASH_3
phone_number = YOUR_PHONE_NUMBER_3
enabled = false

[proxy]
enabled = false
proxy_type = socks5
addr = 127.0.0.1
port = 1080
username = 
password = 

[settings]
max_concurrency = 6
```

#### Account Management
- Add as many accounts as needed (account1, account2, account3, etc.)
- Set `enabled = true/false` to activate/deactivate accounts
- Each account requires valid `api_id`, `api_hash`, and `phone_number`
- The program will automatically distribute username checks among active accounts

## 💻 Usage

### Interactive Menu
```bash
python checker.py
```

The program will display a beautiful interactive menu:

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🔍 TELEGRAM USERNAME CHECKER PLUS v1.0 🔍         ║
║                                                              ║
║                    Multi-Account Edition                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

==================================================
         TELEGRAM USERNAME CHECKER PLUS
==================================================
1. 🚀 Start Username Checking
2. 📊 View Account Status
3. ⚙️  Manage Accounts
4. 🔧 Settings
5. ❌ Exit
==================================================
```

### Menu Options

1. **🚀 Start Username Checking**: Begin checking usernames from file
2. **📊 View Account Status**: Display all accounts and their status
3. **⚙️ Manage Accounts**: Enable/disable accounts or add new ones
4. **🔧 Settings**: Configure application settings
5. **❌ Exit**: Close the application

### Input File Format
The `usernames.txt` file should contain one username per line:
```
testuser123
availableusername
freeusername2024
```

### Example Output
```
[+] Username 'available_username' is available! (Account: account1)
[-] Username 'taken_username' is taken. (Account: account2)
[+] Username 'free_username' is available! (Account: account1)
Flood wait error for 'test_username' on account2. Waiting 30 seconds...
```

### Output Files
- Available usernames are saved to `available.txt`
- Complete logs are recorded in `checker.log`

## ⚙️ Advanced Settings

### Multi-Account Configuration

#### Adding Multiple Accounts
```ini
[account1]
api_id = 12345678
api_hash = abcdef1234567890abcdef1234567890
phone_number = +1234567890
enabled = true

[account2]
api_id = 87654321
api_hash = 1234567890abcdef1234567890abcdef
phone_number = +0987654321
enabled = true

[account3]
api_id = 11223344
api_hash = fedcba0987654321fedcba0987654321
phone_number = +1122334455
enabled = false  # Disabled account
```

### Proxy Configuration (Optional)

#### Method 1: Using config.ini
```ini
[proxy]
enabled = true
proxy_type = socks5
addr = 127.0.0.1
port = 1080
username = your_username
password = your_password
```

#### Method 2: Using proxies.txt file
Create a `proxies.txt` file with multiple proxies (one per line):
```
# Format: proxy_type:address:port:username:password
socks5:127.0.0.1:1080::
socks5:proxy1.example.com:1080:user1:pass1
http:proxy2.example.com:8080::
```
The application will automatically try proxies from this file if no proxy is configured in config.ini.

### Performance Tuning
- Adjust `max_concurrency` in config.ini (default: 6)
- Add more accounts for higher throughput
- Enable/disable accounts based on their rate limit status
- Higher concurrency = faster checking but more risk of rate limits
- More accounts = better FloodWait management and higher speed

### Build Executable
```bash
pip install pyinstaller
pyinstaller --onefile --name=UsernameChecker checker.py
```

## 📊 Performance

### Multi-Account Advantages
- **Speed**: 500+ usernames per hour with multiple accounts
- **Concurrency**: Up to 6 parallel workers per account
- **FloodWait Management**: Automatic account switching when rate limited
- **Efficiency**: Smart delay management (3-6 seconds per check with multi-account)
- **Reliability**: Automatic retry and account rotation
- **Scalability**: Add more accounts for higher throughput

### Performance Metrics
- **Single Account**: ~300 usernames/hour
- **3 Accounts**: ~800 usernames/hour
- **5+ Accounts**: 1000+ usernames/hour
- **Memory**: Low memory footprint with efficient processing

## 🌐 Proxy Support

The application supports various proxy types for enhanced privacy and bypassing restrictions.

### Supported Proxy Types
- **SOCKS5**: Most recommended for Telegram (with authentication)
- **SOCKS4**: Basic SOCKS support
- **HTTP**: Standard HTTP proxy
- **MTProxy**: Telegram's native proxy protocol

### Proxy Configuration

1. **Create proxies.txt** (optional):
```
socks5://username:password@proxy1.example.com:1080
socks5://proxy2.example.com:1080
http://proxy3.example.com:8080
mtproxy://secret@proxy4.example.com:443
```

2. **Enable in config.ini**:
```ini
[GENERAL]
use_proxy = true
proxy_rotation = true
```

### Proxy Features
- **Automatic Rotation**: Rotate proxies for each account
- **Health Checking**: Automatic proxy health monitoring
- **Failover**: Automatic failover to working proxies
- **Load Balancing**: Distribute load across multiple proxies
- **Geo-Location**: Proxy selection based on geographic location
- **Performance Monitoring**: Track proxy performance metrics

## ☁️ Cloud Integration

### Supported Cloud Providers
- **AWS S3**: Amazon Simple Storage Service
- **Google Cloud Storage**: Google's cloud storage solution
- **Azure Blob Storage**: Microsoft's cloud storage
- **Dropbox**: Popular cloud storage service
- **OneDrive**: Microsoft's personal cloud storage

### Cloud Features
- **Automatic Backup**: Scheduled backups of accounts and settings
- **Cross-Device Sync**: Synchronize data across multiple devices
- **Version Control**: Keep multiple versions of backups
- **Encryption**: All data encrypted before upload
- **Compression**: Reduce storage costs with compression

### Cloud Configuration

1. **Edit cloud_config.json**:
```json
{
  "cloud_settings": {
    "enabled": true,
    "provider": "aws_s3",
    "auto_backup": true,
    "backup_interval": 3600
  },
  "providers": {
    "aws_s3": {
      "enabled": true,
      "bucket_name": "your-bucket-name",
      "region": "us-east-1",
      "access_key_id": "your-access-key",
      "secret_access_key": "your-secret-key"
    }
  }
}
```

2. **Enable in Application**:
- Go to "Cloud & Backup Management" menu
- Configure your preferred cloud provider
- Test connection and start syncing

## 🌐 REST API

### API Endpoints

#### Check Username
```http
POST /api/v1/check
Content-Type: application/json
X-API-Key: your-api-key

{
  "username": "testuser",
  "account": "account1"
}
```

#### Bulk Check
```http
POST /api/v1/bulk-check
Content-Type: application/json
X-API-Key: your-api-key

{
  "usernames": ["user1", "user2", "user3"],
  "max_concurrent": 5
}
```

#### Account Status
```http
GET /api/v1/accounts
X-API-Key: your-api-key
```

#### Statistics
```http
GET /api/v1/stats
X-API-Key: your-api-key
```

### API Features
- **RESTful Design**: Standard REST API principles
- **Authentication**: API key-based authentication
- **Rate Limiting**: Configurable rate limits
- **Webhooks**: Real-time event notifications
- **Documentation**: Interactive API documentation
- **CORS Support**: Cross-origin resource sharing

### Starting API Server

1. **Via Menu**: Go to "API Server Management" → "Start API Server"
2. **Via Config**: Set `api_enabled = true` in config.ini
3. **Command Line**: Use `--api` flag when starting

## 🔌 Plugin System

### Plugin Architecture
The plugin system allows you to extend functionality without modifying core code.

### Available Hooks
- **on_startup**: Called when application starts
- **on_shutdown**: Called when application shuts down
- **before_check**: Called before checking a username
- **after_check**: Called after checking a username
- **on_flood_wait**: Called when FloodWait occurs
- **on_account_switch**: Called when switching accounts

### Creating a Plugin

1. **Create plugin file** in `plugins/` directory:
```python
class MyPlugin:
    def __init__(self):
        self.name = "My Plugin"
        self.version = "1.0.0"
    
    def on_startup(self, *args, **kwargs):
        print(f"{self.name} loaded!")
    
    def before_check(self, username, account, *args, **kwargs):
        print(f"Checking {username} with {account}")
        return True  # Continue with check

def get_plugin():
    return MyPlugin()
```

2. **Plugin will be auto-loaded** on next startup

### Plugin Management
- **List Plugins**: View all installed plugins
- **Enable/Disable**: Control plugin activation
- **Configuration**: Configure plugin settings
- **Statistics**: View plugin performance metrics

## 🖥️ Cross-Platform Support

### Supported Platforms
- **Windows**: Windows 10/11 (x64)
- **Linux**: Ubuntu, Debian, CentOS, Fedora, Arch Linux
- **macOS**: macOS 10.15+ (Intel and Apple Silicon)

### Platform-Specific Features

#### Windows
- **Native Console**: Full Windows Console API support
- **Service Mode**: Run as Windows Service
- **Registry Integration**: Store settings in Windows Registry
- **Performance**: Optimized for Windows threading model

#### Linux
- **Systemd Integration**: Run as systemd service
- **Package Managers**: Support for apt, yum, pacman
- **Performance**: Optimized for Linux kernel
- **Container Support**: Docker and Podman compatibility

#### macOS
- **LaunchAgent**: Run as macOS LaunchAgent
- **Keychain Integration**: Secure credential storage
- **Apple Silicon**: Native ARM64 support
- **Performance**: Optimized for macOS threading

### Installation by Platform

#### Windows
```powershell
# Download and extract
Invoke-WebRequest -Uri "https://github.com/xPOURY4/telegram-username-checker/releases/latest/download/telegram-checker-windows.zip" -OutFile "telegram-checker.zip"
Expand-Archive -Path "telegram-checker.zip" -DestinationPath "C:\TelegramChecker"
cd "C:\TelegramChecker"

# Install dependencies
pip install -r requirements.txt

# Run
python checker.py
```

#### Linux
```bash
# Download and extract
wget https://github.com/xPOURY4/telegram-username-checker/releases/latest/download/telegram-checker-linux.tar.gz
tar -xzf telegram-checker-linux.tar.gz
cd telegram-checker

# Install dependencies
pip3 install -r requirements.txt

# Run
python3 checker.py
```

#### macOS
```bash
# Download and extract
curl -L https://github.com/xPOURY4/telegram-username-checker/releases/latest/download/telegram-checker-macos.tar.gz -o telegram-checker.tar.gz
tar -xzf telegram-checker.tar.gz
cd telegram-checker

# Install dependencies
pip3 install -r requirements.txt

# Run
python3 checker.py
```

## 🛠️ Project Structure

```
├── checker.py          # Main application file
├── config.ini          # Configuration file
├── requirements.txt    # Python dependencies
├── usernames.txt       # Sample input file
├── proxies.txt         # Proxy list file (optional)
├── available.txt       # Available usernames output
├── checker.log         # Log file
└── README.md          # Documentation
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the project
2. Create a new branch
3. Commit your changes
4. Submit a Pull Request

## 📄 License

This project is released under the MIT License.

## 👨‍💻 Author

**Pourya**
- GitHub: [@xPOURY4](https://github.com/xPOURY4)
- Twitter: [@TheRealPourya](https://twitter.com/TheRealPourya)

---

<div align="center">

⭐ If this project was helpful to you, please give it a star!

</div>
