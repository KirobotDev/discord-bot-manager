import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
from tkinter.scrolledtext import ScrolledText
from tkinter import Menu
import pygments.lexers
from pygments.token import Token
from pygments import lex
import os
import threading
import queue
import time
from bot_core import start_bot, stop_bot, reload_cog
from utils.encrypt import encrypt_token, decrypt_token, get_master_password
from utils.file_tools import save_file, load_file

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class CodeEditor(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#1e1e2e", **kwargs)
        self.text = ScrolledText(
            self, wrap="none", bg="#1e1e2e", fg="#f8f8f2", insertbackground="#ff79c6",
            font=("Courier New", 14), borderwidth=0, undo=True, autoseparators=True, maxundo=-1
        )
        self.text.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        
        self.line_numbers = tk.Text(
            self, width=4, bg="#282a36", fg="#6272a4", font=("Courier New", 14), bd=0
        )
        self.line_numbers.pack(side="left", fill="y", padx=(10, 5))
        self.line_numbers.config(state="disabled")
        
        self.text.bind("<KeyRelease>", self.on_key_release)
        self.text.bind("<MouseWheel>", self.on_mouse_wheel)
        self.text.bind("<Shift-MouseWheel>", self.on_shift_mouse_wheel)
        self.text.bind("<KeyPress>", self.handle_key_press)
        self.tag_configure("keyword", foreground="#ff79c6")
        self.tag_configure("builtin", foreground="#8be9fd")
        self.tag_configure("string", foreground="#50fa7b")
        self.tag_configure("comment", foreground="#6272a4")
        self.tag_configure("number", foreground="#bd93f9")
        self.tag_configure("operator", foreground="#ff5555")
        self.tag_configure("name", foreground="#f8f8f2")
        self.update_line_numbers()
    
    def on_mouse_wheel(self, event):
        self.text.yview_scroll(int(-event.delta / 120), "units")
        self.line_numbers.yview_scroll(int(-event.delta / 120), "units")
        return "break"
    
    def on_shift_mouse_wheel(self, event):
        self.text.xview_scroll(int(-event.delta / 120), "units")
        return "break"
    
    def handle_key_press(self, event):
        char = event.char
        pairs = { '(': ')', '[': ']', '{': '}', '"': '"', "'": "'" }
        
        try:
            sel_start = self.text.index("sel.first")
            sel_end = self.text.index("sel.last")
            selected_text = self.text.get(sel_start, sel_end)
        except tk.TclError:
            selected_text = None
        
        if char in pairs:
            self.text.delete("sel.first", "sel.last") if selected_text else None
            self.text.insert(tk.INSERT, char + (selected_text or "") + pairs[char])
            self.text.mark_set(tk.INSERT, f"{tk.INSERT} - {len(pairs[char])} chars")
            self.update_line_numbers()
            self.highlight()
            return "break"
        elif char in pairs.values():
            current_pos = self.text.index(tk.INSERT)
            next_char = self.text.get(current_pos, f"{current_pos} + 1 chars")
            if next_char == char:
                self.text.mark_set(tk.INSERT, f"{current_pos} + 1 chars")
                return "break"
        return None
    
    def on_key_release(self, event=None):
        self.update_line_numbers()
        self.highlight()
    
    def update_line_numbers(self):
        self.line_numbers.config(state="normal")
        self.line_numbers.delete(1.0, tk.END)
        line_count = int(self.text.index(tk.END).split('.')[0]) - 1
        for i in range(1, line_count + 1):
            self.line_numbers.insert(tk.END, f"{i}\n")
        self.line_numbers.config(state="disabled")
    
    def highlight(self):
        content = self.text.get("1.0", tk.END)
        self.text.mark_set("current", "1.0")
        tags = ["keyword", "builtin", "string", "comment", "number", "operator", "name"]
        for tag in tags:
            self.text.tag_remove(tag, "1.0", tk.END)
        
        for token, value in lex(content, pygments.lexers.PythonLexer()):
            end = self.text.index(f"current + {len(value)} chars")
            if token in Token.Keyword or token in Token.Keyword.Namespace:
                self.text.tag_add("keyword", "current", end)
            elif token in Token.Name.Builtin:
                self.text.tag_add("builtin", "current", end)
            elif token in Token.String:
                self.text.tag_add("string", "current", end)
            elif token in Token.Comment:
                self.text.tag_add("comment", "current", end)
            elif token in Token.Number:
                self.text.tag_add("number", "current", end)
            elif token in Token.Operator:
                self.text.tag_add("operator", "current", end)
            elif token in Token.Name:
                self.text.tag_add("name", "current", end)
            self.text.mark_set("current", end)
    
    def get(self, start, end):
        return self.text.get(start, end)
    
    def insert(self, index, chars):
        self.text.insert(index, chars)
    
    def delete(self, start, end):
        self.text.delete(start, end)
    
    def tag_configure(self, tagName, **kwargs):
        self.text.tag_configure(tagName, **kwargs)
    
    def tag_remove(self, tagName, start, end):
        self.text.tag_remove(tagName, start, end)
    
    def tag_add(self, tagName, start, end):
        self.text.tag_add(tagName, start, end)
    
    def index(self, index):
        return self.text.index(index)
    
    def mark_set(self, name, index):
        self.text.mark_set(name, index)

class DiscordBotManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Discord Bot Studio")
        self.geometry("1600x1000")
        self.resizable(True, True)
        
        self.bot_process = None
        self.log_queue = queue.Queue()
        self.current_file = None
        self.bot_running = False
        self.sidebar_visible = True
        self.editor_font_size = 14
        
        self.create_widgets()
        self.load_token()
        
        threading.Thread(target=self.process_logs, daemon=True).start()
    
    def create_widgets(self):
        self.grid_columnconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1)
        
        self.top_bar = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color="#44475a")
        self.top_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 0))
        self.top_bar.grid_columnconfigure(0, weight=1)
        
        self.toggle_button = ctk.CTkButton(
            self.top_bar, text="◄", command=self.toggle_sidebar, width=40, corner_radius=10,
            fg_color="#6272a4", hover_color="#8be9fd", font=("Arial", 14), text_color="#f8f8f2"
        )
        self.toggle_button.pack(side="left", padx=10)
        
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=15, fg_color="#282a36")
        self.sidebar.grid(row=1, column=0, sticky="ns", padx=(10, 5), pady=(5, 10))
        self.sidebar.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.sidebar, text="Cogs Explorer", font=("Arial", 18, "bold"), text_color="#ff79c6").pack(pady=(10, 5))
        self.file_tree = tk.Listbox(
            self.sidebar, bg="#282a36", fg="#f8f8f2", font=("Arial", 14),
            selectbackground="#44475a", selectforeground="#f8f8f2", borderwidth=0, highlightthickness=0
        )
        self.file_tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.file_tree.bind("<<ListboxSelect>>", self.on_file_select)
        self.file_tree.bind("<Button-3>", self.show_context_menu)
        
        self.context_menu = Menu(self.file_tree, tearoff=0)
        self.context_menu.add_command(label="Open", command=self.open_selected_file)
        self.context_menu.add_command(label="Delete", command=self.delete_selected_file)
        self.context_menu.add_command(label="Rename", command=self.rename_selected_file)
        
        ctk.CTkButton(
            self.sidebar, text="➕ Create Cog", command=self.create_new_cog_dialog, corner_radius=10,
            font=("Arial", 14, "bold"), fg_color="#bd93f9", hover_color="#ff79c6", text_color="#1e1e2e",
            compound="left", border_width=2, border_color="#6272a4"
        ).pack(pady=5)
        ctk.CTkButton(
            self.sidebar, text="⚙️ Editor Settings", command=self.open_editor_settings, corner_radius=10,
            font=("Arial", 14, "bold"), fg_color="#6272a4", hover_color="#8be9fd", text_color="#f8f8f2",
            compound="left", border_width=2, border_color="#bd93f9"
        ).pack(pady=5)
        
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1e1e2e")
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=(5, 10))
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        
        self.auth_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="#44475a")
        self.auth_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        ctk.CTkLabel(self.auth_frame, text="Master Password:", font=("Arial", 14), text_color="#f1fa8c").pack(side="left", padx=10)
        self.password_entry = ctk.CTkEntry(self.auth_frame, show="*", width=200, font=("Arial", 14))
        self.password_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(self.auth_frame, text="Discord Token:", font=("Arial", 14), text_color="#f1fa8c").pack(side="left", padx=10)
        self.token_entry = ctk.CTkEntry(self.auth_frame, show="*", width=350, font=("Arial", 14))
        self.token_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            self.auth_frame, text="🔒 Save Token", command=self.save_token, corner_radius=10,
            font=("Arial", 14, "bold"), fg_color="#6272a4", hover_color="#bd93f9", text_color="#f8f8f2",
            compound="left", border_width=2, border_color="#ff79c6"
        ).pack(side="left", padx=10)
        
        self.editor_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="#1e1e2e")
        self.editor_frame.pack(fill="both", expand=True, pady=(0, 10), padx=10)
        self.editor_frame.grid_columnconfigure(0, weight=1)
        self.editor_frame.grid_rowconfigure(0, weight=1)
        
        self.editor = CodeEditor(self.editor_frame)
        self.editor.pack(fill="both", expand=True)
        
        self.button_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="#44475a")
        self.button_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        ctk.CTkButton(
            self.button_frame, text="▶️ Launch Bot", command=self.launch_bot, corner_radius=10,
            font=("Arial", 14, "bold"), fg_color="#50fa7b", hover_color="#ff79c6", text_color="#1e1e2e",
            compound="left", border_width=2, border_color="#6272a4"
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            self.button_frame, text="⏹️ Stop Bot", command=self.stop_bot, corner_radius=10,
            font=("Arial", 14, "bold"), fg_color="#ff5555", hover_color="#ff79c6", text_color="#f8f8f2",
            compound="left", border_width=2, border_color="#6272a4"
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            self.button_frame, text="🔄 Reload Cogs", command=self.reload_cogs, corner_radius=10,
            font=("Arial", 14, "bold"), fg_color="#6272a4", hover_color="#8be9fd", text_color="#f8f8f2",
            compound="left", border_width=2, border_color="#bd93f9"
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            self.button_frame, text="💾 Save File", command=self.save_current_file, corner_radius=10,
            font=("Arial", 14, "bold"), fg_color="#bd93f9", hover_color="#ff79c6", text_color="#1e1e2e",
            compound="left", border_width=2, border_color="#6272a4"
        ).pack(side="left", padx=5)
        
        self.console_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="#282a36")
        self.console_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        ctk.CTkLabel(self.console_frame, text="Console Output", font=("Arial", 14, "bold"), text_color="#f1fa8c").pack(anchor="w", padx=10, pady=5)
        self.console = ScrolledText(
            self.console_frame, state="disabled", height=10, bg="#282a36",
            fg="#f8f8f2", font=("Courier New", 12), borderwidth=0
        )
        self.console.pack(fill="x", padx=10, pady=5)
        self.console.tag_configure("error", foreground="#ff5555")
        self.console.tag_configure("info", foreground="#50fa7b")
        self.console.tag_configure("warning", foreground="#f1fa8c")
        
        # Status bar
        self.status_bar = ctk.CTkFrame(self.main_frame, height=30, fg_color="#44475a")
        self.status_bar.pack(fill="x", padx=10)
        self.status_label = ctk.CTkLabel(
            self.status_bar, text="Bot: Offline | Cogs: 0", font=("Arial", 12), text_color="#f1fa8c"
        )
        self.status_label.pack(side="left", padx=10)
        
        self.load_files()
    
    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.grid_remove()
            self.toggle_button.configure(text="►")
            self.sidebar_visible = False
        else:
            self.sidebar.grid(row=1, column=0, sticky="ns", padx=(10, 5), pady=(5, 10))
            self.toggle_button.configure(text="◄")
            self.sidebar_visible = True
    
    def show_context_menu(self, event):
        selection = self.file_tree.curselection()
        if selection:
            self.file_tree.selection_set(selection)
            self.context_menu.post(event.x_root, event.y_root)
    
    def open_selected_file(self):
        selection = self.file_tree.curselection()
        if selection:
            file_name = self.file_tree.get(selection[0]).replace("📜 ", "")
            file_path = os.path.join("cogs", file_name)
            content = load_file(file_path)
            self.editor.delete(1.0, tk.END)
            self.editor.insert(tk.END, content)
            self.current_file = file_path
            self.editor.highlight()
            self.log(f"Opened {file_name}", tag="info")
    
    def delete_selected_file(self):
        selection = self.file_tree.curselection()
        if selection:
            file_name = self.file_tree.get(selection[0]).replace("📜 ", "")
            file_path = os.path.join("cogs", file_name)
            if messagebox.askyesno("Confirm Delete", f"Delete {file_name}?"):
                try:
                    os.remove(file_path)
                    self.load_files()
                    self.log(f"Deleted {file_name}", tag="info")
                    if self.current_file == file_path:
                        self.current_file = None
                        self.editor.delete(1.0, tk.END)
                except Exception as e:
                    self.log(f"Error deleting {file_name}: {str(e)}", tag="error")
    
    def rename_selected_file(self):
        selection = self.file_tree.curselection()
        if selection:
            file_name = self.file_tree.get(selection[0]).replace("📜 ", "")
            dialog = Toplevel(self)
            dialog.title("Rename Cog")
            dialog.geometry("400x150")
            dialog.configure(bg="#282a36")
            
            ctk.CTkLabel(dialog, text="New Name:", font=("Arial", 14), text_color="#f1fa8c").pack(pady=10)
            new_name_entry = ctk.CTkEntry(dialog, width=200, font=("Arial", 14))
            new_name_entry.insert(0, file_name.replace(".py", ""))
            new_name_entry.pack(pady=5)
            
            def rename_file():
                new_name = new_name_entry.get().strip() + ".py"
                if not new_name.endswith(".py") or not new_name[:-3].isidentifier():
                    messagebox.showerror("Error", "Invalid file name")
                    return
                old_path = os.path.join("cogs", file_name)
                new_path = os.path.join("cogs", new_name)
                try:
                    os.rename(old_path, new_path)
                    self.load_files()
                    self.log(f"Renamed {file_name} to {new_name}", tag="info")
                    if self.current_file == old_path:
                        self.current_file = new_path
                    dialog.destroy()
                except Exception as e:
                    self.log(f"Error renaming {file_name}: {str(e)}", tag="error")
            
            ctk.CTkButton(
                dialog, text="Rename", command=rename_file, corner_radius=10,
                font=("Arial", 14, "bold"), fg_color="#bd93f9", hover_color="#ff79c6", text_color="#1e1e2e"
            ).pack(pady=10)
    
    def open_editor_settings(self):
        dialog = Toplevel(self)
        dialog.title("Editor Settings")
        dialog.geometry("400x150")
        dialog.configure(bg="#282a36")
        
        ctk.CTkLabel(dialog, text="Font Size:", font=("Arial", 14), text_color="#f1fa8c").pack(pady=10)
        font_size_entry = ctk.CTkEntry(dialog, width=100, font=("Arial", 14))
        font_size_entry.insert(0, str(self.editor_font_size))
        font_size_entry.pack(pady=5)
        
        def apply_settings():
            try:
                new_size = int(font_size_entry.get())
                if 8 <= new_size <= 24:
                    self.editor_font_size = new_size
                    self.editor.text.configure(font=("Courier New", new_size))
                    self.editor.line_numbers.configure(font=("Courier New", new_size))
                    self.editor.update_line_numbers()
                    self.editor.highlight()
                self.log("Editor settings updated", tag="info")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Invalid font size")
        
        ctk.CTkButton(
            dialog, text="Apply", command=apply_settings, corner_radius=10,
            font=("Arial", 14, "bold"), fg_color="#bd93f9", hover_color="#ff79c6", text_color="#1e1e2e"
        ).pack(pady=10)
    
    def load_files(self):
        self.file_tree.delete(0, tk.END)
        cog_count = 0
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                self.file_tree.insert(tk.END, f"📜 {file}")
                cog_count += 1
        self.update_status(cog_count=cog_count)
    
    def on_file_select(self, event):
        self.open_selected_file()
    
    def create_new_cog_dialog(self):
        dialog = Toplevel(self)
        dialog.title("Create New Cog")
        dialog.geometry("400x200")
        dialog.configure(bg="#282a36")
        
        ctk.CTkLabel(dialog, text="Cog Name:", font=("Arial", 14), text_color="#f1fa8c").pack(pady=10)
        cog_name_entry = ctk.CTkEntry(dialog, width=200, font=("Arial", 14))
        cog_name_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Command Name:", font=("Arial", 14), text_color="#f1fa8c").pack(pady=10)
        command_name_entry = ctk.CTkEntry(dialog, width=200, font=("Arial", 14))
        command_name_entry.pack(pady=5)
        
        def create_cog():
            cog_name = cog_name_entry.get().strip()
            command_name = command_name_entry.get().strip() or cog_name.lower()
            if not cog_name:
                messagebox.showerror("Error", "Cog name cannot be empty")
                return
            file_path = os.path.join("cogs", f"{cog_name}.py")
            template = f"""from discord.ext import commands

class {cog_name.capitalize()}(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def {command_name.lower()}(self, ctx):
        await ctx.send("Command {command_name.lower()} executed!")

async def setup(bot):
    await bot.add_cog({cog_name.capitalize()}(bot))
"""
            save_file(file_path, template)
            self.load_files()
            self.log(f"New cog {cog_name}.py created with command !{command_name}", tag="info")
            dialog.destroy()
        
        ctk.CTkButton(
            dialog, text="Create", command=create_cog, corner_radius=10,
            font=("Arial", 14, "bold"), fg_color="#bd93f9", hover_color="#ff79c6", text_color="#1e1e2e"
        ).pack(pady=10)
    
    def save_current_file(self):
        if not hasattr(self, "current_file") or self.current_file is None:
            messagebox.showwarning("Warning", "No file selected. Please select a cog from the explorer.")
            self.log("No file selected for saving", tag="error")
            return
        content = self.editor.get(1.0, tk.END).strip()
        save_file(self.current_file, content)
        messagebox.showinfo("Saved", "File saved successfully")
        self.log(f"Saved {self.current_file}", tag="info")
    
    def save_token(self):
        token = self.token_entry.get()
        password = self.password_entry.get()
        if token and password:
            try:
                encrypted = encrypt_token(token, password)
                with open("token.enc", "wb") as f:
                    f.write(encrypted)
                messagebox.showinfo("Success", "Token encrypted and saved")
                self.log("Token saved successfully", tag="info")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save token: {str(e)}")
                self.log(f"Error saving token: {str(e)}", tag="error")
    
    def load_token(self):
        if os.path.exists("token.enc"):
            password = self.password_entry.get()
            if not password:
                password = get_master_password()
                self.password_entry.insert(0, password)
            try:
                with open("token.enc", "rb") as f:
                    encrypted = f.read()
                token = decrypt_token(encrypted, password)
                self.token_entry.insert(0, token)
                self.log("Token loaded successfully", tag="info")
            except Exception as e:
                messagebox.showerror("Error", "Invalid master password or corrupted token")
                self.log(f"Error loading token: {str(e)}", tag="error")
    
    def launch_bot(self):
        if self.bot_process is None:
            token = self.token_entry.get()
            if token:
                self.bot_process = threading.Thread(target=start_bot, args=(token, self.log_queue))
                self.bot_process.start()
                self.bot_running = True
                self.log("Bot launch initiated", tag="info")
                self.update_status()
    
    def stop_bot(self):
        if self.bot_process:
            stop_bot()
            self.bot_process = None
            self.bot_running = False
            self.log("Bot stopped", tag="info")
            self.update_status()
    
    def reload_cogs(self):
        if self.bot_process:
            try:
                for file in os.listdir("cogs"):
                    if file.endswith(".py"):
                        cog_name = file[:-3]
                        reload_cog(cog_name)
                        self.log(f"Cog {cog_name} reloaded", tag="info")
            except Exception as e:
                self.log(f"Error reloading cogs: {str(e)}", tag="error")
    
    def process_logs(self):
        while True:
            try:
                message = self.log_queue.get_nowait()
                tag = "error" if "ERROR" in message else ("warning" if "WARNING" in message else "info")
                self.log(message, tag=tag)
            except queue.Empty:
                pass
            time.sleep(0.1)
    
    def log(self, message, tag="info"):
        self.console.config(state="normal")
        self.console.insert(tk.END, f"{message}\n", tag)
        self.console.see(tk.END)
        self.console.config(state="disabled")
    
    def update_status(self, cog_count=None):
        if cog_count is None:
            cog_count = len([f for f in os.listdir("cogs") if f.endswith(".py")])
        status = "Online" if self.bot_running else "Offline"
        self.status_label.configure(text=f"Bot: {status} | Cogs: {cog_count}")

if __name__ == "__main__":
    app = DiscordBotManager()
    app.mainloop()