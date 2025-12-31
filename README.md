# ai-automation-assistant
AI Automation Assistant for Ubuntu 24.04 LTS

This code is free and open-source so you can modify it however you like!

# AI Local Command Agent

A local Linux automation agent that uses OpenAI to generate shell commands, asks for confirmation, and executes them **safely** with real-time output.

This tool is designed to bridge AI reasoning with **human-approved system administration**, not to blindly run commands.

---

## ✨ Features

- 🤖 AI generates Linux shell commands from natural language
- 🔐 Asks for **sudo password only when required**
- 📺 **Live command output** (apt updates, installs, systemctl, etc.)
- 🛑 Whitelist & blacklist command safety system
- 🧪 Dry-run mode (preview without execution)
- 📜 Full command + output logging
- 🔑 OpenAI API key embedded locally (no env vars required)

---

## ⚠️ Important Disclaimer

This project **executes real system commands**.

- You are responsible for reviewing commands before execution
- Do **not** run this on production machines without understanding the risks
- The AI output is **not trusted blindly** — confirmation is required

---

## 🧠 How It Works

1. You describe a task in natural language  

2. The AI returns **only shell commands**
3. The agent:
- Filters commands via whitelist / blacklist
- Shows them to you for confirmation
- Requests sudo password if needed
- Executes commands with live output
4. Everything is logged locally

---

## 🖥️ Requirements

- Linux (tested on Ubuntu/Debian)
- Python **3.10+**
- `sudo` access
- OpenAI API key

---

## 📦 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/XAndrr23/ai-automation-assistant.git
cd ai-automation-assistant

2️⃣ Create or download the virtual environment from the git (recommended)
python3 -m venv ai_agent_venv
source ai_agent_venv/bin/activate

3️⃣ Install dependencies
pip install openai

🔑 Configure API Key

Open ai_agent.py and paste your OpenAI API key:

client = OpenAI(
    api_key="sk-proj-PASTE_YOUR_KEY_HERE"
)

▶️ Usage

Run the agent:

python ai_agent.py


Example prompt:

Update system packages and install PHP 8.1


You will see:

AI-generated commands

Confirmation prompt

Live terminal output

Log file written on completion

##Note: If you downloaded the venv from the git, you don't need to do all these steps, just activate the venv and run the "ai_agent.py" file! :D
