"""
نسخة مبسطة من التطبيق تتجاهل وحدة التحليل التي تعتمد على matplotlib
يمكن استخدامها في بيئات الإنتاج حيث لا تتوفر مكتبة matplotlib
"""
import os
import sys
import logging
from importlib.util import find_spec

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# استثناء وحدات التحليل المعتمدة على matplotlib
sys.modules['matplotlib'] = object()
sys.modules['matplotlib.pyplot'] = object()

try:
    from app import create_app, db
    
    # تعريف الطرق الوهمية للتوافق
    class DummyPlotter:
        def figure(*args, **kwargs): return None
        def savefig(*args, **kwargs): return None
        def close(*args, **kwargs): return None
        def plot(*args, **kwargs): return None
        def title(*args, **kwargs): return None
        def xlabel(*args, **kwargs): return None
        def ylabel(*args, **kwargs): return None
        def legend(*args, **kwargs): return None
        def grid(*args, **kwargs): return None
        def subplots(*args, **kwargs): return (None, None)
    
    # تعريف matplotlib.pyplot الوهمي
    sys.modules['matplotlib.pyplot'] = DummyPlotter()
    
    # إنشاء تطبيق Flask
    app = create_app()

    # تشغيل التطبيق
    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
except Exception as e:
    logger.error(f"Application startup error: {e}", exc_info=True)
    raise
