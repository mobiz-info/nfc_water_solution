import datetime
import json
import re
from urllib.parse import unquote, urlencode
import requests
from django.http import JsonResponse
from django.db.models import F, Value, CharField, Q
from django.db.models.functions import Substr, Length, Cast

from accounts.models import CustomerComplaints, GuestCustomerOrder
from customer_care.models import DiffBottlesModel
from master.functions import get_custom_id
from product.models import ProdutItemMaster
from .models import EmirateMaster, LocationMaster, WhatsappData, WhatsappResponse, Customers

# ============================================================
# Dictionary of responses for different commands in all languages
# ============================================================
RESPONSES = {
    "LANGUAGE_SET": {
        "EN": "✅ Language set to English.",
        "AR": "✅ تم تغيير اللغة إلى العربية.",
        "HD": "✅ भाषा हिंदी में सेट की गई।",
        "UR": "✅ زبان اردو میں سیٹ کر دی گئی ہے۔",
        "BG": "✅ ভাষা বাংলা-তে সেট করা হয়েছে।",
        "MA": "✅ ഭാഷ മലയാളത്തിൽ സജ്ജമാക്കി.",
    },
    "ORDER_WATER": {
        "EN": "💧 To place an order, send: W <number of bottles>, Example: W 4",
        "AR": "💧 لعمل طلب، أرسل: W <عدد الزجاجات>",
        "HD": "💧 ऑर्डर देने के लिए भेजें: W <बोतलों की संख्या>",
        "UR": "💧 آرڈر دینے کے لیے بھیجیں: W <بوتلوں کی تعداد>",
        "BG": "💧 অর্ডার দিতে, পাঠান: W <বোতলের সংখ্যা>",
        "MA": "💧 ഓർഡർ നൽകാൻ അയയ്ക്കുക: W <ബോട്ടിലുകളുടെ എണ്ണം>",
    },
    "ORDER_STATUS": {
        "EN": "Order Status",
        "AR": "حالة الطلب",
        "HD": "ऑर्डर स्थिति",
        "UR": "آرڈر کی حیثیت",
        "BG": "অর্ডারের অবস্থা",
        "MA": "ഓർഡർ സ്റ്റാറ്റസ്",
    },
    "NOT_SCHEDULED": {
        "EN": "Not Scheduled",
        "AR": "غير مجدول",
        "HD": "अनुसूचित नहीं",
        "UR": "شیڈول نہیں ہوا",
        "BG": "সময়সূচী করা হয়নি",
        "MA": "ഷെഡ്യൂൾ ചെയ്തിട്ടില്ല",
    },
    "PENDING_CONFIRMATION": {
        "EN": "Pending Confirmation",
        "AR": "في انتظار التأكيد",
        "HD": "पुष्टि लंबित",
        "UR": "تصدیق زیر التواء",
        "BG": "নিশ্চিতকরণের অপেক্ষায়",
        "MA": "സ്ഥിരീകരണം ബാക്കി",
    },
    "NO_ORDER": {
        "EN": "⚠️ No orders found. Please place a new order.",
        "AR": "⚠️ لم يتم العثور على أي طلبات. يرجى تقديم طلب جديد.",
        "HD": "⚠️ कोई ऑर्डर नहीं मिला। कृपया नया ऑर्डर दें।",
        "UR": "⚠️ کوئی آرڈر نہیں ملا۔ براہ کرم نیا آرڈر دیں۔",
        "BG": "⚠️ কোনো অর্ডার পাওয়া যায়নি। অনুগ্রহ করে একটি নতুন অর্ডার দিন।",
        "MA": "⚠️ ഓർഡർ ഒന്നും കണ്ടെത്താനായില്ല. ദയവായി പുതിയ ഓർഡർ നൽകുക.",
    },
    "COMPLAINTS": {
        "EN": "📩 Your complaint has been registered. Our support team will contact you shortly.",
        "AR": "📩 تم تسجيل شكواك. سيتواصل معك فريق الدعم قريبًا.",
        "HD": "📩 आपकी शिकायत दर्ज कर ली गई है। हमारी सहायता टीम जल्द ही आपसे संपर्क करेगी।",
        "UR": "📩 آپ کی شکایت درج کر لی گئی ہے۔ ہماری ٹیم جلد ہی آپ سے رابطہ کرے گی۔",
        "BG": "📩 আপনার অভিযোগ নিবন্ধিত হয়েছে। আমাদের সাপোর্ট টিম দ্রুত যোগাযোগ করবে।",
        "MA": "📩 നിങ്ങളുടെ പരാതിയെ രജിസ്റ്റർ ചെയ്തിട്ടുണ്ട്. ഞങ്ങളുടെ സഹായസംഘം ഉടൻ തന്നെ ബന്ധപ്പെടും.",
    },
    "UNKNOWN": {
        "EN": "❌ Unknown command. Please try again.",
        "AR": "❌ أمر غير معروف. حاول مرة أخرى.",
        "HD": "❌ अज्ञात कमांड। कृपया पुनः प्रयास करें।",
        "UR": "❌ نامعلوم کمانڈ۔ دوبارہ کوشش کریں۔",
        "BG": "❌ অজানা কমান্ড। অনুগ্রহ করে আবার চেষ্টা করুন।",
        "MA": "❌ അറിയപ്പെടാത്ത കമാൻഡ്. ദയവായി വീണ്ടും ശ്രമിക്കുക.",
    }
}

