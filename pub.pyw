import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
from datetime import datetime

class BlogPublisher:
    def __init__(self, root):
        self.root = root
        self.root.title("博客发布工具")
        self.root.geometry("300x120")
        
        self.btn = ttk.Button(root, text="选择 .md 文件并发布", command=self.publish)
        self.btn.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

    def publish(self):
        file_path = filedialog.askopenfilename(filetypes=[("Markdown files", "*.md")])
        if not file_path:
            return

        original_name = os.path.basename(file_path)
        title = os.path.splitext(original_name)[0]
        today = datetime.now().strftime("%Y-%m-%d")
        new_filename = f"{today}-{title}.md"
        
        dest_dir = "_posts"
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, new_filename)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        front_matter = f"---\nlayout: default\ntitle: {title}\ndate: {today}\n---\n\n"

        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(front_matter + content)

        # 执行 Git 自动化操作
        self.git_commit_and_push(dest_path, title)

    def git_commit_and_push(self, file_path, title):
        try:
            # 1. 将新文件添加到暂存区
            subprocess.run(["git", "add", file_path], check=True, capture_output=True)
            
            # 2. 提交更改
            commit_message = f"Auto-publish: {title}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True)
            
            # 3. 推送到远程仓库
            # 禁用按钮防止重复点击，并提示正在推送
            self.btn.config(state=tk.DISABLED, text="正在推送到 GitHub...")
            self.root.update()
            
            subprocess.run(["git", "push"], check=True, capture_output=True)
            
            messagebox.showinfo("发布成功", f"文件已保存并成功推送到 GitHub！\n\n文件路径: {file_path}")
            
        except subprocess.CalledProcessError as e:
            # 如果 Git 命令执行失败，捕获错误输出并显示
            error_msg = e.stderr.decode('utf-8', errors='replace') if e.stderr else "未知 Git 错误"
            messagebox.showerror("推送失败", f"本地文件已生成，但 Git 操作失败。\n\n错误信息:\n{error_msg}")
        finally:
            # 恢复按钮状态
            self.btn.config(state=tk.NORMAL, text="选择 .md 文件并发布")

if __name__ == "__main__":
    root = tk.Tk()
    app = BlogPublisher(root)
    root.mainloop()
