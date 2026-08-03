import re
from typing import Dict, Any, Tuple, Optional
import google.generativeai as genai
from app.core.config import settings

# Keyword to category mapping matrix with system categories
CATEGORY_KEYWORDS: Dict[str, list] = {
    "Food": [
        "chai", "tea", "coffee", "starbucks", "cafe", "restaurant", "swiggy", "zomato",
        "dinner", "lunch", "breakfast", "snacks", "pizza", "burger", "mcdonalds",
        "dominos", "vegetables", "grocery", "groceries", "milk", "bread", "food",
        "biryani", "supermarket", "blinkit", "zepto", "instamart"
    ],
    "Transport": [
        "petrol", "diesel", "fuel", "uber", "ola", "rapido", "bus", "metro",
        "cab", "taxi", "train", "auto", "parking", "toll", "flight", "car wash"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "meesho", "clothes", "shoes", "mall",
        "zara", "h&m", "electronics", "gadgets", "laptop", "mobile", "shopping"
    ],
    "Subscriptions": [
        "netflix", "spotify", "prime", "hotstar", "youtube", "apple", "chatgpt",
        "subscription", "gym", "membership", "disney"
    ],
    "Entertainment": [
        "movie", "cinema", "bookmyshow", "concert", "game", "gaming", "steam",
        "pub", "bar", "party", "club"
    ],
    "Bills": [
        "electricity", "light bill", "water bill", "gas", "cylinder", "recharge",
        "wifi", "broadband", "jio", "airtel", "vi", "mobile bill", "maintenance"
    ],
    "Utilities": [
        "housework", "plumber", "electrician", "cleaning", "maid", "waste"
    ],
    "Healthcare": [
        "doctor", "hospital", "medicine", "pharmacy", "apollo", "pharmeasy",
        "clinic", "health", "dental", "lab test"
    ],
    "Education": [
        "books", "course", "udemy", "coursera", "school", "college", "tuition",
        "exam fee", "stationery"
    ],
    "Rent": [
        "rent", "house rent", "room rent", "pg rent", "flat rent"
    ],
    "Travel": [
        "hotel", "airbnb", "resort", "booking.com", "trip", "vacation", "make-my-trip",
        "goibibo", "flight ticket"
    ],
    "Investment": [
        "sip", "mutual fund", "stocks", "zerodha", "groww", "indmoney", "crypto",
        "fd", "savings", "gold"
    ],
    "Salary": [
        "salary", "stipend", "paycheck", "income", "freelance"
    ],
    "Miscellaneous": []
}

PAYMENT_MODES = {
    "cash": ["cash"],
    "upi": ["upi", "gpay", "googlepay", "phonepe", "paytm", "scan"],
    "card": ["card", "credit card", "debit card", "pos"],
    "netbanking": ["netbanking", "neft", "rtgs", "imps"]
}

class CategorizationService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception:
                self.gemini_model = None
        else:
            self.gemini_model = None

    def parse_and_categorize(self, text: str) -> Dict[str, Any]:
        """
        Parses raw input string (e.g., '80 chai', '₹350 petrol via UPI') and returns structured data.
        Returns:
            amount: float
            description: str
            merchant: Optional[str]
            category: str
            payment_mode: str
            confidence: float
        """
        clean_text = text.strip()
        
        # 1. Extract Amount using Regex
        # Matches patterns like: 80, 80.50, ₹80, Rs 80, 80rs, 80inr
        amount_match = re.search(r'(?:(?:₹|rs\.?|inr|\$)\s*)?(\d+(?:\.\d{1,2})?)(?:\s*(?:rs\.?|rupees|inr))?', clean_text, re.IGNORECASE)
        
        if not amount_match:
            # Fallback regex for floating amounts
            amount_match = re.search(r'(\d+\.\d{1,2}|\d+)', clean_text)

        amount = 0.0
        if amount_match:
            try:
                amount = float(amount_match.group(1))
            except ValueError:
                amount = 0.0

        # Remove the extracted amount phrase from text to leave description
        if amount_match:
            desc_text = clean_text.replace(amount_match.group(0), "").strip()
        else:
            desc_text = clean_text

        # Clean leading/trailing punctuation from description
        desc_text = re.sub(r'^[^\w\s]+|[^\w\s]+$', '', desc_text).strip()
        if not desc_text:
            desc_text = "Expense"

        # 2. Extract Payment Mode
        payment_mode = "UPI"  # Default
        for mode, keywords in PAYMENT_MODES.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', clean_text, re.IGNORECASE):
                    payment_mode = mode.upper()
                    # Clean payment mode out of description text if desired
                    desc_text = re.sub(r'\b' + re.escape(kw) + r'\b', '', desc_text, flags=re.IGNORECASE).strip()
                    break

        if not desc_text:
            desc_text = "Expense"

        # 3. Predict Category & Merchant using Keyword Matrix
        category, confidence = self._match_keywords(desc_text)
        merchant = self._extract_merchant(desc_text)

        # 4. If confidence is low and Gemini API is available, ask Gemini
        if confidence < 0.6 and self.gemini_model:
            gemini_cat, gemini_conf = self._categorize_with_gemini(desc_text)
            if gemini_cat:
                category = gemini_cat
                confidence = gemini_conf

        return {
            "amount": amount,
            "description": desc_text.capitalize(),
            "merchant": merchant,
            "category": category,
            "payment_mode": payment_mode,
            "confidence_score": round(confidence, 2),
            "raw_text": text
        }

    def _match_keywords(self, text: str) -> Tuple[str, float]:
        text_lower = text.lower()
        words = re.findall(r'\w+', text_lower)
        
        best_category = "Miscellaneous"
        highest_score = 0.0

        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    # Exact word match gets 0.95, substring match gets 0.8
                    score = 0.95 if any(w == kw for w in words) else 0.80
                    if score > highest_score:
                        highest_score = score
                        best_category = cat

        if highest_score == 0.0:
            return "Miscellaneous", 0.50

        return best_category, highest_score

    def _extract_merchant(self, text: str) -> Optional[str]:
        known_merchants = [
            "Amazon", "Flipkart", "Myntra", "Swiggy", "Zomato", "Uber", "Ola",
            "Netflix", "Spotify", "Starbucks", "McDonalds", "Dominos", "Blinkit",
            "Zepto", "Instamart", "BookMyShow", "Zerodha", "Groww", "Apollo"
        ]
        text_lower = text.lower()
        for m in known_merchants:
            if m.lower() in text_lower:
                return m
        return text.strip().title() if len(text.strip()) > 0 else None

    def _categorize_with_gemini(self, description: str) -> Tuple[Optional[str], float]:
        try:
            prompt = f"""Categorize this expense description into exactly one of the following categories:
Food, Entertainment, Transport, Shopping, Utilities, Healthcare, Education, Rent, Travel, Investment, Subscriptions, Salary, Bills, Miscellaneous.

Description: "{description}"

Respond in format: CATEGORY|CONFIDENCE
Example: Food|0.90
"""
            response = self.gemini_model.generate_content(prompt)
            result = response.text.strip()
            if "|" in result:
                cat, conf = result.split("|")
                return cat.strip(), float(conf.strip())
        except Exception:
            pass
        return None, 0.0

categorization_service = CategorizationService()