# ============================================================
# Utility functions
# ============================================================
def get_effective_date(message_time=None):
    if message_time is None:
        message_time = datetime.datetime.now()
    cutoff_time = message_time.replace(hour=17, minute=0, second=0, microsecond=0)
    return (message_time + datetime.timedelta(days=1)).date() if message_time >= cutoff_time else message_time.date()

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002700-\U000027BF"  # dingbats
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U0001FA70-\U0001FAFF"  # symbols & pictographs extended-A
        "\U00002600-\U000026FF"  # misc symbols
        "\U00002B00-\U00002BFF"  # arrows, etc
        "\U0001F100-\U0001F1FF"  # enclosed alphanumerics (🅰, 🆕, etc.)
        "]+", 
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text).strip()

def send_whatsapp_simple(to_number, message):
    base_url = "http://wawy.org/conv_wa.php"
    params = {
        "username": "sanawater",
        "api_password": "3ef9egl7az1j7lah6",
        "sender": "97167408655",
        "to": to_number,
        "message": message
    }
    try:
        response = requests.get(f"{base_url}?{urlencode(params)}")
        return response.text if response.status_code == 200 else f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

def translate(key, lang):
    return RESPONSES.get(key, {}).get(lang, RESPONSES.get(key, {}).get("EN", key))

