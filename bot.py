import subprocess
import os
import io
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8087047084:AAHPy5yOms06wcBIfbkLnQtSH0GVPptwG8g"
ADMIN_ID = 8585552975  # ваш ID

async def start(update, context):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Доступ запрещён.")
        return
    await update.message.reply_text("Бот активирован. Команды: /cmd, /screenshot, /processes, /kill, /upload, /shutdown")

async def cmd(update, context):
    if update.effective_user.id != ADMIN_ID: return
    command = ' '.join(context.args)
    if not command:
        await update.message.reply_text("Укажите команду, например /cmd ipconfig")
        return
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        if len(output) > 4096:
            output = output[:4000] + "\n... (обрезано)"
        await update.message.reply_text(f"```\n{output}\n```", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def screenshot(update, context):
    if update.effective_user.id != ADMIN_ID: return
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        bio = io.BytesIO()
        img.save(bio, format='PNG')
        bio.seek(0)
        await update.message.reply_photo(photo=bio, filename='screenshot.png')
    except Exception as e:
        await update.message.reply_text(f"Не удалось сделать скриншот: {e}")

async def processes(update, context):
    if update.effective_user.id != ADMIN_ID: return
    try:
        result = subprocess.run("tasklist", shell=True, capture_output=True, text=True)
        output = result.stdout
        if len(output) > 4096:
            output = output[:4000] + "\n... (обрезано)"
        await update.message.reply_text(f"```\n{output}\n```", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def kill(update, context):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("Укажите PID, например /kill 1234")
        return
    pid = context.args[0]
    try:
        subprocess.run(f"taskkill /PID {pid} /F", shell=True, check=True)
        await update.message.reply_text(f"Процесс {pid} завершён.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def upload(update, context):
    if update.effective_user.id != ADMIN_ID: return
    if not context.args:
        await update.message.reply_text("Укажите путь, например /upload C:\\file.txt")
        return
    path = ' '.join(context.args)
    if not os.path.exists(path):
        await update.message.reply_text("Файл не найден.")
        return
    try:
        with open(path, 'rb') as f:
            await update.message.reply_document(document=f, filename=os.path.basename(path))
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def handle_document(update, context):
    if update.effective_user.id != ADMIN_ID: return
    doc = update.message.document
    if not doc: return
    file = await doc.get_file()
    path = os.path.join(os.getcwd(), doc.file_name)
    await file.download_to_drive(path)
    await update.message.reply_text(f"Файл сохранён как {path}")

async def shutdown(update, context):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text("Выключаю ПК...")
    os.system("shutdown /s /t 1")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cmd", cmd))
    app.add_handler(CommandHandler("screenshot", screenshot))
    app.add_handler(CommandHandler("processes", processes))
    app.add_handler(CommandHandler("kill", kill))
    app.add_handler(CommandHandler("upload", upload))
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling()

if __name__ == "__main__":
    main()