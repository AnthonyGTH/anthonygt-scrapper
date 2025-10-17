#!/usr/bin/env python3
"""
Script to check FTP structure and see where files are actually located
"""

import ftplib
import os

def check_ftp_structure():
    # FTP connection details
    host = '82.197.83.99'
    user = 'u267443062.anthonygt-scrappers.com.mx'
    password = 'A1g3T2h4||'
    port = 21

    try:
        # Connect to FTP
        print("🔌 Connecting to FTP...")
        ftp = ftplib.FTP()
        ftp.connect(host, port)
        ftp.login(user, password)
        
        print('✅ Connected to FTP successfully')
        print(f'📍 Current directory: {ftp.pwd()}')
        
        # List current directory
        print('\n📁 Current directory contents:')
        ftp.retrlines('LIST')
        
        # Try to navigate to domains
        print('\n🔍 Checking domains directory...')
        try:
            ftp.cwd('domains')
            print(f'📁 In domains directory: {ftp.pwd()}')
            ftp.retrlines('LIST')
            
            # Check if anthonygt-scrappers.com.mx exists
            print('\n🔍 Checking anthonygt-scrappers.com.mx...')
            try:
                ftp.cwd('anthonygt-scrappers.com.mx')
                print(f'📁 In anthonygt-scrappers.com.mx: {ftp.pwd()}')
                ftp.retrlines('LIST')
                
                # Check public_html
                print('\n🔍 Checking public_html...')
                try:
                    ftp.cwd('public_html')
                    print(f'📁 In public_html: {ftp.pwd()}')
                    ftp.retrlines('LIST')
                except Exception as e:
                    print(f'❌ Cannot access public_html: {e}')
            except Exception as e:
                print(f'❌ Cannot access anthonygt-scrappers.com.mx: {e}')
        except Exception as e:
            print(f'❌ Cannot access domains: {e}')
        
        # Check if there's a different structure
        print('\n🔍 Checking for alternative structure...')
        ftp.cwd('/')  # Go back to root
        print(f'📍 Back to root: {ftp.pwd()}')
        
        # List all directories in root
        print('\n📁 Root directory contents:')
        ftp.retrlines('LIST')
        
        ftp.quit()
        print('\n✅ FTP connection closed')
        
    except Exception as e:
        print(f'❌ FTP connection failed: {e}')

if __name__ == "__main__":
    check_ftp_structure()
