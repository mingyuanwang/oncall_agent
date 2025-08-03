# Flask应用入口
import sys
from pathlib import Path
# 添加app目录到Python路径
sys.path.append(str(Path(__file__).resolve().parent.parent))
from flask import Flask, send_from_directory
from flask_cors import CORS
from app.routes.query import bp as query_bp
from app.routes.train import bp as train_bp

app = Flask(__name__, static_folder='static')

CORS(app)

# 提供聊天界面
@app.route('/')
def serve_chat():
    return send_from_directory('static', 'index.html')

# 注册API路由
app.register_blueprint(query_bp, url_prefix='/api/v1')
app.register_blueprint(train_bp, url_prefix='/api/v1')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)