from flask import Flask, render_template, request, redirect, url_for, flash
import subprocess
import os
import time
from typing import List, Dict, Tuple, Optional
from cron_descriptor import Options, ExpressionDescriptor

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 用于flash消息

# 常量定义
PRESETS = {
    # 每分钟
    "每分钟执行一次": "* * * * *",
    # 每几分钟
    "每2分钟执行一次": "*/2 * * * *",
    "每3分钟执行一次": "*/3 * * * *",
    "每4分钟执行一次": "*/4 * * * *",
    "每5分钟执行一次": "*/5 * * * *",
    "每10分钟执行一次": "*/10 * * * *",
    "每15分钟执行一次": "*/15 * * * *",
    "每20分钟执行一次": "*/20 * * * *",
    "每30分钟执行一次": "*/30 * * * *",
    # 每小时
    "每小时执行一次": "0 * * * *",
    "每小时的第15分钟执行": "15 * * * *",
    "每小时的第30分钟执行": "30 * * * *",
    "每小时的第45分钟执行": "45 * * * *",
    # 每天
    "每天凌晨执行一次": "0 0 * * *",
    "每天早上6点执行": "0 6 * * *",
    "每天中午12点执行": "0 12 * * *",
    "每天下午6点执行": "0 18 * * *",
    # 每周
    "每周日凌晨执行一次": "0 0 * * 0",
    "每周一凌晨执行一次": "0 0 * * 1",
    "每周二凌晨执行一次": "0 0 * * 2",
    "每周三凌晨执行一次": "0 0 * * 3",
    "每周四凌晨执行一次": "0 0 * * 4",
    "每周五凌晨执行一次": "0 0 * * 5",
    "每周六凌晨执行一次": "0 0 * * 6",
    # 每月
    "每月1号凌晨执行一次": "0 0 1 * *",
    # 每年
    "每年1月1号凌晨执行一次": "0 0 1 1 *"
}
SCRIPT_TYPES = {
    "python": {"ext": ".py", "interpreter": "python"},
    "shell": {"ext": ".sh", "interpreter": "sh"}
}
SCRIPT_DIR = "scripts"

os.makedirs(SCRIPT_DIR, exist_ok=True)



def get_crontab_lines() -> List[str]:
    """获取当前用户的crontab内容"""
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    context = result.stdout.strip().split("\n")
    context = list(map(lambda x: x.strip(), context))  # 去除每行的前后空格
    if result.returncode == 0 and context!=['']:
        return context
    else:
        return []


def save_crontab(lines: List[str]) -> bool:
    """保存crontab内容"""
    result = subprocess.run(
        ["crontab", "-"],
        input="\n".join(lines) + "\n",
        text=True,
        capture_output=True
    )
    return result.returncode == 0


def create_script(script_type: str, content: str) -> Tuple[str, str]:
    """创建脚本文件并返回(脚本路径, 执行命令)"""
    script_name = f"task_{int(time.time() * 1000)}"
    script_ext = SCRIPT_TYPES[script_type]["ext"]
    script_path = os.path.abspath(os.path.join(SCRIPT_DIR, f"{script_name}{script_ext}"))

    with open(script_path, "w") as f:
        if script_type == "shell":
            f.write(f"#!/bin/bash\n{content}")
        else:
            f.write(content)

    if script_type == "shell":
        os.chmod(script_path, 0o755)

    interpreter = SCRIPT_TYPES[script_type]["interpreter"]
    return script_path, f"{interpreter} {script_path}"


def parse_cron_task(task: str) -> Optional[Tuple[str, str]]:
    """解析cron任务为(时间表达式, 命令)"""
    parts = task.strip().split()
    return " ".join(parts[:5]), " ".join(parts[5:]) if len(parts) >= 6 else None


def get_script_content(script_path: str) -> str:
    """读取脚本内容并移除shebang行"""
    try:
        script_path = os.path.abspath(script_path)
        with open(script_path, "r") as f:
            content = f.read()
            return content[content.find("\n") + 1:].strip() if content.startswith("#!") else content.strip()
    except Exception as e:
        print(f"Error reading script: {e}")
        return f"# 无法读取原始脚本\n# 错误: {str(e)}"


def get_preset(schedule: str) -> str:
    """根据时间表达式返回匹配的预设key"""
    inverted_presets = {v: k for k, v in PRESETS.items()}
    return inverted_presets.get(schedule, "")


@app.route("/")
def index():
    return render_template("index.html", tasks=get_crontab_lines())


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        schedule = request.form["schedule"]
        script_type = request.form["script_type"]
        script_content = request.form["script_content"]

        _, command = create_script(script_type, script_content)
        lines = get_crontab_lines()
        lines.append(f"{schedule} {command}")

        if not save_crontab(lines):
            flash("保存crontab失败", "error")
        return redirect(url_for("index"))

    return render_template("add.html", presets=PRESETS)


@app.route("/delete/<int:task_id>")
def delete(task_id):
    lines = get_crontab_lines()
    if 0 <= task_id < len(lines):
        task_info = parse_cron_task(lines[task_id])
        if task_info:
            _, command = task_info
            script_path = command.split()[1]  # 获取脚本路径
            try:
                os.remove(script_path)  # 删除脚本文件
                # 删除对应的日志文件
                log_path = get_log_path(script_path)
                if os.path.exists(log_path):
                    os.remove(log_path)
            except Exception as e:
                print(f"Error deleting files: {e}")
                flash("删除相关文件失败", "error")
        del lines[task_id]
        if not save_crontab(lines):
            flash("删除任务失败", "error")
    return redirect(url_for("index"))


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    lines = get_crontab_lines()
    if not (0 <= task_id < len(lines)):
        return redirect(url_for("index"))

    if request.method == "POST":
        schedule = request.form["schedule"]
        script_type = request.form["script_type"]
        script_content = request.form["script_content"]

        _, command = create_script(script_type, script_content)
        lines[task_id] = f"{schedule} {command}"

        if not save_crontab(lines):
            flash("更新任务失败", "error")
        return redirect(url_for("index"))

    # 解析现有任务
    task_info = parse_cron_task(lines[task_id])
    if not task_info:
        flash("任务格式无效", "error")
        return redirect(url_for("index"))

    schedule, command = task_info
    script_type = "python" if command.startswith("python ") else "shell"
    script_path = command[7:] if script_type == "python" else command[3:]
    script_content = get_script_content(script_path)

    return render_template(
        "edit.html",
        presets=PRESETS,
        schedule=schedule,
        script_content=script_content,
        script_type=script_type,
        selected_preset=get_preset(schedule)
    )

@app.route("/get_description")
def get_description_route():
    cron = request.args.get('cron', '')
    try:
        options = Options()
        options.locale_code = "zh_CN"
        return str(ExpressionDescriptor(cron, options))
    except Exception as e:
        print(f"Error parsing cron expression {cron}: {e}")
        return "无效的 Crontab 表达式"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)