def send_interactive_whatsapp(to_number, lang="EN", customer_name=None):
    # Default to EN if unsupported
    lang = lang.upper()
    if lang not in ["EN", "AR", "MA", "HD", "UR", "BG"]:
        lang = "EN"

    MENU_TRANSLATIONS = {
        "EN": {
            "message": f"Dear {customer_name or ''}, Welcome to Demo Pure Drinking Water.\nChoose Options.",
            "header": "Welcome to Demo Water",
            "footer": "Select an option",
            "list_title": "Choose Service",
            "choices": {
                "order_water": "🧊 Order Water",
                "order_status": "📦 Check Order",
                "complaints": "📣 Complaints",
                "language": "🌐 Change Language"
            }
        },
        "MA": {  # Malayalam
            "message": f"പ്രിയപ്പെട്ട {customer_name or ''}, സന പ്യുവർ ഡ്രിങ്കിംഗ് വാട്ടറിലേക്ക് സ്വാഗതം.\nഓപ്ഷനുകൾ തിരഞ്ഞെടുക്കുക.",
            "header": "സന വാട്ടറിലേക്ക് സ്വാഗതം",
            "footer": "ഒരു ഓപ്ഷൻ തിരഞ്ഞെടുക്കുക",
            "list_title": "സർവീസ് തിരഞ്ഞെടുക്കുക",
            "choices": {
                "order_water": "🧊 വെള്ളം ഓർഡർ ചെയ്യുക",
                "order_status": "📦 ഓർഡർ സ്റ്റാറ്റസ്",
                "complaints": "📣 പരാതികൾ",
                "language": "🌐 ഇഷ്ടഭാഷ സജ്ജമാക്കുക"
            }
        },
        "AR": {
            "message": f"عزيزي {customer_name or ''}، مرحبًا بك في شركة سناء لمياه الشرب النقية. اختر الخيارات.",
            "header": "مرحبا بك في سناء",
            "footer": "اختر خيارًا",
            "list_title": "اختر الخدمة",
            "choices": {
                "order_water": "🧊 طلب مياه",
                "order_status": "📦 حالة الطلب",
                "complaints": "📣 الشكاوى",
                "language": "🌐 اختيار اللغة المفضلة"
            }
        },
        "HD": {
            "message": f"प्रिय {customer_name or ''}, सना प्योर ड्रिंकिंग वाटर में आपका स्वागत है। विकल्प चुनें।",
            "header": "सना वॉटर में आपका स्वागत है",
            "footer": "कोई विकल्प चुनें",
            "list_title": "सेवा चुनें",
            "choices": {
                "order_water": "🧊 पानी ऑर्डर करें",
                "order_status": "📦 ऑर्डर की स्थिति",
                "complaints": "📣 शिकायतें",
                "language": "🌐 पसंदीदा भाषा चुनें"
            }
        },
        "UR": {
            "message": f"پیارے {customer_name or ''}، ثنا خالص پینے کے پانی میں خوش آمدید۔ اختیارات کا انتخاب کریں۔",
            "header": "سناء واٹر میں خوش آمدید",
            "footer": "ایک آپشن منتخب کریں",
            "list_title": "سروس منتخب کریں",
            "choices": {
                "order_water": "🧊 پانی کا آرڈر دیں",
                "order_status": "📦 آرڈر کی حیثیت",
                "complaints": "📣 شکایات",
                "language": "🌐 ترجیحی زبان سیٹ کریں"
            }
        },
        "BG": {
            "message": f"প্রিয় {customer_name or ''}, সানা পিউর ড্রিংকিং ওয়াটারে স্বাগতম। বিকল্পগুলি চয়ন করুন।",
            "header": "সানা ওয়াটারে স্বাগতম",
            "footer": "একটি বিকল্প নির্বাচন করুন",
            "list_title": "সেবা নির্বাচন করুন",
            "choices": {
                "order_water": "🧊 পানি অর্ডার করুন",
                "order_status": "📦 অর্ডারের অবস্থা",
                "complaints": "📣 অভিযোগ",
                "language": "🌐 পছন্দের ভাষা নির্বাচন করুন"
            }
        }
    }

    t = MENU_TRANSLATIONS[lang]

    payload = {
        "username": "sanawater",
        "api_password": "3ef9egl7az1j7lah6",
        "sender": "97167408655",
        "interactive_type": "1",
        "data": [{
            "number": to_number,
            "message": t["message"],
            "header_message": t["header"],
            "footer_message": t["footer"],
            "interactive": {
                "list_title": t["list_title"],
                "sections": [
                    {
                        "title": "Order Services",
                        "choices": [
                            {"title": t["choices"]["order_water"], "choice_id": "order_water", "description": ""},
                            {"title": t["choices"]["order_status"], "choice_id": "order_status", "description": ""}
                        ]
                    },
                    {
                        "title": "Other Services",
                        "choices": [
                            {"title": t["choices"]["complaints"], "choice_id": "complaints", "description": ""},
                            {"title": t["choices"]["language"], "choice_id": "language", "description": ""}
                        ]
                    }
                ]
            }
        }]
    }

    response = requests.post("http://wawy.org/conv_wa.php", json=payload)
    print("API Response:", response.text)
    return response.text


def normalize_uae_number(number: str) -> str:
    # remove spaces, dashes, plus
    number = re.sub(r"[^\d]", "", number)

    # If starts with +971 → convert to 971
    if number.startswith("971") and len(number) == 12:
        return number

    # If starts with 0 → remove it and add 971
    if number.startswith("0") and len(number) == 10:
        return "971" + number[1:]

    # If already 9 digits (like 5XXXXXXXX)
    if len(number) == 9 and number.startswith("5"):
        return "971" + number

    # Already normalized
    if len(number) == 12 and number.startswith("971"):
        return number

    return number  # fallback (invalid or landline maybe)


