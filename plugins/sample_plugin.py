#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sample Plugin for Telegram Username Checker Plus v2.3

This is a sample plugin that demonstrates how to create plugins
for the Telegram Username Checker Plus application.

Plugin API Version: 2.3.0
Author: xPOURY4
Created: August 7, 2025
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Any

class SamplePlugin:
    """
    Sample plugin that demonstrates the plugin system capabilities.
    """
    
    def __init__(self):
        self.name = "Sample Plugin"
        self.version = "1.0.0"
        self.description = "A sample plugin demonstrating the plugin system"
        self.author = "xPOURY4"
        self.enabled = True
        self.hooks = {
            'on_startup': self.on_startup,
            'on_shutdown': self.on_shutdown,
            'before_check': self.before_check,
            'after_check': self.after_check,
            'on_flood_wait': self.on_flood_wait,
            'on_account_switch': self.on_account_switch
        }
        self.stats = {
            'checks_processed': 0,
            'flood_waits_detected': 0,
            'account_switches': 0,
            'startup_time': None
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Return plugin information."""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'enabled': self.enabled,
            'hooks': list(self.hooks.keys()),
            'stats': self.stats
        }
    
    def on_startup(self, *args, **kwargs):
        """Called when the application starts."""
        self.stats['startup_time'] = datetime.now()
        print(f"🔌 {self.name} v{self.version} loaded successfully!")
        print(f"   📝 {self.description}")
        print(f"   👤 Author: {self.author}")
    
    def on_shutdown(self, *args, **kwargs):
        """Called when the application shuts down."""
        print(f"🔌 {self.name} shutting down...")
        print(f"   📊 Processed {self.stats['checks_processed']} checks")
        print(f"   ⏰ FloodWaits detected: {self.stats['flood_waits_detected']}")
        print(f"   🔄 Account switches: {self.stats['account_switches']}")
        
        # Save plugin statistics
        try:
            stats_file = f"plugins/stats_{self.name.lower().replace(' ', '_')}.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, default=str)
            print(f"   💾 Statistics saved to {stats_file}")
        except Exception as e:
            print(f"   ❌ Failed to save statistics: {e}")
    
    def before_check(self, username: str, account_name: str, *args, **kwargs):
        """Called before checking a username."""
        print(f"🔍 [{self.name}] Preparing to check '{username}' with account '{account_name}'")
        return True  # Return False to skip this check
    
    def after_check(self, username: str, account_name: str, result: bool, response_time: float, *args, **kwargs):
        """Called after checking a username."""
        self.stats['checks_processed'] += 1
        status = "✅ Available" if result else "❌ Taken"
        print(f"📊 [{self.name}] '{username}' is {status} (checked in {response_time:.2f}s)")
    
    def on_flood_wait(self, account_name: str, wait_time: int, *args, **kwargs):
        """Called when a FloodWait occurs."""
        self.stats['flood_waits_detected'] += 1
        print(f"⏰ [{self.name}] FloodWait detected on '{account_name}' - waiting {wait_time} seconds")
    
    def on_account_switch(self, from_account: str, to_account: str, *args, **kwargs):
        """Called when switching between accounts."""
        self.stats['account_switches'] += 1
        print(f"🔄 [{self.name}] Switching from '{from_account}' to '{to_account}'")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Return plugin statistics."""
        runtime = None
        if self.stats['startup_time']:
            runtime = (datetime.now() - self.stats['startup_time']).total_seconds()
        
        return {
            **self.stats,
            'runtime_seconds': runtime,
            'checks_per_minute': (self.stats['checks_processed'] / max(1, runtime / 60)) if runtime else 0
        }
    
    def configure(self, config: Dict[str, Any]):
        """Configure the plugin with custom settings."""
        if 'enabled' in config:
            self.enabled = config['enabled']
        
        print(f"🔧 [{self.name}] Configuration updated")
    
    def reset_statistics(self):
        """Reset plugin statistics."""
        self.stats = {
            'checks_processed': 0,
            'flood_waits_detected': 0,
            'account_switches': 0,
            'startup_time': self.stats['startup_time']  # Keep startup time
        }
        print(f"🔄 [{self.name}] Statistics reset")

# Plugin entry point
def get_plugin():
    """Return the plugin instance."""
    return SamplePlugin()

# Plugin metadata
PLUGIN_INFO = {
    'name': 'Sample Plugin',
    'version': '1.0.0',
    'description': 'A sample plugin demonstrating the plugin system',
    'author': 'xPOURY4',
    'api_version': '2.3.0',
    'required_permissions': ['read_config', 'write_stats'],
    'dependencies': []
}

if __name__ == "__main__":
    # Test the plugin
    plugin = get_plugin()
    print("Testing Sample Plugin...")
    
    # Simulate plugin lifecycle
    plugin.on_startup()
    plugin.before_check("testuser", "account1")
    plugin.after_check("testuser", "account1", True, 1.5)
    plugin.on_flood_wait("account1", 30)
    plugin.on_account_switch("account1", "account2")
    
    # Show statistics
    stats = plugin.get_statistics()
    print("\nPlugin Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    plugin.on_shutdown()
