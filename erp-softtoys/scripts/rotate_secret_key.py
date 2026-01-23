"""SECRET_KEY Rotation System
===========================
Automated JWT secret key rotation with grace period

Author: Daniel (IT Senior Developer)
Date: January 21, 2026
Version: 1.0

Features:
- Generates new 256-bit SECRET_KEY
- Maintains history of last 3 keys (270-day grace period)
- Updates .env file automatically
- Supports gradual token invalidation
- Logs rotation events

Usage:
    python scripts/rotate_secret_key.py

Cron job (rotate every 90 days at 2 AM):
    0 2 */90 * * cd /path/to/erp && python scripts/rotate_secret_key.py && docker-compose restart backend
"""

import re
import secrets
from datetime import datetime
from pathlib import Path
from typing import list, tuple


class SecretKeyRotation:
    """Handles SECRET_KEY rotation with history management"""

    def __init__(self, env_file: str = ".env"):
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / env_file
        self.backup_dir = self.project_root / "backups" / "secret_keys"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """Log rotation events"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = "✅" if level == "SUCCESS" else "📊" if level == "INFO" else "⚠️ "
        print(f"[{timestamp}] {prefix} {message}")

        # Also log to file
        log_file = self.project_root / "logs" / "secret_key_rotation.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")

    def generate_new_key(self) -> str:
        """Generate a new 256-bit secret key"""
        # 256 bits = 32 bytes, urlsafe_b64 produces 43 chars
        new_key = secrets.token_urlsafe(32)
        self.log(f"Generated new SECRET_KEY: {new_key[:10]}... (truncated)", "INFO")
        return new_key

    def read_env_file(self) -> str:
        """Read current .env file content"""
        if not self.env_file.exists():
            raise FileNotFoundError(f".env file not found at {self.env_file}")

        with open(self.env_file) as f:
            content = f.read()

        return content

    def extract_current_key(self, env_content: str) -> str:
        """Extract current SECRET_KEY from .env"""
        pattern = r'^SECRET_KEY=(.+)$'
        match = re.search(pattern, env_content, re.MULTILINE)

        if not match:
            raise ValueError("SECRET_KEY not found in .env file")

        current_key = match.group(1).strip()
        self.log(f"Current SECRET_KEY: {current_key[:10]}... (truncated)", "INFO")
        return current_key

    def extract_key_history(self, env_content: str) -> list[str]:
        """Extract SECRET_KEYS_HISTORY from .env"""
        pattern = r'^SECRET_KEYS_HISTORY=(.*)$'
        match = re.search(pattern, env_content, re.MULTILINE)

        if not match or not match.group(1).strip():
            return []

        history_str = match.group(1).strip()
        keys = [k.strip() for k in history_str.split(',') if k.strip()]

        self.log(f"Found {len(keys)} keys in history", "INFO")
        return keys

    def update_key_history(self, current_key: str, existing_history: list[str]) -> list[str]:
        """Update key history (keep last 3 keys)"""
        # Add current key to history
        new_history = [current_key] + existing_history

        # Keep only last 3 keys (270-day grace period: 90 days × 3)
        new_history = new_history[:3]

        self.log(f"Updated key history (keeping {len(new_history)} keys)", "INFO")
        return new_history

    def backup_env_file(self):
        """Create backup of .env before modification"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"env_backup_{timestamp}.txt"

        env_content = self.read_env_file()

        with open(backup_file, "w") as f:
            f.write(env_content)

        self.log(f"Created backup: {backup_file.name}", "SUCCESS")

    def update_env_file(self, new_key: str, new_history: list[str]):
        """Update .env file with new key and history"""
        env_content = self.read_env_file()

        # Replace SECRET_KEY
        env_content = re.sub(
            r'^SECRET_KEY=.+$',
            f'SECRET_KEY={new_key}',
            env_content,
            flags=re.MULTILINE
        )

        # Replace or add SECRET_KEYS_HISTORY
        history_str = ','.join(new_history)

        if re.search(r'^SECRET_KEYS_HISTORY=', env_content, re.MULTILINE):
            # Update existing line
            env_content = re.sub(
                r'^SECRET_KEYS_HISTORY=.*$',
                f'SECRET_KEYS_HISTORY={history_str}',
                env_content,
                flags=re.MULTILINE
            )
        else:
            # Add new line after SECRET_KEY
            env_content = re.sub(
                r'^(SECRET_KEY=.+)$',
                f'\\1\nSECRET_KEYS_HISTORY={history_str}',
                env_content,
                flags=re.MULTILINE
            )

        # Add or update KEY_LAST_ROTATED
        rotation_timestamp = datetime.now().isoformat()

        if re.search(r'^KEY_LAST_ROTATED=', env_content, re.MULTILINE):
            env_content = re.sub(
                r'^KEY_LAST_ROTATED=.*$',
                f'KEY_LAST_ROTATED={rotation_timestamp}',
                env_content,
                flags=re.MULTILINE
            )
        else:
            env_content = re.sub(
                r'^(SECRET_KEYS_HISTORY=.+)$',
                f'\\1\nKEY_LAST_ROTATED={rotation_timestamp}',
                env_content,
                flags=re.MULTILINE
            )

        # Write updated content
        with open(self.env_file, "w") as f:
            f.write(env_content)

        self.log("Updated .env file successfully", "SUCCESS")

    def create_rotation_report(self, old_key: str, new_key: str, history: list[str]):
        """Create rotation report for auditing"""
        report_file = self.backup_dir / f"rotation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        report = f"""
