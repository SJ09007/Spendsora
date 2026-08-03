import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import User
from app.models.expense import Expense
from app.models.category import Category
from app.models.budget import Budget
from app.services.categorization_service import categorization_service
from app.services.budget_service import budget_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_by_telegram_id(db: Session, telegram_id: int) -> User:
    return db.query(User).filter(User.telegram_id == telegram_id).first()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        user = get_user_by_telegram_id(db, user_id)
        if user:
            welcome_text = (
                f"👋 <b>Welcome back, {user.full_name or 'Friend'}!</b>\n\n"
                f"I am your <b>ExpenseSense AI</b> Assistant.\n"
                f"Simply send me a message like <code>80 chai</code> or <code>1200 Amazon</code> to log expenses instantly!\n\n"
                f"Type /help to see all available commands."
            )
        else:
            welcome_text = (
                f"👋 <b>Welcome to ExpenseSense AI!</b>\n\n"
                f"To link your Telegram to your ExpenseSense account:\n"
                f"1. Login to your Web Dashboard\n"
                f"2. Go to Settings -> Link Telegram and generate a 6-digit code.\n"
                f"3. Send <code>/link &lt;6-digit-code&gt;</code> here!\n\n"
                f"Or simply start typing expenses directly, and I'll log them under a guest profile!"
            )
        await update.message.reply_html(welcome_text)
    finally:
        db.close()

async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args or len(context.args) == 0:
        await update.message.reply_html("⚠️ Please provide your 6-digit link code.\nExample: <code>/link 123456</code>")
        return

    code = context.args[0].strip()
    db = SessionLocal()
    try:
        user = db.query(User).filter(
            User.telegram_link_code == code,
            User.telegram_link_code_expires > datetime.utcnow()
        ).first()

        if not user:
            await update.message.reply_html("❌ Invalid or expired link code. Please generate a new code from the Web Dashboard.")
            return

        user.telegram_id = user_id
        user.telegram_link_code = None
        user.telegram_link_code_expires = None
        db.commit()

        await update.message.reply_html(f"🎉 <b>Success!</b> Your Telegram account has been linked to <b>{user.email}</b>!")
    finally:
        db.close()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 <b>ExpenseSense AI Bot Commands</b>\n\n"
        "💬 <b>Quick Log:</b> Simply send <code>80 chai</code> or <code>350 petrol</code>\n\n"
        "📜 <b>Commands:</b>\n"
        "/today - View today's total spending\n"
        "/week - View weekly spending summary\n"
        "/month - View monthly spending summary\n"
        "/analytics - Quick category & merchant breakdown\n"
        "/budget - Check budget status & limits\n"
        "/link &lt;code&gt; - Link your Web Account\n"
        "/help - Show this guide"
    )
    await update.message.reply_html(help_text)

async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        user = get_user_by_telegram_id(db, user_id)
        if not user:
            await update.message.reply_html("⚠️ Account not linked yet. Use /link <code> to link your account.")
            return

        now = datetime.utcnow()
        today_start = datetime(now.year, now.month, now.day)
        total = float(db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
            Expense.user_id == user.id, Expense.date >= today_start
        ).scalar())

        expenses = db.query(Expense).filter(Expense.user_id == user.id, Expense.date >= today_start).all()
        msg = f"📊 <b>Today's Spending:</b> {user.currency}{total:.2f}\n"
        msg += f"Total Transactions: {len(expenses)}\n\n"
        for e in expenses:
            cat_name = e.category.name if e.category else "Other"
            msg += f"• {user.currency}{float(e.amount):.2f} - {e.description} ({cat_name})\n"

        await update.message.reply_html(msg)
    finally:
        db.close()

async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    db = SessionLocal()
    try:
        user = get_user_by_telegram_id(db, user_id)
        if not user:
            # Create a guest user for immediate seamless Telegram usage if not linked
            user = db.query(User).filter(User.email == f"tg_{user_id}@expensesense.local").first()
            if not user:
                from app.core.security import get_password_hash
                user = User(
                    telegram_id=user_id,
                    email=f"tg_{user_id}@expensesense.local",
                    password_hash=get_password_hash("guest_password"),
                    full_name=update.effective_user.full_name or "Telegram User"
                )
                db.add(user)
                db.commit()
                db.refresh(user)

        # Parse expense using AI categorization service
        parsed = categorization_service.parse_and_categorize(text)
        if parsed["amount"] <= 0:
            await update.message.reply_html("💡 Could not detect expense amount. Please send in format: <code>80 chai</code>")
            return

        # Find category
        category = db.query(Category).filter(Category.name.ilike(parsed["category"])).first()
        category_id = category.id if category else None

        expense = Expense(
            user_id=user.id,
            category_id=category_id,
            amount=parsed["amount"],
            description=parsed["description"],
            merchant=parsed["merchant"],
            payment_mode=parsed["payment_mode"],
            raw_telegram_text=text,
            confidence_score=parsed["confidence_score"]
        )
        db.add(expense)
        db.commit()

        # Check budget alert
        alert = None
        if category_id:
            alert = budget_service.check_and_trigger_budget_alerts(db, user_id=user.id, category_id=category_id)

        card_reply = (
            f"✅ <b>Expense Added</b>\n\n"
            f"💰 <b>Amount:</b> {user.currency}{parsed['amount']:.2f}\n"
            f"📂 <b>Category:</b> {parsed['category']}\n"
            f"🏪 <b>Merchant:</b> {parsed['merchant'] or parsed['description']}\n"
            f"💳 <b>Mode:</b> {parsed['payment_mode']}\n"
            f"🎯 <b>Confidence:</b> {int(parsed['confidence_score'] * 100)}%"
        )
        if alert:
            card_reply += f"\n\n{alert}"

        await update.message.reply_html(card_reply)
    finally:
        db.close()

def build_telegram_application() -> Application:
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not provided in environment.")
        return None

    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("link", link_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))

    return app
