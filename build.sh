#!/bin/bash

# إظهار البيئة الحالية
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"

# تثبيت الحزم بشكل صريح وباستخدام خيارات إضافية
pip install --no-cache-dir -r requirements.txt

# تثبيت Flask-WTF بشكل منفصل لضمان تثبيته
pip install --no-cache-dir Flask-WTF==1.2.1 WTForms==3.1.0

# التحقق من تثبيت الحزم
pip list | grep -E 'Flask|WTF'

# إنشاء مجلد التحميلات إذا لم يكن موجودًا
mkdir -p uploads

# إعداد قاعدة البيانات
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

echo "Build completed successfully"
