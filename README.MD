# 🎮 Discord Bot Studio

**Craft, manage, and deploy Discord bots with ease in a sleek, VS Code-inspired interface!**

Welcome to **Discord Bot Studio**, a powerful and intuitive GUI application built with Python and `customtkinter` to streamline Discord bot development. Featuring a modern dark-themed interface with neon accents, a robust code editor, and seamless bot management, this tool empowers developers to create, edit, and control Discord bots effortlessly. Whether you're a beginner or a seasoned coder, Discord Bot Studio makes bot development fun and efficient!

---

## ✨ Features

### 🚀 Code Editor
- **VS Code-like Experience**: Auto-closing brackets (`()`, `[]`, `{}`) and quotes (`""`, `''`) with smart cursor positioning, just like Visual Studio Code.
- **Syntax Highlighting**: Monokai-themed syntax highlighting for Python, with support for keywords, strings, comments, and more.
- **No Scrollbars, All Control**: Hidden scrollbars for a clean look, with smooth scrolling via mouse wheel (vertical), `Shift+MouseWheel` (horizontal), or arrow keys.
- **Line Numbers & Undo/Redo**: Persistent line numbers and full undo/redo support for a professional coding experience.
- **Customizable**: Adjust font size via the "⚙️ Editor Settings" button.

### 📂 Cogs Explorer
- **Compact & Organized**: Fixed 300-pixel width sidebar, toggleable with `◄`/`►` buttons for a distraction-free workspace.
- **File Management**: Create, open, delete, and rename cogs with a right-click context menu.
- **Simplified Cog Creation**: Use the "➕ Create Cog" button to generate new cogs with customizable command templates.

### 🤖 Bot Management
- **Seamless Control**: Launch, stop, and reload cogs with dedicated buttons (`▶️ Launch Bot`, `⏹️ Stop Bot`, `🔄 Reload Cogs`).
- **Token Security**: Encrypt and save your Discord token with a master password for secure storage.
- **Real-time Logs**: Color-coded console output (green for info, red for errors, yellow for warnings) to monitor bot activity.

### 🎨 Aesthetics
- **Dark Theme**: Eye-friendly dark interface (`#1e1e2e`, `#282a36`) with vibrant neon accents (pink `#ff79c6`, blue `#6272a4`, green `#50fa7b`, purple `#bd93f9`).
- **Glassmorphism Design**: Rounded frames and stylized buttons with hover effects for a modern, polished look.
- **Snappy Performance**: Optimized for responsiveness, mimicking the feel of C-based GUIs.

### ⚙️ Supported Commands
- `!ping`: Responds with "Pong!" to test bot connectivity.
- `!kaka`: Sends a cheeky "J'tes chié dessus ok ?" message.

---

## 🛠️ Installation

### Prerequisites
- **Python 3.8+**: Ensure Python is installed ([Download Python](https://www.python.org/downloads/)).
- **Virtual Environment**: Recommended for dependency management.
- **Dependencies**:
  ```bash
  pip install customtkinter==5.2.2 discord.py pygments
  ```

### Setup Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/discord-bot-studio.git
   cd discord-bot-studio
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `cogs/` Directory**:
   ```bash
   mkdir cogs
   ```

5. **Add Example Cogs**:
   Create `cogs/ping.py`:
   ```python
   from discord.ext import commands

   class Ping(commands.Cog):
       def __init__(self, bot):
           self.bot = bot
       
       @commands.command()
       async def ping(self, ctx):
           await ctx.send("Pong!")

   async def setup(bot):
       await bot.add_cog(Ping(bot))
   ```

   Create `cogs/kaka.py`:
   ```python
   from discord.ext import commands

   class Kaka(commands.Cog):
       def __init__(self, bot):
           self.bot = bot
       
       @commands.command()
       async def kaka(self, ctx):
           await ctx.send("J'tes chié dessus ok ?")

   async def setup(bot):
       await bot.add_cog(Kaka(bot))
   ```

6. **Run the Application**:
   ```bash
   python manager.py
   ```

---

## 📖 Usage

1. **Launch Discord Bot Studio**:
   Run `python manager.py` to open the GUI.

2. **Enter Credentials**:
   - Input your **Discord bot token** (from [Discord Developer Portal](https://discord.com/developers/applications)).
   - Provide a **master password** to encrypt and save the token securely.
   - Click `🔒 Save Token` to store the encrypted token.

3. **Manage Cogs**:
   - Use the **Cogs Explorer** to view `.py` files in the `cogs/` directory.
   - Right-click a cog for options: **Open**, **Delete**, or **Rename**.
   - Click `➕ Create Cog` to generate a new cog with a custom command.

4. **Edit Code**:
   - Open a cog in the **Code Editor** to modify it.
   - Enjoy **VS Code-like auto-closing** for brackets (`()`, `[]`, `{}`) and quotes (`""`, `''`).
   - Save changes with the `💾 Save File` button.

5. **Control the Bot**:
   - Click `▶️ Launch Bot` to start the bot with your token.
   - Use `🔄 Reload Cogs` to update cogs without restarting.
   - Click `⏹️ Stop Bot` to shut down the bot.
   - Monitor logs in the **Console Output** section.

6. **Test Commands**:
   - In your Discord server, use:
     - `!ping` → "Pong!"
     - `!kaka` → "J'tes chié dessus ok ?"

---

## 🖼️ Screenshots

| **Cogs Explorer & Code Editor** | **Bot Running with Console Logs** |
|--------------------------------|------------------------------------|
| ![Cogs Explorer](screenshots/explorer.png) | ![Bot Running](screenshots/bot_running.png) |

*Note: Screenshots are placeholders. Add actual screenshots to the `screenshots/` directory and update paths.*

---

## 🛠️ Troubleshooting

- **Auto-closing not working?**
  - Ensure the `<KeyPress>` binding in `manager.py` (CodeEditor class) is active.
  - Test typing `(` or `"` to verify `()` or `""` appears with the cursor inside.
- **Can’t scroll in the editor?**
  - Confirm scrollbars are hidden and test mouse wheel (`<MouseWheel>`) or `Shift+MouseWheel`.
  - Use arrow keys as an alternative.
- **Bot not connecting?**
  - Verify your Discord token is valid (check [Discord Developer Portal](https://discord.com/developers/applications)).
  - Ensure the master password matches the one used for `token.enc`.
- **Cogs not loading?**
  - Check `cogs/` directory for `.py` files with correct syntax.
  - Review console logs for errors (e.g., “Failed to load cog”).
- **Interface looks off?**
  - Ensure `customtkinter==5.2.2` is installed (`pip install customtkinter==5.2.2`).
  - Verify fonts (`Arial`, `Courier New`); fallback to `TkDefaultFont` if needed.

---

## 🚀 Future Enhancements
- **Auto-indentation**: Automatically indent code for better readability.
- **Code Snippets**: Add templates for common Discord bot commands.
- **Theme Customization**: Allow switching between light and dark themes.
- **Real-time Error Checking**: Highlight syntax errors as you type.

---

## 🤝 Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/awesome-feature`).
3. Commit changes (`git commit -m "Add awesome feature"`).
4. Push to the branch (`git push origin feature/awesome-feature`).
5. Open a pull request.

---

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🌟 Acknowledgements
- Built with [customtkinter](https://github.com/TomSchimansky/CustomTkinter) for the sleek UI.
- Powered by [discord.py](https://github.com/Rapptz/discord.py) for Discord bot functionality.
- Syntax highlighting via [Pygments](https://pygments.org/).

---

**Discord Bot Studio** – Build your Discord bot with style and ease! 🚀