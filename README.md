# 🔍 Telegram Username Checker Plus

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Telethon](https://img.shields.io/badge/Telethon-1.35.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-lightgrey.svg)

A powerful and professional tool for checking Telegram username availability with multi-account support

</div>

## ✨ Features

- 🚀 **High Performance**: Optimized for speed with concurrent processing
- 👥 **Multi-Account Support**: Use multiple Telegram accounts simultaneously
- 🔄 **Parallel Processing**: Multiple simultaneous checks for faster results
- 🛡️ **Smart FloodWait Management**: Intelligent handling of rate limits across accounts
- 📊 **Comprehensive Logging**: Detailed logs with rotation for monitoring
- 🎨 **Beautiful Menu Interface**: Interactive menu system with emojis
- ⚙️ **Easy Configuration**: Simple config file setup for multiple accounts
- 🌐 **Proxy Support**: SOCKS5/SOCKS4/HTTP proxy compatibility
- 📈 **Real-time Status**: Live account status and flood wait monitoring
- 📦 **EXE Conversion**: Can be compiled to standalone executable

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