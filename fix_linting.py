#!/usr/bin/env python3
import os
import re

def fix_all_linting():
    """Fix all common linting issues across all Python files"""
    
    # Files to fix
    files_to_fix = [
        'src/api.py',
        'src/bot.py', 
        'src/main.py',
        'src/lambda_function.py',
        'src/config/settings.py',
        'src/database/db.py',
        'src/models/models.py',
        'src/services/alerting.py',
        'src/services/auto_sell.py',
        'src/services/indicators.py',
        'src/services/market_data.py',
        'src/services/plotting.py',
        'src/services/portfolio.py',
        'src/services/scoring.py'
    ]
    
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove trailing whitespace and fix newlines
            lines = content.split('\n')
            fixed_lines = [line.rstrip() for line in lines]
            fixed_content = '\n'.join(fixed_lines)
            
            # Add newline at end if missing
            if fixed_content and not fixed_content.endswith('\n'):
                fixed_content += '\n'
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print(f"Fixed {filepath}")

if __name__ == "__main__":
    fix_all_linting()
    print("All whitespace issues fixed!")