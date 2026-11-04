#!/usr/bin/env python3
"""
LEAF_AI All-in-One Launcher (connect.py)
----------------------------------------
Tự động:
1. Kiểm tra cấu hình và file môi trường (.env)
2. Tự động khởi tạo .venv trong backend/.venv nếu chưa có
3. Quét toàn bộ package cần thiết của Backend:
   - Đã có trong .venv -> Bỏ qua
   - Chưa có -> Tải về và cài đặt đầy đủ vào backend/.venv
4. Quét dependencies của Frontend (package.json / node_modules):
   - Đã có -> Bỏ qua
   - Chưa có -> Tự động chạy npm install
5. Giải phóng cổng 8000 và 5173 nếu đang bị kẹt
6. Khởi chạy song song Backend (FastAPI) & Frontend (Vite)
7. Xuất trực tiếp đường link truy cập ra Terminal và tự động mở trình duyệt!
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
import threading

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"

BACKEND_HOST = os.environ.get("LEAF_AI_BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.environ.get("LEAF_AI_BACKEND_PORT", "8000"))
FRONTEND_HOST = os.environ.get("LEAF_AI_FRONTEND_HOST", "127.0.0.1")
FRONTEND_PORT = int(os.environ.get("LEAF_AI_FRONTEND_PORT", "5173"))

PROCESSES: list[subprocess.Popen] = []
STOPPING = False


def print_banner() -> None:
    print("\n" + "=" * 68)
    print("      🌱 LEAF_AI AUTO CONNECT & LAUNCHER (Python Only) 🌱")
    print("=" * 68)
    print(f" ▸ Project Path : {ROOT}")
    print(f" ▸ Hệ điều hành : {platform.system()} ({platform.release()})")
    print(f" ▸ Python Host  : {sys.version.split()[0]}")
    print("=" * 68 + "\n", flush=True)


def get_venv_python() -> Path:
    if os.name == "nt":
        return BACKEND / ".venv" / "Scripts" / "python.exe"
    return BACKEND / ".venv" / "bin" / "python"


def find_executable(*names: str) -> str | None:
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def ensure_env_files() -> None:
    """Sao chép file .env từ .env.example nếu chưa có."""
    pairs = [
        (BACKEND / ".env.example", BACKEND / ".env"),
        (FRONTEND / ".env.example", FRONTEND / ".env"),
    ]
    for example, target in pairs:
        if example.is_file() and not target.is_file():
            try:
                shutil.copy(example, target)
                print(f" [i] Đã tự động tạo {target.name} từ {example.name}")
            except Exception as e:
                print(f" [!] Không thể copy {example.name} -> {target.name}: {e}")


def ensure_backend_venv() -> Path:
    """Đảm bảo thư mục .venv trong backend sẵn sàng."""
    venv_dir = BACKEND / ".venv"
    venv_python = get_venv_python()

    if not venv_python.is_file():
        print(f"[*] Chưa tìm thấy .venv trong backend. Đang tự động tạo môi trường ảo tại {venv_dir}...")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True, cwd=str(BACKEND))
            print(" [✓] Khởi tạo .venv thành công!")
        except Exception as exc:
            raise RuntimeError(f"Tạo .venv thất bại: {exc}") from exc

    # Kiểm tra tính hợp lệ của Python trong .venv
    try:
        res = subprocess.run(
            [str(venv_python), "-c", "import sys; print(sys.executable)"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if res.returncode != 0:
            raise RuntimeError("Python trong .venv không thể thực thi.")
    except Exception as exc:
        raise RuntimeError(f"Lỗi kiểm tra môi trường .venv ({venv_python}): {exc}") from exc

    return venv_python


def scan_and_install_backend_packages(venv_python: Path) -> None:
    """
    Quét toàn bộ package cần thiết trong backend/requirements.txt.
    Kiểm tra từng package xem đã có trong .venv chưa.
    - Đã có -> Bỏ qua.
    - Chưa có -> Tải về và cài đặt bổ sung.
    """
    print("\n🔍 ĐANG KIỂM TRA CÁC GÓI THƯ VIỆN BACKEND (.venv)...")
    req_file = BACKEND / "requirements.txt"
    if not req_file.is_file():
        print(" [!] Không tìm thấy backend/requirements.txt. Sẽ kiểm tra tối thiểu fastapi và uvicorn...")
        req_lines = ["fastapi", "uvicorn[standard]"]
    else:
        req_lines = [
            line.strip()
            for line in req_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]

    # Kiểm tra danh sách package đã cài đặt trong .venv
    check_script = """