SECRET_KEY Rotation Report
==========================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Old SECRET_KEY: {old_key[:15]}... (truncated)
New SECRET_KEY: {new_key[:15]}... (truncated)

Key History ({len(history)} keys maintained):
"""
        for i, key in enumerate(history, 1):
            report += f"  {i}. {key[:15]}... (truncated)\n"

        report += f"""
Grace Period: {len(history) * 90} days
Next Rotation: {datetime.now().replace(day=datetime.now().day + 90).strftime('%Y-%m-%d')}

Actions Required:
1. Restart backend service: docker-compose restart backend
2. Monitor logs for JWT validation errors
3. Old tokens remain valid for grace period
4. New logins will use new SECRET_KEY

Security Notes:
- Old keys maintained for gradual token invalidation
- Users with old tokens can continue until expiry
- New logins immediately use new key
- After 270 days, oldest key dropped

Generated by: Secret Key Rotation System v1.0
"""

        with open(report_file, "w") as f:
            f.write(report)

        self.log(f"Created rotation report: {report_file.name}", "SUCCESS")

    def rotate(self) -> tuple[str, str, list[str]]:
        """Execute complete rotation process"""
        self.log("Starting SECRET_KEY rotation...", "INFO")

        # Step 1: Backup current .env
        self.backup_env_file()

        # Step 2: Read current state
        env_content = self.read_env_file()
        current_key = self.extract_current_key(env_content)
        existing_history = self.extract_key_history(env_content)

        # Step 3: Generate new key
        new_key = self.generate_new_key()

        # Step 4: Update history
        new_history = self.update_key_history(current_key, existing_history)

        # Step 5: Update .env file
        self.update_env_file(new_key, new_history)

        # Step 6: Create audit report
        self.create_rotation_report(current_key, new_key, new_history)

        return current_key, new_key, new_history


def main():
    """Execute rotation"""
    print("="*70)
    print("SECRET_KEY ROTATION SYSTEM")
    print("="*70)
    print()

    rotator = SecretKeyRotation()

    try:
        old_key, new_key, history = rotator.rotate()

        print()
        print("="*70)
        print("✅ SECRET_KEY ROTATION COMPLETE")
        print("="*70)
        print()
        print("Summary:")
        print(f"  - Old key: {old_key[:15]}... (truncated)")
        print(f"  - New key: {new_key[:15]}... (truncated)")
        print(f"  - Keys in history: {len(history)}")
        print(f"  - Grace period: {len(history) * 90} days")
        print()
        print("⚠️  NEXT STEPS:")
        print("1. Restart backend service:")
        print("   docker-compose restart backend")
        print()
        print("2. Monitor application logs:")
        print("   docker-compose logs -f backend | grep JWT")
        print()
        print("3. Verify JWT validation:")
        print("   - Old tokens still work (grace period)")
        print("   - New logins use new key")
        print()
        print("4. Schedule next rotation:")
        print("   - 90 days from now")
        print(f"   - Recommended date: {datetime.now().replace(day=datetime.now().day + 90).strftime('%Y-%m-%d')}")
        print()

    except Exception as e:
        print()
        print(f"❌ ROTATION FAILED: {str(e)}")
        print()
        print("Error recovery:")
        print("1. Check .env file integrity")
        print("2. Restore from backup if needed:")
        print("   cp backups/secret_keys/env_backup_*.txt .env")
        print("3. Contact security team for assistance")
        print()
        sys.exit(1)


if __name__ == "__main__":
    import sys
    main()
