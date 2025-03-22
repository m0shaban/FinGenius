#!/usr/bin/env python
"""
ملف بسيط للتحقق من صحة التطبيق
"""
import sys
import importlib.util

# الحزم المطلوبة للتطبيق
required_packages = [
    'flask',
    'flask_sqlalchemy',
    'flask_login',
    'flask_migrate',
    'flask_wtf',
    'wtforms',
    'sqlalchemy',
    'pandas',
    'numpy',
    'gunicorn',
    'python-dotenv'
]

print("Checking required packages...")
missing_packages = []

for package in required_packages:
    spec = importlib.util.find_spec(package)
    if spec is None:
        missing_packages.append(package)
        print(f"❌ {package}: Missing")
    else:
        print(f"✅ {package}: Found")

if missing_packages:
    print("\n⚠️ Missing packages:")
    for package in missing_packages:
        print(f"  - {package}")
    sys.exit(1)
else:
    print("\n✅ All required packages are installed!")
    sys.exit(0)