import importlib.metadata, json
installed = {}
for dist in importlib.metadata.distributions():
    try:
        name = dist.metadata['Name']
        if name:
            installed[name.lower().replace('_', '-')] = dist.version
    except Exception:
        pass
print(json.dumps(installed))
"""
    try:
        proc = subprocess.run(
            [str(venv_python), "-c", check_script],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(BACKEND),
        )
        installed_dists = json.loads(proc.stdout)
    except Exception as exc:
        print(f" [!] Không thể lấy danh sách gói đã cài: {exc}. Sẽ chạy pip install dự phòng.")
        installed_dists = {}

    missing_reqs: list[str] = []

    for req in req_lines:
        # Lấy tên package gốc, loại bỏ [extra] và version specifier
        raw_name = re.split(r"[<>=!~;]", req)[0].strip()
        pkg_name = re.sub(r"\[.*?\]", "", raw_name).strip().lower().replace("_", "-")

        if pkg_name in installed_dists:
            version = installed_dists[pkg_name]
            print(f"   [✓] {req:<32} (đã cài: v{version}) -> BỎ QUA")
        else:
            print(f"   [+] {req:<32} -> CHƯA CÓ (sẽ tải về)")
            missing_reqs.append(req)

    if not missing_reqs:
        print(" ✨ Tất cả thư viện Python cần thiết đã được cài đầy đủ trong .venv!")
    else:
        print(f"\n📦 Đang tải và cài đặt {len(missing_reqs)} gói còn thiếu vào .venv...")
        install_cmd = [str(venv_python), "-m", "pip", "install", *missing_reqs]
        try:
            subprocess.run(install_cmd, check=True, cwd=str(BACKEND))
            print(" [✓] Cài đặt các gói thiếu vào .venv hoàn tất thành công!")
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"Cài đặt gói backend thất bại: {exc}") from exc


def scan_and_install_frontend_packages() -> str | None:
    """
    Quét package.json của Frontend.
    - Nếu máy có Node.js: kiểm tra node_modules, thiếu thì npm install, đủ thì bỏ qua.
    - Nếu máy KHÔNG có Node.js: tự động chuyển sang chế độ Python Static Server từ frontend/dist.
    """
    print("\n🔍 ĐANG KIỂM TRA DEPENDENCIES FRONTEND...")
    npm = find_executable("npm.cmd", "npm")
    node = find_executable("node.exe", "node")

    dist_dir = FRONTEND / "dist"

    if not node or not npm:
        print(" [i] Hệ thống KHÔNG CÓ Node.js/npm.")
        if dist_dir.is_dir() and (dist_dir / "index.html").is_file():
            print(" [✓] Đã phát hiện bản build frontend/dist!")
            print(" 🚀 Tự động kích hoạt Web Server bằng PYTHON THUẦN (Không cần cài Node.js)!")
        else:
            print(" [!] Cảnh báo: Chưa có frontend/dist và không có Node.js.")
            print("     Để có trải nghiệm tốt nhất, bạn có thể cài Node.js từ https://nodejs.org")
        return None

    pkg_json = FRONTEND / "package.json"
    if not pkg_json.is_file():
        print(" [!] Không tìm thấy frontend/package.json.")
        return npm

    try:
        data = json.loads(pkg_json.read_text(encoding="utf-8"))
        deps = {}
        deps.update(data.get("dependencies", {}))
        deps.update(data.get("devDependencies", {}))
    except Exception as exc:
        print(f" [!] Không thể đọc package.json: {exc}")
        deps = {}

    node_modules = FRONTEND / "node_modules"
    missing = []
    for dep in deps:
        if (node_modules / dep).exists():
            print(f"   [✓] {dep:<32} -> Đã có (BỎ QUA)")
        else:
            print(f"   [+] {dep:<32} -> CHƯA CÓ")
            missing.append(dep)

    if not node_modules.is_dir() or len(missing) > 0:
        print(f"\n📦 Đang cài đặt node modules cho Frontend...")
        lockfile = FRONTEND / "package-lock.json"
        cmd = [npm, "ci"] if lockfile.is_file() and not node_modules.is_dir() else [npm, "install"]
        try:
            subprocess.run(cmd, check=True, cwd=str(FRONTEND))
            print(" [✓] Cài đặt dependencies Frontend hoàn tất!")
        except subprocess.CalledProcessError as exc:
            print(f" [!] npm install gặp lỗi: {exc}")
    else:
        print(" ✨ Tất cả frontend packages đã có đầy đủ trong node_modules! Bỏ qua tải lại.")

    return npm


def free_port_if_busy(host: str, port: int) -> None:
    """Kiểm tra và giải phóng cổng nếu đang bị kẹt bởi tiến trình trước."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        is_busy = sock.connect_ex((host, port)) == 0

    if not is_busy:
        return

    print(f" [i] Cổng {port} đang bận, đang kiểm tra và giải phóng...")
    try:
        if os.name == "nt":
            # Windows: tìm PID và taskkill
            out = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True, text=True)
            for line in out.strip().splitlines():
                parts = line.split()
                if len(parts) >= 5 and "LISTENING" in line.upper():
                    pid = parts[-1]
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
        else:
            # Linux / macOS: fuser
            subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True)
        time.sleep(1)
    except Exception:
        pass


