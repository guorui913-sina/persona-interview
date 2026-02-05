#!/usr/bin/env python3
"""
决策追踪Web服务器
提供HTTP API用于决策的CRUD操作，同时服务静态网页

使用方法：
    python decision_server.py

服务器启动后：
    - 访问 http://localhost:8000 查看网页
    - API会自动处理 /api/* 的请求
    - 数据存储在 data/decisions/ 目录
"""

import http.server
import socketserver
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import mimetypes

# 添加路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# 导入决策追踪模块
from decision_tracker import (
    record_decision,
    load_decision,
    load_all_decisions,
    get_decision_dir,
    DECISION_TYPES
)


class DecisionAPIHandler(http.server.SimpleHTTPRequestHandler):
    """处理决策API请求的HTTP处理器"""

    def __init__(self, *args, **kwargs):
        self.json_content_type = 'application/json;charset=utf-8'
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """处理GET请求"""
        parsed = urlparse(self.path)

        # API请求
        if parsed.path.startswith('/api/'):
            self.handle_api_get(parsed)
        else:
            # 静态文件
            super().do_GET()

    def do_POST(self):
        """处理POST请求"""
        parsed = urlparse(self.path)

        if parsed.path.startswith('/api/'):
            self.handle_api_post(parsed)
        else:
            self.send_error(404, "Not Found")

    def handle_api_get(self, parsed):
        """处理API GET请求"""
        path = parsed.path

        try:
            if path == '/api/decisions':
                # 获取所有决策
                decisions = load_all_decisions()
                self.send_json_response({
                    'success': True,
                    'data': decisions
                })

            elif path.startswith('/api/decisions/'):
                # 获取单个决策
                decision_id = path.split('/')[-1]
                decision = load_decision(decision_id)

                if decision:
                    self.send_json_response({
                        'success': True,
                        'data': decision
                    })
                else:
                    self.send_json_response({
                        'success': False,
                        'error': 'Decision not found'
                    }, status=404)

            elif path == '/api/stats':
                # 获取统计信息
                decisions = load_all_decisions()
                stats = self.calculate_stats(decisions)
                self.send_json_response({
                    'success': True,
                    'data': stats
                })

            else:
                self.send_json_response({
                    'success': False,
                    'error': 'Invalid API endpoint'
                }, status=404)

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    def handle_api_post(self, parsed):
        """处理API POST请求"""
        path = parsed.path

        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            if path == '/api/decisions':
                # 创建新决策
                decision = record_decision(
                    description=data.get('description', ''),
                    decision_type=data.get('type', 'important'),
                    rational_analysis=data.get('rational_analysis', ''),
                    emotional_factors=data.get('emotional_factors', []),
                    ai_warning=data.get('ai_warning', '')
                )
                self.send_json_response({
                    'success': True,
                    'data': decision
                })

            elif path.startswith('/api/decisions/') and path.endswith('/status'):
                # 更新决策状态
                decision_id = path.split('/')[-2]
                new_status = data.get('status')
                note = data.get('note', '')

                from decision_tracker import update_decision_status

                updated_decision = update_decision_status(decision_id, new_status, note)
                self.send_json_response({
                    'success': True,
                    'data': updated_decision
                })

            elif path.startswith('/api/decisions/') and path.endswith('/complete'):
                # 完成决策
                decision_id = path.split('/')[-2]
                result = data.get('result')
                outcome = data.get('outcome', '')
                lessons = data.get('lessons', '')

                from decision_tracker import complete_decision

                completed_decision = complete_decision(decision_id, result, outcome, lessons)
                self.send_json_response({
                    'success': True,
                    'data': completed_decision
                })

            else:
                self.send_json_response({
                    'success': False,
                    'error': 'Invalid API endpoint'
                }, status=404)

        except Exception as e:
            self.send_json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    def calculate_stats(self, decisions):
        """计算统计信息"""
        stats = {
            'total': len(decisions),
            'by_type': {},
            'by_status': {},
            'by_risk': {}
        }

        for d in decisions:
            dtype = d.get('type', 'unknown')
            status = d.get('outcome', 'pending')
            risk = d.get('risk_level', 'unknown')

            stats['by_type'][dtype] = stats['by_type'].get(dtype, 0) + 1
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            stats['by_risk'][risk] = stats['by_risk'].get(risk, 0) + 1

        return stats

    def send_json_response(self, data, status=200):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header('Content-Type', self.json_content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))


def run_server(port=8000):
    """启动Web服务器"""
    # 确保数据目录存在
    decision_dir = get_decision_dir()
    decision_dir.mkdir(parents=True, exist_ok=True)

    # 设置MIME类型
    mimetypes.init()

    print(f"""
╔════════════════════════════════════════════════════════════╗
║           📊 决策追踪Web服务器                          ║
╚════════════════════════════════════════════════════════════╝
🌐 服务器地址：http://localhost:{port}
📂 数据目录：{decision_dir}
📄 API文档：http://localhost:{port}/api/
🔄 状态检查：http://localhost:{port}/api/stats

按 Ctrl+C 停止服务器
    """)

    # 切换到包含HTML文件的目录
    os.chdir(script_dir.parent)

    Handler = DecisionAPIHandler

    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="决策追踪Web服务器")
    parser.add_argument("--port", type=int, default=8000, help="端口号（默认8000）")

    args = parser.parse_args()

    try:
        run_server(port=args.port)
    except KeyboardInterrupt:
        print("\n\n✅ 服务器已停止")
