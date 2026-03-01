import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
import git
import time

class UpdateManager:
    def __init__(self, repo_path=None):
        self.repo_path = repo_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config_file = os.path.join(self.repo_path, 'git_config.json')
        self.config = self.load_config()
        self.repo = git.Repo(self.repo_path)
    
    def load_config(self):
        """Load git config from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            'repo_url': None,
            'branch': 'main',
            'last_update': None,
            'current_version': '1.0.0',
            'check_interval_hours': 1
        }
    
    def save_config(self):
        """Save git config to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def check_for_updates(self):
        """Check if remote has newer commits than local"""
        try:
            # Fetch latest from remote
            self.repo.remotes.origin.fetch()
            
            # Get local and remote commit hashes
            local_commit = self.repo.head.commit.hexsha
            remote_commit = self.repo.remotes.origin.refs[self.config['branch']].commit.hexsha
            
            if local_commit != remote_commit:
                print(f"[UPDATE] New version available!")
                print(f"[UPDATE] Local:  {local_commit[:8]}")
                print(f"[UPDATE] Remote: {remote_commit[:8]}")
                return True
            else:
                print(f"[UPDATE] Already up to date ({local_commit[:8]})")
                return False
                
        except Exception as e:
            print(f"[UPDATE ERROR] Failed to check for updates: {e}")
            return False
    
    def pull_updates(self):
        """Pull latest code from remote"""
        try:
            print(f"[UPDATE] Pulling updates from {self.config['branch']}...")
            self.repo.remotes.origin.pull(self.config['branch'])
            self.config['last_update'] = datetime.utcnow().isoformat()
            self.save_config()
            print("[UPDATE] ✅ Updates pulled successfully!")
            return True
        except Exception as e:
            print(f"[UPDATE ERROR] Failed to pull updates: {e}")
            return False
    
    def auto_update(self):
        """Check and auto-pull if updates available"""
        print("[UPDATE] Checking for updates...")
        
        if self.check_for_updates():
            if self.pull_updates():
                print("[UPDATE] ⚠️  Server restart recommended. Updates will take effect on next startup.")
                return True
        
        return False
    
    def get_current_commit(self):
        """Get current commit hash"""
        try:
            return self.repo.head.commit.hexsha[:8]
        except:
            return "unknown"
    
    def get_update_status(self):
        """Get update status info"""
        return {
            'current_version': self.config['current_version'],
            'current_commit': self.get_current_commit(),
            'last_update': self.config['last_update'],
            'branch': self.config['branch'],
            'check_interval_hours': self.config['check_interval_hours']
        }

def check_updates_on_startup():
    """Called on app startup to check and pull updates"""
    try:
        manager = UpdateManager()
        manager.auto_update()
    except Exception as e:
        print(f"[UPDATE] Startup update check failed: {e}")

if __name__ == '__main__':
    manager = UpdateManager()
    manager.auto_update()
