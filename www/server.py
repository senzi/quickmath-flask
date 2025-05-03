import http.server
import socket
import threading
import os
import sys

PORT = 5233

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 可选：屏蔽访问日志输出

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    server = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), QuietHandler)

    def run_server():
        try:
            server.serve_forever()
        except Exception:
            pass

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

    ip = get_local_ip()
    print("🚀 Serving at:")
    print(f"  👉 http://127.0.0.1:{PORT}")
    print(f"  👉 http://{ip}:{PORT}")
    print("💡 输入 `q` 或 `exit` 然后回车以退出服务器")

    try:
        while True:
            cmd = input("> ").strip().lower()
            if cmd in ('q', 'exit', 'quit'):
                print("🛑 正在关闭服务器...")
                server.shutdown()
                print("✅ 服务器已关闭。")
                break
    except KeyboardInterrupt:
        print("\n🛑 捕获 Ctrl+C，正在关闭服务器...")
        server.shutdown()
        print("✅ 服务器已关闭。")
        sys.exit(0)
