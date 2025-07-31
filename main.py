import json
import asyncio
import os
from pyrogram import Client, filters

# --- config ---
with open("config.json", "r") as f:
    config = json.load(f)

api_id = config["api_id"]
api_hash = config["api_hash"]
admin_id = config["admin_id"]
interval = config["interval_minutes"] * 60

# --- Pyrogram session ---
app = Client("main", api_id=api_id, api_hash=api_hash)

# --- مدیریت وضعیت pause ---
pause_file = "pause.flag"

def is_paused():
    return os.path.exists(pause_file)

def set_pause(state: bool):
    if state:
        open(pause_file, "w").close()
    else:
        if os.path.exists(pause_file):
            os.remove(pause_file)

# --- فرستادن پیام‌ها ---
async def send_loop():
    while True:
        if not is_paused():
            try:
                with open("config.json", "r") as f:
                    cfg = json.load(f)
                for group in cfg["groups"]:
                    try:
                        await app.send_message(group["chat_id"], group["message"])
                        with open("log.txt", "a") as log:
                            log.write(f"✅ Sent to {group['chat_id']}\n")
                    except Exception as e:
                        with open("log.txt", "a") as log:
                            log.write(f"❌ Error on {group['chat_id']}: {e}\n")
            except Exception as e:
                print(f"[ERROR] {e}")
        await asyncio.sleep(cfg["interval_minutes"] * 60)

# --- دستورات مدیریتی ---
@app.on_message(filters.command("pause") & filters.user(admin_id))
async def pause_cmd(_, msg):
    set_pause(True)
    await msg.reply("⏸ پیام‌دهی متوقف شد.")

@app.on_message(filters.command("resume") & filters.user(admin_id))
async def resume_cmd(_, msg):
    set_pause(False)
    await msg.reply("▶️ پیام‌دهی ادامه پیدا کرد.")

@app.on_message(filters.command("status") & filters.user(admin_id))
async def status_cmd(_, msg):
    with open("config.json", "r") as f:
        cfg = json.load(f)
    out = "📋 لیست گروه‌ها:\n\n"
    for g in cfg["groups"]:
        out += f"➤ {g['chat_id']}: {g['message']}\n"
    await msg.reply(out)

@app.on_message(filters.command("add") & filters.user(admin_id))
async def add_cmd(_, msg):
    try:
        parts = msg.text.split(" ", 2)
        chat_id = int(parts[1])
        msg_text = parts[2]
        with open("config.json", "r") as f:
            cfg = json.load(f)
        cfg["groups"].append({"chat_id": chat_id, "message": msg_text})
        with open("config.json", "w") as f:
            json.dump(cfg, f, indent=2)
        await msg.reply("✅ گروه جدید اضافه شد.")
    except:
        await msg.reply("❌ فرمت اشتباهه.\nمثال:\n`/add -1001234567890 پیام تست`")

@app.on_message(filters.command("remove") & filters.user(admin_id))
async def remove_cmd(_, msg):
    try:
        chat_id = int(msg.text.split(" ", 1)[1])
        with open("config.json", "r") as f:
            cfg = json.load(f)
        cfg["groups"] = [g for g in cfg["groups"] if g["chat_id"] != chat_id]
        with open("config.json", "w") as f:
            json.dump(cfg, f, indent=2)
        await msg.reply("🗑 گروه حذف شد.")
    except:
        await msg.reply("❌ فرمت اشتباهه.\nمثال:\n`/remove -1001234567890`")

@app.on_message(filters.command("setmsg") & filters.user(admin_id))
async def setmsg_cmd(_, msg):
    try:
        parts = msg.text.split(" ", 2)
        chat_id = int(parts[1])
        new_msg = parts[2]
        with open("config.json", "r") as f:
            cfg = json.load(f)
        for g in cfg["groups"]:
            if g["chat_id"] == chat_id:
                g["message"] = new_msg
        with open("config.json", "w") as f:
            json.dump(cfg, f, indent=2)
        await msg.reply("✏️ پیام بروزرسانی شد.")
    except:
        await msg.reply("❌ فرمت اشتباهه.\nمثال:\n`/setmsg -1001234567890 پیام جدید`")

# --- اجرای موازی ---
async def main():
    await app.start()
    await asyncio.gather(
        send_loop(),
        app.idle()
    )

if __name__ == "__main__":
    asyncio.run(main())