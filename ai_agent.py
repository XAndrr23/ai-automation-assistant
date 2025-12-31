#!/usr/bin/env python3

import subprocess
import difflib
import os
import sys
import getpass
from datetime import datetime
from openai import OpenAI, OpenAIError

# ==========================
# CONFIGURATION
# ==========================

LOG_FILE = "ai_command_log.txt"
DRY_RUN = False  # True = preview only, do not execute

WHITELIST = [
    "sudo apt",
    "apt",
    "systemctl",
    "service",
    "mkdir",
    "rm",
    "cp",
    "mv",
    "echo",
    "cat",
    "nano",
    "touch",
    "chmod",
    "chown"
]

BLACKLIST = [
    "rm -rf /",
    "mkfs",
    "dd if=",
    ":(){:|:&};:",
    "shutdown",
    "reboot",
    "poweroff"
]

# ==========================
# OPENAI CLIENT (HARDCODED)
# ==========================

client = OpenAI(
    api_key="your-api-key-here"  # <-- Put your API key here inside quotes
)

# ==========================
# SUDO HANDLING
# ==========================

SUDO_PASSWORD = None

def get_sudo_password():
    global SUDO_PASSWORD
    if SUDO_PASSWORD is None:
        SUDO_PASSWORD = getpass.getpass("[sudo] password: ")
    return SUDO_PASSWORD

# ==========================
# AI FUNCTIONS
# ==========================

def ask_ai(prompt: str) -> str:
    """
    Ask AI to generate ONLY shell commands.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Linux Ubuntu Server 24.04 LTS automation assistant."
                        "Return ONLY shell commands, one per line."
                        "Do not explain anything."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        print(f"[AI ERROR] {e}")
        return ""

# ==========================
# SAFETY
# ==========================

def is_safe_command(cmd: str) -> bool:
    for bad in BLACKLIST:
        if bad in cmd:
            print(f"[BLOCKED - blacklist] {cmd}")
            return False

    for ok in WHITELIST:
        if cmd.startswith(ok):
            return True

    print(f"[BLOCKED - not whitelisted] {cmd}")
    return False

# ==========================
# DIFF PREVIEW
# ==========================

def preview_diff(file_path: str, new_content: str):
    if not os.path.exists(file_path):
        print(f"[+] File will be created: {file_path}")
        return

    with open(file_path, "r") as f:
        old = f.read()

    diff = difflib.unified_diff(
        old.splitlines(),
        new_content.splitlines(),
        fromfile="current",
        tofile="ai",
        lineterm=""
    )

    diff_text = "\n".join(diff)
    if diff_text:
        print("\n===== FILE DIFF =====")
        print(diff_text)
        print("=====================")

# ==========================
# COMMAND EXECUTION (LIVE)
# ==========================

def run_command_live(cmd: str) -> str:
    needs_sudo = cmd.strip().startswith("sudo")

    if needs_sudo:
        sudo_pass = get_sudo_password()
        cmd = cmd.replace("sudo", "sudo -S", 1)

    print(f"\n>> {cmd}")

    process = subprocess.Popen(
        cmd,
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    if needs_sudo:
        process.stdin.write(sudo_pass + "\n")
        process.stdin.flush()

    output = ""

    for line in process.stdout:
        print(line, end="")
        output += line

    process.wait()
    return output

def run_commands(commands):
    results = []

    for cmd in commands:
        if not is_safe_command(cmd):
            continue

        if DRY_RUN:
            print(f"[DRY-RUN] {cmd}")
            results.append((cmd, "[DRY-RUN]"))
            continue

        try:
            out = run_command_live(cmd)
            results.append((cmd, out))
        except Exception as e:
            print(f"[ERROR] {e}")
            results.append((cmd, str(e)))

    return results

# ==========================
# LOGGING
# ==========================

def log_results(results):
    with open(LOG_FILE, "a") as f:
        f.write(f"\n==== {datetime.now()} ====\n")
        for cmd, out in results:
            f.write(f"$ {cmd}\n{out}\n")
        f.write("==== END ====\n")

# ==========================
# MAIN LOOP
# ==========================

def main():
    print("=== AI AUTOMATION ASSISTANT ===")
    print(f"Dry-run: {'ON' if DRY_RUN else 'OFF'}")

    while True:
        task = input("\nEnter task for AI (or 'exit'): ").strip()
        if task.lower() == "exit":
            break

        ai_output = ask_ai(task)
        if not ai_output:
            print("No AI commands generated.")
            continue

        print("\n[AI suggested commands]")
        print(ai_output)

        commands = [
            line.strip()
            for line in ai_output.splitlines()
            if line.strip() and not line.startswith("#")
        ]

        if not commands:
            print("No commands to execute.")
            continue

        print("\n===== CONFIRM =====")
        for c in commands:
            print(c)

        if input("Execute these commands? [y/N]: ").lower() != "y":
            print("Aborted.")
            continue

        results = run_commands(commands)
        log_results(results)

        print(f"\n[✔] Done. Logged to {LOG_FILE}")

if __name__ == "__main__":
    main()
