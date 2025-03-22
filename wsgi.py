import os
import sys
import logging

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # تصحيح levellevelname إلى levelname
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

try:
    from app import create_app, db
    
    # إنشاء تطبيق Flask
    app = create_app()
    
    # التأكد من وجود مجلد التحميلات
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # إعداد قاعدة البيانات
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
    
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
except Exception as e:
    logger.error(f"Application startup error: {e}", exc_info=True)
    raise