# ============================================================
# 🚰 Main WhatsApp Handler
# ============================================================
def water_order_handler(request):
    number = request.GET.get('number', '')
    msg = unquote(request.GET.get('msg', '')).strip()
    clean_message = remove_emojis(msg).upper()
    
    normalized = normalize_uae_number(number)

    possible_formats = set([
        normalized,
        normalized.replace("971", "0", 1),  # 9715xxxx → 05xxxxxx
        normalized[3:],                    # remove 971
    ])
    
    # print(number)
    customer = None
    reply = None
    send_message = True

    # ===================== GET OR CREATE CUSTOMER =====================
    try:
        if Customers.objects.filter(whats_app__in=possible_formats,is_deleted=False).exists():
            customer = Customers.objects.filter(whats_app__in=possible_formats,is_deleted=False).latest("created_date")
        
        elif Customers.objects.filter(mobile_no__in=possible_formats,is_deleted=False).exists():
            customer = Customers.objects.filter(mobile_no__in=possible_formats,is_deleted=False).latest("created_date")
            customer.whats_app = number
            customer.save()
            
    except Customers.DoesNotExist:
        # Guest user not found → send registration instructions
        reply = (
            "💧 Welcome to Demo WATER!\n"
            "🙏 Thank you for choosing Demo WATER\n\n" 
            "We couldn’t find your number in our customer records.\n\n"
            "✅ If you are an existing customer, please reply with your registered mobile number.\n"
            "🆕 If you are a new customer, please reply with: New Customer"
            # "👋 Welcome to Demo Pure Drinking Water!\n\n"
            # "You are not registered in our system. Please share your details in this format:\n\n"
            # "NEW <Name>, <Building>, <House No>, <Floor>, <Location>, <Emirate>\n\n"
            # "Example:\nNEW John, Palm Tower, A-102, 10th, Marina, Dubai"
        )

    # ===================== SET LANGUAGE =====================
    lang = "EN"
    if customer and customer.preferred_language:
        lang = customer.preferred_language.upper()

    # ===================== LOG WHATSAPP MESSAGE =====================
    whatsapp_data = WhatsappData.objects.create(
        customer=None if not customer else customer,
        reciever_no=number,
        message=clean_message,
        created_by="system",
    )

    # ===================== LANGUAGE CHANGE =====================
    if customer and clean_message in ['AR', 'MA', 'HD', 'UR', 'BG', 'EN']:
        customer.preferred_language = clean_message
        customer.save()
        reply = translate("LANGUAGE_SET", clean_message)

    # ===================== GREETINGS =====================
    elif clean_message in ['HI', 'HELLO', 'HAI', 'CALL', 'SUPPORT', 'HABIBI']:
        if customer:
            send_interactive_whatsapp(to_number=number, lang=lang, customer_name=customer.customer_name)
            WhatsappResponse.objects.create(
                whatsapp_data=whatsapp_data,
                send_to=number,
                message="[Interactive List Sent]",
                created_by="system"
            )
            return JsonResponse({"message": "Interactive options sent."})
        else:
            print("else")
            reply = (
                "💧 Welcome to Demo WATER!\n"
                "🙏 Thank you for choosing Demo WATER\n\n"
                "We couldn’t find your number in our customer records.\n\n"
                "✅ If you are an existing customer, please reply with your registered mobile number.\n"
                "🆕 If you are a new customer, please reply with: New Customer"
                # "👋 Welcome to Demo Pure Drinking Water!\n\n"
                # "You are not registered in our system. Please share your details in this format:\n\n"
                # "NEW <Name>, <Building>, <House No>, <Floor>, <Location>, <Emirate>\n\n"
                # "Example:\nNEW John, Palm Tower, A-102, 10th, Marina, Dubai"
            )

    # ===================== ORDER WATER =====================
    elif customer and clean_message in ['ORDER WATER','വെള്ളം ഓർഡർ ചെയ്യുക','طلب مياه','पानी ऑर्डर करें','پانی کا آرڈر دیں','পানি অর্ডার করুন']:
        reply = translate("ORDER_WATER", lang)

    # ===================== ORDER STATUS =====================
    elif customer and clean_message in ['ORDER STATUS', 'ഓർഡർ സ്റ്റാറ്റസ്', 'حالة الطلب', 'ऑर्डर की स्थिति', 'آرڈر کی حیثیت', 'অর্ডারের অবস্থা']:
        if customer.is_guest:
            order = GuestCustomerOrder.objects.filter(customer=customer).order_by("-created_date").first()
            if order:
                reply = (
                    f"📦 {translate('ORDER_STATUS', lang)}\n\n"
                    f"👤 {customer.customer_name}\n"
                    f"🫙 {order.no_bottles_required}\n"
                    f"📅 {order.delivery_date.strftime('%d-%m-%Y') if order.delivery_date else translate('NOT_SCHEDULED', lang)}\n"
                    f"📌 {translate('PENDING_CONFIRMATION', lang)}"
                )
            else:
                reply = translate("NO_ORDER", lang)
        else:
            order = DiffBottlesModel.objects.filter(customer=customer).order_by("-created_date").first()
            if order:
                reply = (
                    f"📦 {translate('ORDER_STATUS', lang)}\n\n"
                    f"👤 {customer.customer_name}\n"
                    f"🫙 {order.quantity_required}\n"
                    f"📅 {order.delivery_date.strftime('%d-%m-%Y') if order.delivery_date else translate('NOT_SCHEDULED', lang)}\n"
                    f"📌 {order.status}"
                )
            else:
                reply = translate("NO_ORDER", lang)

    # ===================== COMPLAINTS =====================
    elif customer and re.match(r'^complaint\s+(.+)$', msg, re.IGNORECASE):
        complaint_text = re.match(r'^complaint\s+(.+)$', msg, re.IGNORECASE).group(1).strip()
        CustomerComplaints.objects.create(customer=customer, complaint=complaint_text)
        reply = translate("COMPLAINTS", lang)

    # ===================== CHANGE LANGUAGE =====================
    elif customer and clean_message in ['CHANGE LANGUAGE','ഇഷ്ടഭാഷ സജ്ജമാക്കുക','اختيار اللغة المفضلة','पसंदीदा भाषा चुनें','ترجیحی زبان سیٹ کریں','পছন্দের ভাষা নির্বাচন করুন']:
        reply = (
            "To set language send:\n"
            "AR - عربي\nMA - മലയാളം\nHD - हिंदी\nUR - اردو\nBG - বাঙালি\nEN - English"
        )

    # ===================== PLACE ORDER (W <number>) =====================
    elif customer and (match := re.match(r'^W\s*(\d+)$', clean_message)):
        bottle_count = match.group(1)
        if customer.is_guest:
            GuestCustomerOrder.objects.create(
                customer=customer,
                product=ProdutItemMaster.objects.get(product_name="5 Gallon"),
                no_bottles_required=bottle_count,
                delivery_date=get_effective_date(),
            )
            reply = f"✅ Your request for {bottle_count} bottle(s) has been received.\n💧 Our team will contact you shortly to confirm your details."
        else:
            data = DiffBottlesModel.objects.create(
                customer=customer,
                product_item=ProdutItemMaster.objects.get(product_name="5 Gallon"),
                quantity_required=bottle_count,
                delivery_date=get_effective_date(),
                assign_this_to=customer.sales_staff,
                mode="paid",
            )
            translations = {
                "EN": "✅ Order received for {bottle_count} bottles.\n📅 Delivery: {delivery_date}\n💧 Thank you!",
                "AR": "✅ تم استلام طلب {bottle_count} زجاجة.\n📅 التسليم: {delivery_date}\n💧 شكرًا لك!",
                "HD": "✅ {bottle_count} बोतलों का ऑर्डर मिला।\n📅 डिलीवरी: {delivery_date}\n💧 धन्यवाद!",
                "UR": "✅ {bottle_count} بوتلوں کا آرڈر موصول ہوا۔\n📅 ترسیل کی تاریخ: {delivery_date}\n💧 شکریہ!",
                "BG": "✅ {bottle_count} বোতলের অর্ডার গৃহীত হয়েছে।\n📅 ডেলিভারি: {delivery_date}\n💧 ধন্যবাদ!",
                "MA": "✅ {bottle_count} ബോട്ടിലുകളുടെ ഓർഡർ ലഭിച്ചു.\n📅 ഡെലിവറി: {delivery_date}\n💧 നന്ദി!",
            }
            t = translations.get(lang, translations["EN"])
            reply = t.format(bottle_count=bottle_count, delivery_date=data.delivery_date.strftime("%d-%m-%Y"))

    # ===================== REGISTER NEW CUSTOMER =====================
    elif not customer and clean_message.startswith("NEW CUSTOMER"):
        # Ask for details in new format
        reply = (
            "🎉 Thank you for choosing Demo WATER!\n"
            "We’re excited to serve you 💙 Please share your details below:\n\n"
            "👤 Name -\n"
            "📱 Mobile Number -\n"
            "🏠 Building Name / Villa No -\n"
            "🚪 Apartment Number -\n"
            "📍 Area -\n"
            "🕌 Emirate -\n\n"
            "📌 Also, kindly share your location 🗺️ for faster delivery."
        )
        
    elif not customer and ("NAME -" in msg.upper() and "MOBILE" in msg.upper() and "EMIRATE" in msg.upper()):
        try:
            # Simple line-by-line parsing
            details = {}
            for line in msg.splitlines():
                if "-" in line:
                    key, val = line.split("-", 1)
                    details[key.strip()] = val.strip()

            customer = Customers.objects.create(
                custom_id = get_custom_id(Customers),
                customer_name = details.get("👤 Name", ""),
                building_name = details.get("🏠 Building Name / Villa No", ""),
                door_house_no = details.get("🚪 Apartment Number", ""),
                floor_no = "",  # not in new form, keep blank
                location = LocationMaster.objects.get(location_name__iexact=details.get("📍 Area", "")),
                emirate = EmirateMaster.objects.get(name__iexact=details.get("🕌 Emirate", "")),
                mobile_no = details.get("📱 Mobile Number", number),
                whats_app = number,
                is_guest = True
            )
            customer.visit_schedule = {
                "Friday": [""],
                "Monday": [""],
                "Sunday": [""],
                "Tuesday": [""],
                "Saturday": [""],
                "Thursday": [""],
                "Wednesday": [""]
            }
            # Save the updated customer
            customer.save()

            reply = f"✅ Welcome {customer.customer_name}! You are now registered as a guest.\nOur team will verify your details. Once approved, you can place regular orders."
            
            send_interactive_whatsapp(to_number=number, lang=lang, customer_name=customer.customer_name)
            send_whatsapp_simple(number, reply)
            send_message = False
            
        except Exception as e:
            reply = f"⚠️ Invalid details format. Please try again.\n\n{str(e)}"
            
    
    elif customer and "LOCATION" in clean_message:
        try:
            # Parse incoming JSON body
            data = json.loads(request.body.decode('utf-8'))
            location_data = data.get("location", {})

            latitude = location_data.get("latitude")
            longitude = location_data.get("longitude")
            loc_name = location_data.get("name", "")
            loc_address = location_data.get("address", "")

            if latitude and longitude:
                if customer:
                    # Save location into customer profile
                    customer.gps_latitude = latitude
                    customer.gps_longitude = longitude
                    customer.save()
                    
                    reply = (
                        f"✅ Your location has been saved successfully!\n"
                        f"📍 {loc_name or 'Shared Location'}\n"
                        f"🌐 {latitude}, {longitude}"
                    )
                else:
                    reply = "⚠️ Please register first using 'New Customer' before sharing location."
            else:
                reply = "⚠️ Could not read location. Please try sharing your live location again."

        except Exception as e:
            reply = f"⚠️ Error while saving location: {str(e)}"

    # elif not customer and clean_message.startswith("NEW"):
    #     details = msg[4:].strip()
    #     pattern = r'^([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*(.+)$'
    #     match = re.match(pattern, details, re.IGNORECASE)
    #     if match:
    #         name, building, house_no, floor, location, emirate = match.groups()
    #         customer = Customers.objects.create(
    #             customer_name = name.strip(),
    #             building_name = building.strip(),
    #             door_house_no = house_no.strip(),
    #             floor_no = floor.strip(),
    #             location = LocationMaster.objects.get(location_name__iexact=location.strip()),
    #             emirate = EmirateMaster.objects.get(name__iexact=emirate.strip()),
    #             mobile_no = number,
    #             whats_app = number,
    #             is_guest = True
    #         )
    #         reply = f"✅ Welcome {customer.customer_name}! You are now registered as a guest.\nOur team will verify your details. Once approved, you can place regular orders."
            
    #         send_interactive_whatsapp(to_number=number, lang=lang, customer_name=customer.customer_name)
            
    #     else:
    #         reply = "⚠️ Invalid format.\nExample:\nNEW John, Palm Tower, A-102, 10th, Marina, Dubai"

    # ===================== UNKNOWN COMMAND =====================
    else:
        reply = translate("UNKNOWN", lang)

    # ===================== SAVE RESPONSE & SEND =====================
    # print(reply)
    # print(remove_emojis(reply))
    WhatsappResponse.objects.create(
        whatsapp_data=whatsapp_data,
        send_to=number,
        message=remove_emojis(reply),
        created_by="system"
    )
    if send_message :
        send_whatsapp_simple(number, reply)

    return JsonResponse({"message": reply})