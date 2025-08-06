# Flask应用入口
import sys
from pathlib import Path
# 添加app目录到Python路径
sys.path.append(str(Path(__file__).resolve().parent.parent))

# 设置日志配置
from utils.logging_config import setup_logging
setup_logging()

from flask import Flask, send_from_directory
from flask_cors import CORS
from app.routes.query import bp as query_bp
from app.routes.train import bp as train_bp

# 启用流式响应支持
from flask import stream_with_context, Response

app = Flask(__name__, static_folder='static')

CORS(app)

# 提供聊天界面
@app.route('/')
def serve_chat():
    return send_from_directory('static', 'index.html')

# 注册API路由
app.register_blueprint(query_bp)
app.register_blueprint(train_bp, url_prefix='/api/v1')

if __name__ == '__main__':
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Memory Agent Project')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    # 打印所有注册的路由
    print('Registered routes:')
    for rule in app.url_map.iter_rules():
        print(f'  {rule.endpoint}: {rule.rule}')
    
    # 根据参数决定是否启用debug模式
    app.run(host='0.0.0.0', port=8000, debug=args.debug)