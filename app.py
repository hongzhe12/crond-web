from flask import Flask, render_template, request, redirect, url_for
import subprocess

app = Flask(__name__)

def get_crontab_lines():
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return result.stdout.strip().split("\n")

@app.route("/")
def index():
    lines = get_crontab_lines()
    return render_template("index.html", tasks=lines)

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        schedule = request.form["schedule"]
        command = request.form["command"]
        new_line = f"{schedule} {command}"
        lines = get_crontab_lines()
        lines.append(new_line)
        joined = "\n".join(lines) + "\n"
        subprocess.run(["crontab", "-"], input=joined, text=True)
        return redirect(url_for("index"))
    return render_template("add.html")

@app.route("/delete/<int:task_id>")
def delete(task_id):
    lines = get_crontab_lines()
    if 0 <= task_id < len(lines):
        del lines[task_id]
        new_crontab = "\n".join(lines) + "\n" if lines else ""
        subprocess.run(["crontab", "-"], input=new_crontab, text=True)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

