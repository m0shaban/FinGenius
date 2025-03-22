#!/bin/bash

# إظهار البيئة الحالية
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# تثبيت الحزم بشكل صريح وباستخدام خيارات إضافية
pip install --no-cache-dir -r requirements.txt

# تثبيت مكتبات محددة بشكل منفصل لضمان تثبيتها
pip install --no-cache-dir Flask-WTF==1.2.1 WTForms==3.1.0
pip install --no-cache-dir matplotlib==3.8.0
pip install --no-cache-dir openai==1.3.3

# التحقق من تثبيت الحزم
pip list | grep -E 'Flask|WTF|matplotlib|openai'

# إنشاء مجلد التحميلات إذا لم يكن موجودًا
mkdir -p uploads

# إعداد قاعدة البيانات - تعليق هذا الأمر لمنع المشاكل في الإنتاج
# python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

echo "Build completed successfully"
