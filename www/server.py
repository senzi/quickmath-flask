import http.server
import socketserver

PORT = 5233
Handler = http.server.SimpleHTTPRequestHandler

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(__file__))
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Serving at http://0.0.0.0:{PORT}")
        httpd.serve_forever()
