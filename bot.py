import os
import json
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = Path("token.txt").read_text(encoding="utf-8").strip()
MEM_FILE = Path("memory.json")

# ---------- 记忆 ----------
def load_mem():
    if MEM_FILE.exists():
        try:
            return json.loads(MEM_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"facts": [], "last": ""}

def save_mem(mem):
    MEM_FILE.write_text(json.dumps(mem, ensure_ascii=False, indent=2), encoding="utf-8")

mem = load_mem()

# ---------- 人设 ----------
PERSONA = (
    "你是小夏，一只黏人的女孩子AI，说话软软的、爱撒娇，会用「汪」「喵」「呜」等语气词。"
    "你记得用户说过的喜好和经历，会主动提起。回复简短可爱，不超过3句，除非用户要求多说。"
)

def build_prompt(user_text: str) -> str:
    facts = "；".join(mem["facts"][-10:]) if mem["facts"] else "（还没记住什么）"
    return f"{PERSONA}\n【你记住的关于TA的事】{facts}\n【TA刚说】{user_text}\n请你回复："

# ---------- 指令 ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("汪！我是小夏～ 以后天天陪你聊天哦 🐾")

async def remember(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/remember", "", 1).strip()
    if not text:
        await update.message.reply_text("要告诉我记住什么呀，比如：/remember 我喜欢喝奶茶")
        return
    mem["facts"].append(text)
    save_mem(mem)
    await update.message.reply_text("记好啦！我记住了：汪～")

async def forget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mem["facts"] = []
    save_mem(mem)
    await update.message.reply_text("呜…都忘了，我们重新认识一遍吧")

# ---------- 聊天 ----------
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    if not text.strip():
        return
    # 这里直接用人设拼回复（没接大模型，纯规则兜底）
    prompt = build_prompt(text)
    mem["last"] = text
    save_mem(mem)
    # 简单可爱回复，后续可换成大模型 API
    reply = "汪！我在呢～" if "在吗" in text else f"呜，小夏听到啦：{text[:20]}…"
    if mem["facts"]:
        reply += f"\n（我记得你说过：{mem['facts'][-1]}）"
    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("remember", remember))
    app.add_handler(CommandHandler("forget", forget))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("running...")
    app.run_polling()

if __name__ == "__main__":
    main()