def is_service_ready(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def wait_for_service(host: str, port: int, process: subprocess.Popen, name: str, timeout: int = 45) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False
        if is_service_ready(host, port):
            return True
        time.sleep(0.5)
    return False


def stream_logs(pipe, prefix: str) -> None:
    """In log của subprocess ra terminal có kèm nhãn."""
    try:
        for line in iter(pipe.readline, ""):
            if STOPPING:
                break
            line_str = line.strip()
            if line_str:
                print(f"[{prefix}] {line_str}", flush=True)
    except Exception:
        pass


def stop_all_processes() -> None:
    global STOPPING
    if STOPPING:
        return
    STOPPING = True

    print("\n\n🛑 Đang dừng tất cả các dịch vụ LEAF_AI...")
    for proc in reversed(PROCESSES):
        if proc.poll() is not None:
            continue
        try:
            if os.name == "nt":
                subprocess.run(f"taskkill /F /T /PID {proc.pid}", shell=True, capture_output=True)
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            try:
                proc.terminate()
            except Exception:
                pass

    for proc in reversed(PROCESSES):
        if proc.poll() is None:
            try:
                proc.wait(timeout=2)
            except Exception:
                proc.kill()
    print("👋 Đã tắt hoàn tất! Hẹn gặp lại.\n")


def main() -> int:
    print_banner()

    if not BACKEND.is_dir() or not FRONTEND.is_dir():
        print("❌ Lỗi: Thư mục backend hoặc frontend không tồn tại!")
        print(f"   Vui lòng đặt file connect.py tại thư mục gốc: {ROOT}")
        return 1

    # 1. Đảm bảo file .env
    ensure_env_files()

    # 2. Tạo hoặc kiểm tra .venv
    venv_python = ensure_backend_venv()

    # 3. Quét & cài đặt package backend (chỉ cài những gì thiếu)
    scan_and_install_backend_packages(venv_python)

    # 4. Quét & cài đặt package frontend
    npm = scan_and_install_frontend_packages()

    # 5. Giải phóng cổng nếu cần
    free_port_if_busy(BACKEND_HOST, BACKEND_PORT)
    free_port_if_busy(FRONTEND_HOST, FRONTEND_PORT)

    # 6. Khởi chạy Backend & Frontend
    print("\n🚀 ĐANG KHỞI CHẠY BACKEND & FRONTEND...")

    backend_cmd = [
        str(venv_python), "-m", "uvicorn", "app.main:app",
        "--host", BACKEND_HOST, "--port", str(BACKEND_PORT),
        "--reload"
    ]

    kwargs_be: dict = {
        "cwd": str(BACKEND),
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
        "bufsize": 1,
    }
    kwargs_fe: dict = {
        "cwd": str(FRONTEND),
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
        "bufsize": 1,
    }

    if os.name == "nt":
        kwargs_be["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        kwargs_fe["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        kwargs_be["start_new_session"] = True
        kwargs_fe["start_new_session"] = True

    backend_proc = subprocess.Popen(backend_cmd, **kwargs_be)
    PROCESSES.append(backend_proc)

    frontend_proc = None
    dist_dir = FRONTEND / "dist"
    if npm:
        frontend_cmd = [
            npm, "run", "dev", "--",
            "--host", FRONTEND_HOST,
            "--port", str(FRONTEND_PORT)
        ]
        frontend_proc = subprocess.Popen(frontend_cmd, **kwargs_fe)
        PROCESSES.append(frontend_proc)
    elif dist_dir.is_dir() and (dist_dir / "index.html").is_file():
        # Chạy máy chủ SPA thuần Python cho frontend nếu máy không có Node.js
        spa_server_code = f"""
import os, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class SPAHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=r'{dist_dir}', **kwargs)

    def do_GET(self):
        req_path = self.path.split('?')[0]
        local_path = os.path.join(r'{dist_dir}', req_path.lstrip('/'))
        if not os.path.exists(local_path):
            self.path = '/index.html'
        return super().do_GET()

server = ThreadingHTTPServer(('{FRONTEND_HOST}', {FRONTEND_PORT}), SPAHandler)
server.serve_forever()
"""
        frontend_cmd = [str(venv_python), "-c", spa_server_code]
        frontend_proc = subprocess.Popen(frontend_cmd, **kwargs_fe)
        PROCESSES.append(frontend_proc)

    # Đợi dịch vụ sẵn sàng
    be_ok = wait_for_service(BACKEND_HOST, BACKEND_PORT, backend_proc, "Backend", timeout=30)
    fe_ok = False
    if frontend_proc:
        fe_ok = wait_for_service(FRONTEND_HOST, FRONTEND_PORT, frontend_proc, "Frontend", timeout=30)

    website_url = f"http://{FRONTEND_HOST}:{FRONTEND_PORT}"
    api_url = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
    docs_url = f"http://{BACKEND_HOST}:{BACKEND_PORT}/docs"

    # Xuất ra banner link to rõ trên terminal
    print("\n" + "=" * 68)
    print("   🎉🎉🎉 LEAF_AI FULL-STACK ĐÃ KHỞI CHẠY THÀNH CÔNG! 🎉🎉🎉")
    print("=" * 68)
    print(f"  🌐 Giao diện Web (Frontend) : {website_url}")
    print(f"  🔌 API Backend Docs (Swagger): {docs_url}")
    print(f"  📡 API Base URL             : {api_url}")
    print("=" * 68)
    print("  👉 Nhấn Ctrl + C tại đây bất kỳ lúc nào để tắt toàn bộ hệ thống.")
    print("=" * 68 + "\n", flush=True)

    # Tự động mở trình duyệt nếu frontend sẵn sàng
    if fe_ok:
        try:
            webbrowser.open(website_url)
        except Exception:
            pass
    elif be_ok:
        try:
            webbrowser.open(docs_url)
        except Exception:
            pass

    # Thread in log ngầm
    t_be = threading.Thread(target=stream_logs, args=(backend_proc.stdout, "Backend"), daemon=True)
    t_be.start()
    if frontend_proc and frontend_proc.stdout:
        t_fe = threading.Thread(target=stream_logs, args=(frontend_proc.stdout, "Frontend"), daemon=True)
        t_fe.start()

    # Vòng lặp giữ tiến trình hoạt động
    while True:
        if backend_proc.poll() is not None:
            print(f"\n[!] Backend đã dừng (mã thoát: {backend_proc.returncode}).")
            break
        if frontend_proc and frontend_proc.poll() is not None:
            print(f"\n[!] Frontend đã dừng (mã thoát: {frontend_proc.returncode}).")
            break
        time.sleep(1)

    return 0


if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s, f: stop_all_processes() or sys.exit(0))
    signal.signal(signal.SIGTERM, lambda s, f: stop_all_processes() or sys.exit(0))
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        stop_all_processes()
        sys.exit(0)
    except Exception as exc:
        print(f"\n❌ LỖI KHỞI CHẠY: {exc}", file=sys.stderr)
        stop_all_processes()
        sys.exit(1)
