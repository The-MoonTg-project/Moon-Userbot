import os
import platform
import psutil
import time
from datetime import timedelta

from bottle import Bottle, request, response, redirect, SimpleTemplate

app = Bottle()

BASE_PATH = os.path.abspath(os.getcwd())
PUBLIC_PATH = os.path.join(BASE_PATH, "public")
START_TIME = time.time()

def get_stats():
    uptime_seconds = int(time.time() - START_TIME)
    uptime_str = str(timedelta(seconds=uptime_seconds))
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=0.1)
    return {
        "uptime": uptime_str,
        "memory_used": memory.used // (1024 * 1024),
        "memory_total": memory.total // (1024 * 1024),
        "memory_percent": int(memory.percent),
        "cpu_percent": int(cpu_percent),
        "platform": platform.system(),
        "python_version": platform.python_version(),
    }

def get_builtin_modules():
    modules = []
    modules_path = f"{BASE_PATH}/modules"
    for f in os.listdir(modules_path):
        if f.endswith(".py") and not f.startswith("_") and f not in ("loader.py", "__init__.py"):
            modules.append({"name": f[:-3], "type": "builtin"})
    return modules

def get_custom_modules():
    custom_path = f"{BASE_PATH}/modules/custom_modules"
    modules = []
    if os.path.exists(custom_path):
        for f in os.listdir(custom_path):
            if f.endswith(".py"):
                modules.append({"name": f[:-3], "type": "custom"})
    return modules

def get_all_modules():
    return get_builtin_modules() + get_custom_modules()

def render_page(content_name, page, **vars):
    with open(os.path.join(PUBLIC_PATH, "base.html")) as f:
        base_tpl = f.read()
    with open(os.path.join(PUBLIC_PATH, content_name)) as f:
        content_tpl = f.read()
    
    content = SimpleTemplate(content_tpl).render(**vars)
    vars["base"] = content
    vars["page"] = page
    return SimpleTemplate(base_tpl).render(**vars)

@app.get("/")
def index():
    stats = get_stats()
    modules = get_all_modules()
    builtin = get_builtin_modules()
    custom = get_custom_modules()
    message = request.params.get("message", "")
    message_type = request.params.get("type", "")
    
    return render_page("overview.html", "overview",
        uptime=stats["uptime"],
        memory_used=stats["memory_used"],
        memory_total=stats["memory_total"],
        memory_percent=stats["memory_percent"],
        cpu_percent=stats["cpu_percent"],
        module_count=len(modules),
        platform=stats["platform"],
        python_version=stats["python_version"],
        builtin_count=len(builtin),
        custom_count=len(custom),
        message=message,
        message_type=message_type
    )

@app.get("/modules")
def modules_page():
    modules = get_all_modules()
    builtin = get_builtin_modules()
    custom = get_custom_modules()
    message = request.params.get("message", "")
    message_type = request.params.get("type", "")
    
    return render_page("modules.html", "modules",
        modules=modules,
        builtin_count=len(builtin),
        custom_count=len(custom),
        message=message,
        message_type=message_type
    )

@app.post("/modules/delete")
def delete_module():
    module_name = request.forms.get("module_name")
    custom_path = f"{BASE_PATH}/modules/custom_modules/{module_name}.py"
    if os.path.exists(custom_path):
        os.remove(custom_path)
        return redirect(f"/modules?message={module_name}+deleted&type=success")
    return redirect("/modules?message=Module+not+found&type=error")

@app.get("/logs")
def logs():
    log_file = f"{BASE_PATH}/moonlogs.txt"
    logs_content = "No logs yet"
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            lines = f.readlines()
            logs_content = "".join(lines[-500:]) or "No logs yet"
    
    message = request.params.get("message", "")
    message_type = request.params.get("type", "")
    
    return render_page("logs.html", "logs",
        logs=logs_content,
        message=message,
        message_type=message_type
    )

@app.get("/logs/clear")
def clear_logs():
    log_file = f"{BASE_PATH}/moonlogs.txt"
    if os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("")
    return redirect("/logs?message=Logs+cleared&type=success")

@app.get("/api/stats")
def api_stats():
    import json
    response.content_type = "application/json"
    return json.dumps(get_stats())

@app.get("/api/modules")
def api_modules():
    import json
    response.content_type = "application/json"
    return json.dumps(get_all_modules())

if __name__ == "__main__":
    from bottle import run
    run(app, host="0.0.0.0", port=5000, debug=False)
