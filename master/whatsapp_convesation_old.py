import datetime
import re
from urllib.parse import unquote, urlencode
import requests
from django.http import JsonResponse

from accounts.models import CustomerComplaints, GuestCustomerOrder
from customer_care.models import DiffBottlesModel
from master.functions import get_custom_id
from product.models import ProdutItemMaster
from .models import EmirateMaster, LocationMaster, WhatsappData, WhatsappResponse, Customers

# ============================================================
# Dictionary of responses for different commands in all languages
# ============================================================
RESPONSES = {
    "ORDER_WATER": {
        "EN": "How Many Bottles? Reply: W <number>\nExample: W 4",
        "AR": "كم عدد الزجاجات؟ أرسل: W <العدد>\nمثال: W 4",
        "HD": "कितनी बोतलें चाहिए? जवाब दें: W <संख्या>\nउदाहरण: W 4",
        "UR": "کتنی بوتلیں چاہئیں؟ جواب دیں: W <تعداد>\nمثال: W 4",
        "BG": "কত বোতল লাগবে? উত্তর দিন: W <সংখ্যা>\nউদাহরণ: W 4",
        "MA": "എത്ര ബോട്ടിലുകൾ വേണം? മറുപടി: W <എണ്ണം>\nഉദാഹരണം: W 4",
    },
    "ORDER_STATUS": {
        "EN": "🔎 Fetching your order status...",
        "AR": "🔎 يتم جلب حالة طلبك...",
        "HD": "🔎 आपके ऑर्डर की स्थिति प्राप्त की जा रही है...",
        "UR": "🔎 آپ کے آرڈر کی حیثیت حاصل کی جا رہی ہے...",
        "BG": "🔎 আপনার অর্ডারের অবস্থা আনা হচ্ছে...",
        "MA": "🔎 നിങ്ങളുടെ ഓർഡർ സ്റ്റാറ്റസ് കൊണ്ടുവരുന്നു...",
    },
    "COMPLAINTS": {
        "EN": "📩 Please type your complaint in this format:\ncomplaint your message",
        "AR": "📩 الرجاء كتابة الشكوى بهذا التنسيق:\ncomplaint رسالتك",
        "HD": "📩 कृपया इस प्रारूप में अपनी शिकायत लिखें:\ncomplaint आपका संदेश",
        "UR": "📩 براہ کرم اپنی شکایت اس فارمیٹ میں لکھیں:\ncomplaint آپ کا پیغام",
        "BG": "📩 দয়া করে এই ফর্ম্যাটে আপনার অভিযোগ লিখুন:\ncomplaint আপনার বার্তা",
        "MA": "📩 നിങ്ങളുടെ പരാതി ഈ ഫോർമാറ്റിൽ ടൈപ്പ് ചെയ്യുക:\ncomplaint നിങ്ങളുടെ സന്ദേശം",
    },
    "LANGUAGE_SET": {
        "AR": "تم ضبط اللغة المفضلة للتواصل على اللغة العربية.",
        "MA": "നിങ്ങളുടെ ആശയവിനിമയത്തിനുള്ള ഇഷ്ടഭാഷ മലയാളം ആയി സജ്ജീകരിച്ചിട്ടുണ്ട്.",
        "HD": "आपकी पसंदीदा संवाद भाषा हिंदी निर्धारित की गई है।",
        "UR": "آپ کی پسندیدہ مواصلاتی زبان اردو مقرر کی گئی ہے।",
        "BG": "আপনার পছন্দের যোগাযোগের ভাষা বাংলায় নির্ধারণ করা হয়েছে।",
        "EN": "Your preferred language has been set to English."
    },
    "UNKNOWN": {
        "EN": "❓ Sorry, I didn’t understand. Please try again.",
        "AR": "❓ عذراً، لم أفهم. حاول مرة أخرى.",
        "HD": "❓ क्षमा करें, मैं समझ नहीं पाया। कृपया पुनः प्रयास करें।",
        "UR": "❓ معاف کریں، میں سمجھ نہیں سکا۔ دوبارہ کوشش کریں۔",
        "BG": "❓ দুঃখিত, আমি বুঝতে পারিনি। আবার চেষ্টা করুন।",
        "MA": "❓ ക്ഷമിക്കണം, എനിക്ക് മനസ്സിലായില്ല. ദയവായി വീണ്ടും ശ്രമിക്കുക.",
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
        "[" "\U0001F600-\U0001F64F" "\U0001F300-\U0001F5FF" "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF" "\U00002700-\U000027BF" "\U0001F900-\U0001F9FF"
        "\U00002600-\U000026FF" "\U00002B00-\U00002BFF" "]+", flags=re.UNICODE
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


# ============================================================
# 🚰 Main WhatsApp Handler
# ============================================================
# def water_order_handler(request):
#     number = request.GET.get('number', '')
#     msg = unquote(request.GET.get('msg', '')).strip()
#     clean_message = remove_emojis(msg).upper()

#     # Get or create customer
#     try:
#         customer = Customers.objects.filter(whats_app=number, is_deleted=False).latest("created_date")
#     except Customers.DoesNotExist:
#         customer = Customers.objects.create(
#             customer_name=f"Guest-{number}",
#             whats_app=number,
#             mobile_no=number,
#             created_by="system",
#             is_guest=True,
#             custom_id=get_custom_id(Customers)
#         )

#     whatsapp_data = WhatsappData.objects.create(
#         customer=None if customer.is_guest else customer,
#         reciever_no=number,
#         message=clean_message,
#         created_by="system"
#     )

#     # Use stored language or default to EN
#     lang = customer.preferred_language or "EN"

#     # ============= LANGUAGE CHANGE =============
#     if clean_message in ['AR', 'MA', 'HD', 'UR', 'BG', 'EN']:
#         customer.preferred_language = clean_message
#         customer.save()
#         reply = RESPONSES["LANGUAGE_SET"].get(clean_message, RESPONSES["LANGUAGE_SET"]["EN"])

#     # ============= GREETINGS =============
#     elif clean_message in ['HI', 'HELLO', 'HAI', 'CALL', 'SUPPORT', 'HABIBI']:
#         send_interactive_whatsapp(to_number=number)
        
        
        
#         WhatsappResponse.objects.create(
#             whatsapp_data=whatsapp_data,
#             send_to=number,
#             message="[Interactive List Sent]",
#             created_by="system"
#         )
#         return JsonResponse({"message": "Interactive options sent."})

#     # ============= MAIN COMMANDS =============
#     elif clean_message == 'ORDER WATER':
#         reply = RESPONSES["ORDER_WATER"].get(lang, RESPONSES["ORDER_WATER"]["EN"])

#     elif clean_message == 'ORDER STATUS':
#         reply = RESPONSES["ORDER_STATUS"].get(lang, RESPONSES["ORDER_STATUS"]["EN"])

#     elif clean_message == 'COMPLAINTS':
#         reply = RESPONSES["COMPLAINTS"].get(lang, RESPONSES["COMPLAINTS"]["EN"])

#     elif clean_message == 'CHANGE LANGUAGE':
#         reply = "To set language send:\nAR - Arabic\nMA - Malayalam\nHD - Hindi\nUR - Urdu\nBG - Bangla\nEN - English"

#     # ============= PLACE ORDER (W 4) =============
#     elif match := re.match(r'^W\s*(\d+)$', clean_message):
#         bottle_count = match.group(1)

#         if not customer.is_guest:
#             data = DiffBottlesModel.objects.create(
#                 customer=customer,
#                 product_item=ProdutItemMaster.objects.get(product_name="5 Gallon"),
#                 quantity_required=bottle_count,
#                 delivery_date=get_effective_date(),
#                 assign_this_to=customer.sales_staff,
#                 mode="paid",
#             )
#         else:
#             data = GuestCustomerOrder.objects.create(
#                 customer=customer,
#                 product=ProdutItemMaster.objects.get(product_name="5 Gallon"),
#                 no_bottles_required=bottle_count,
#                 delivery_date=get_effective_date(),
#             )

#         # ✅ Define translations for multiple languages
#         translations = {
#             "EN": {
#                 "order_received": "✅ Order received for {bottle_count} bottle(s).",
#                 "delivery_date": "📅 Delivery Date: {delivery_date}",
#                 "location": "🏠 Location: {location}",
#                 "sales_staff": "👨‍💼 Sales Staff: {sales_staff}",
#                 "thanks": "💧 Thank you for your order! Our team will contact you if needed."
#             },
#             "AR": {
#                 "order_received": "✅ تم استلام طلب {bottle_count} زجاجة.",
#                 "delivery_date": "📅 تاريخ التسليم: {delivery_date}",
#                 "location": "🏠 الموقع: {location}",
#                 "sales_staff": "👨‍💼 موظف المبيعات: {sales_staff}",
#                 "thanks": "💧 شكرًا لطلبك! سيتواصل معك فريقنا إذا لزم الأمر."
#             },
#             "HD": {
#                 "order_received": "✅ {bottle_count} बोतलों का ऑर्डर प्राप्त हुआ।",
#                 "delivery_date": "📅 डिलीवरी की तारीख: {delivery_date}",
#                 "location": "🏠 स्थान: {location}",
#                 "sales_staff": "👨‍💼 बिक्री कर्मचारी: {sales_staff}",
#                 "thanks": "💧 आपके ऑर्डर के लिए धन्यवाद! आवश्यकता होने पर हमारी टीम आपसे संपर्क करेगी।"
#             },
#             "UR": {
#                 "order_received": "✅ {bottle_count} بوتلوں کا آرڈر موصول ہوگیا ہے۔",
#                 "delivery_date": "📅 ترسیل کی تاریخ: {delivery_date}",
#                 "location": "🏠 مقام: {location}",
#                 "sales_staff": "👨‍💼 سیلز اسٹاف: {sales_staff}",
#                 "thanks": "💧 آپ کے آرڈر کا شکریہ! ضرورت پڑنے پر ہماری ٹیم آپ سے رابطہ کرے گی۔"
#             },
#             "BN": {
#                 "order_received": "✅ {bottle_count} বোতলের অর্ডার গ্রহণ করা হয়েছে।",
#                 "delivery_date": "📅 ডেলিভারি তারিখ: {delivery_date}",
#                 "location": "🏠 অবস্থান: {location}",
#                 "sales_staff": "👨‍💼 বিক্রয় কর্মী: {sales_staff}",
#                 "thanks": "💧 আপনার অর্ডারের জন্য ধন্যবাদ! প্রয়োজনে আমাদের দল আপনার সাথে যোগাযোগ করবে।"
#             },
#             "ML": {
#                 "order_received": "✅ {bottle_count} ബോട്ടിലുകളുടെ ഓർഡർ സ്വീകരിച്ചു.",
#                 "delivery_date": "📅 ഡെലിവറി തീയതി: {delivery_date}",
#                 "location": "🏠 സ്ഥലം: {location}",
#                 "sales_staff": "👨‍💼 സെയിൽസ് സ്റ്റാഫ്: {sales_staff}",
#                 "thanks": "💧 ഓർഡറിനുവേണ്ടി നന്ദി! ആവശ്യമെങ്കിൽ ഞങ്ങളുടെ ടീം ബന്ധപ്പെടും."
#             }
#         }

#         # ✅ Pick customer language (default English)
#         lang = getattr(customer, "preferred_language", "EN").upper()
#         t = translations.get(lang, translations["EN"])

#         reply = (
#             f"{t['order_received'].format(bottle_count=bottle_count)}\n"
#             f"{t['delivery_date'].format(delivery_date=data.delivery_date.strftime('%d-%m-%Y'))}\n"
#             f"{t['location'].format(location=customer.location.location_name)}\n"
#             f"{t['sales_staff'].format(sales_staff=customer.sales_staff.get_fullname() if customer.sales_staff else 'Not Assigned')}\n\n"
#             f"{t['thanks']}"
#         )


#     # ============= REGISTER NEW CUSTOMER =============
#     elif clean_message.startswith("NEW"):
#         details = msg[4:].strip()
#         pattern = r'^([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*(.+)$'
#         match = re.match(pattern, details, re.IGNORECASE)
#         if match:
#             name, building, house_no, floor, location, emirate = match.groups()
#             customer.customer_name = name.strip()
#             customer.building_name = building.strip()
#             customer.door_house_no = house_no.strip()
#             customer.floor_no = floor.strip()
#             customer.location = LocationMaster.objects.get(location_name__exact=location.strip())
#             customer.emirate = EmirateMaster.objects.get(name__exact=emirate.strip())
#             customer.is_guest = False
#             customer.save()
#             reply = f"✅ Welcome {customer.customer_name}! You are now registered.\nSend ORDER WATER to place an order."
#         else:
#             reply = "⚠️ Invalid format. Example:\nNEW John, Palm Tower, A-102, 10th, Marina, Dubai"

#     # ============= COMPLAINT HANDLING =============
#     elif match := re.match(r'^complaint\s+(.+)$', msg, re.IGNORECASE):
#         complaint_text = match.group(1).strip()
        
#         CustomerComplaints.objects.create(
#             customer=customer,
#             complaint=complaint_text,
#         )
        
#         # TODO: Save complaint_text in DB if needed
#         replies = {
#             "en": "📩 Your complaint has been registered. Our support team will contact you shortly.",
#             "hd": "📩 आपकी शिकायत दर्ज कर ली गई है। हमारी सहायता टीम जल्द ही आपसे संपर्क करेगी।",
#             "ml": "📩 നിങ്ങളുടെ പരാതിയെ രജിസ്റ്റർ ചെയ്തിട്ടുണ്ട്. ഞങ്ങളുടെ സഹായസംഘം ഉടൻ തന്നെ നിങ്ങളുമായി ബന്ധപ്പെടും.",
#             "ar": "📩 تم تسجيل شكواك. سيتواصل معك فريق الدعم قريبًا.",
#             "ta": "📩 உங்கள் புகார் பதிவு செய்யப்பட்டுள்ளது. எங்கள் ஆதரவு குழு விரைவில் உங்களை தொடர்புகொள்ளும்.",
#         }
        
#         reply = replies.get(customer.preferred_language, replies["en"]) 

#     else:
#         reply = RESPONSES["UNKNOWN"].get(lang, RESPONSES["UNKNOWN"]["EN"])

#     # Save reply
#     WhatsappResponse.objects.create(
#         whatsapp_data=whatsapp_data,
#         send_to=number,
#         message=remove_emojis(reply),
#         created_by="system"
#     )
#     send_whatsapp_simple(number, reply)
#     return JsonResponse({"message": reply})


def water_order_handler(request):
    number = request.GET.get('number', '')
    msg = unquote(request.GET.get('msg', '')).strip()
    clean_message = remove_emojis(msg).upper()

    # ======================================================
    # Get or create customer
    # ======================================================
    try:
        customer = Customers.objects.filter(
            whats_app=number, is_deleted=False
        ).latest("created_date")
    except Customers.DoesNotExist:
        # customer = Customers.objects.create(
        #     customer_name=f"Guest-{number}",
        #     whats_app=number,
        #     mobile_no=number,
        #     created_by="system",
        #     is_guest=True,
        #     custom_id=get_custom_id(Customers)
        # )
        reply = (
                "👋 Welcome to Demo Pure Drinking Water!\n\n"
                "You are not registered in our system. Please share your details in this format:\n\n"
                "NEW <Name>, <Building>, <House No>, <Floor>, <Location>, <Emirate>\n\n"
                "Example:\nNEW John, Palm Tower, A-102, 10th, Marina, Dubai"
            )
        
    if customer:
        whatsapp_data = WhatsappData.objects.create(
            customer=None if customer.is_guest else customer,
            reciever_no=number,
            message=clean_message,
            created_by="system"
        )

    # ======================================================
    # Pick language (default English)
    # ======================================================
    lang = (customer.preferred_language or "EN").upper()

    # ======================================================
    # LANGUAGE CHANGE
    # ======================================================
    if clean_message in ['AR', 'MA', 'HD', 'UR', 'BG', 'EN']:
        customer.preferred_language = clean_message
        customer.save()
        reply = RESPONSES["LANGUAGE_SET"].get(clean_message, RESPONSES["LANGUAGE_SET"]["EN"])

    # ======================================================
    # GREETINGS
    # ======================================================
    elif clean_message in ['HI', 'HELLO', 'HAI', 'CALL', 'SUPPORT', 'HABIBI']:

        if not customer.is_guest:
            # ✅ Registered customer → interactive menu
            send_interactive_whatsapp(
                to_number=number,
                lang=lang,
                customer_name=customer.customer_name
            )
            WhatsappResponse.objects.create(
                whatsapp_data=whatsapp_data,
                send_to=number,
                message="[Interactive List Sent]",
                created_by="system"
            )
            return JsonResponse({"message": "Interactive options sent."})
        else:
            # ✅ Guest → ask for details
            reply = (
                "👋 Welcome to Demo Pure Drinking Water!\n\n"
                "You are not registered in our system. Please share your details in this format:\n\n"
                "NEW <Name>, <Building>, <House No>, <Floor>, <Location>, <Emirate>\n\n"
                "Example:\nNEW John, Palm Tower, A-102, 10th, Marina, Dubai"
            )

    # ======================================================
    # MAIN COMMANDS
    # ======================================================
    elif clean_message in ['ORDER WATER','വെള്ളം ഓർഡർ ചെയ്യുക','طلب مياه','पानी ऑर्डर करें','پانی کا آرڈر دیں','পানি অর্ডার করুন'] :
        reply = RESPONSES["ORDER_WATER"].get(lang, RESPONSES["ORDER_WATER"]["EN"])

    elif clean_message in ['ORDER STATUS', 'ഓർഡർ സ്റ്റാറ്റസ്', 'حالة الطلب', 'ऑर्डर की स्थिति', 'آرڈر کی حیثیت', 'অর্ডারের অবস্থা']:

        if customer.is_guest:
            order = GuestCustomerOrder.objects.filter(customer=customer).order_by("-created_date").first()
            if order:
                translations = {
                    "EN": (
                        "📦 Order Status\n\n"
                        "👤 Customer: {name}\n"
                        "🫙 Bottles: {bottles}\n"
                        "📅 Delivery Date: {date}\n"
                        "📌 Status: Pending Confirmation"
                    ),
                    "AR": (
                        "📦 حالة الطلب\n\n"
                        "👤 العميل: {name}\n"
                        "🫙 الزجاجات: {bottles}\n"
                        "📅 تاريخ التسليم: {date}\n"
                        "📌 الحالة: في انتظار التأكيد"
                    ),
                    "HD": (
                        "📦 ऑर्डर स्थिति\n\n"
                        "👤 ग्राहक: {name}\n"
                        "🫙 बोतलें: {bottles}\n"
                        "📅 डिलीवरी तिथि: {date}\n"
                        "📌 स्थिति: पुष्टि लंबित"
                    ),
                    "UR": (
                        "📦 آرڈر کی حیثیت\n\n"
                        "👤 کسٹمر: {name}\n"
                        "🫙 بوتلیں: {bottles}\n"
                        "📅 ترسیل کی تاریخ: {date}\n"
                        "📌 حیثیت: تصدیق کا انتظار"
                    ),
                    "BG": (
                        "📦 অর্ডারের অবস্থা\n\n"
                        "👤 গ্রাহক: {name}\n"
                        "🫙 বোতল: {bottles}\n"
                        "📅 ডেলিভারি তারিখ: {date}\n"
                        "📌 অবস্থা: নিশ্চিতকরণের অপেক্ষায়"
                    ),
                    "MA": (
                        "📦 ഓർഡർ സ്റ്റാറ്റസ്\n\n"
                        "👤 ഉപഭോക്താവ്: {name}\n"
                        "🫙 ബോട്ടിലുകൾ: {bottles}\n"
                        "📅 ഡെലിവറി തീയതി: {date}\n"
                        "📌 നില: സ്ഥിരീകരണം ബാക്കി"
                    ),
                }
                t = translations.get(lang, translations["EN"])
                reply = t.format(
                    name=customer.customer_name,
                    bottles=order.no_bottles_required,
                    date=order.delivery_date.strftime("%d-%m-%Y") if order.delivery_date else "Not Scheduled"
                )
            else:
                reply = RESPONSES["NO_ORDER"].get(lang, RESPONSES["NO_ORDER"]["EN"])

        else:
            order = DiffBottlesModel.objects.filter(customer=customer).order_by("-created_date").first()
            if order:
                translations = {
                    "EN": (
                        "📦 Order Status\n\n"
                        "👤 Customer: {name}\n"
                        "🫙 Bottles: {bottles}\n"
                        "📅 Delivery Date: {date}\n"
                        "📌 Status: {status}"
                    ),
                    "AR": (
                        "📦 حالة الطلب\n\n"
                        "👤 العميل: {name}\n"
                        "🫙 الزجاجات: {bottles}\n"
                        "📅 تاريخ التسليم: {date}\n"
                        "📌 الحالة: {status}"
                    ),
                    "HD": (
                        "📦 ऑर्डर स्थिति\n\n"
                        "👤 ग्राहक: {name}\n"
                        "🫙 बोतलें: {bottles}\n"
                        "📅 डिलीवरी तिथि: {date}\n"
                        "📌 स्थिति: {status}"
                    ),
                    "UR": (
                        "📦 آرڈر کی حیثیت\n\n"
                        "👤 کسٹمر: {name}\n"
                        "🫙 بوتلیں: {bottles}\n"
                        "📅 ترسیل کی تاریخ: {date}\n"
                        "📌 حیثیت: {status}"
                    ),
                    "BG": (
                        "📦 অর্ডারের অবস্থা\n\n"
                        "👤 গ্রাহক: {name}\n"
                        "🫙 বোতল: {bottles}\n"
                        "📅 ডেলিভারি তারিখ: {date}\n"
                        "📌 অবস্থা: {status}"
                    ),
                    "MA": (
                        "📦 ഓർഡർ സ്റ്റാറ്റസ്\n\n"
                        "👤 ഉപഭോക്താവ്: {name}\n"
                        "🫙 ബോട്ടിലുകൾ: {bottles}\n"
                        "📅 ഡെലിവറി തീയതി: {date}\n"
                        "📌 നില: {status}"
                    ),
                }
                t = translations.get(lang, translations["EN"])
                reply = t.format(
                    name=customer.customer_name,
                    bottles=order.quantity_required,
                    date=order.delivery_date.strftime("%d-%m-%Y") if order.delivery_date else "Not Scheduled",
                    status=order.status
                )
            else:
                reply = RESPONSES["NO_ORDER"].get(lang, RESPONSES["NO_ORDER"]["EN"])

    elif clean_message in ['COMPLAINTS','പരാതികൾ','الشكاوى','शिकायतें','شکایات','অভিযোগ']:
        reply = RESPONSES["COMPLAINTS"].get(lang, RESPONSES["COMPLAINTS"]["EN"])

    elif clean_message in ['CHANGE LANGUAGE','ഇഷ്ടഭാഷ സജ്ജമാക്കുക','اختيار اللغة المفضلة','पसंदीदा भाषा चुनें','ترجیحی زبان سیٹ کریں','পছন্দের ভাষা নির্বাচন করুন']:
        reply = (
            "To set language send:\n"
            "AR - عربي\nMA - മലയാളം\nHD - हिंदी\nUR - اردو\nBG - बांग्ला\nEN - English"
        )

    # ======================================================
    # PLACE ORDER (W 4)
    # ======================================================
    elif match := re.match(r'^W\s*(\d+)$', clean_message):
        bottle_count = match.group(1)

        if customer.is_guest:
            # Guest order → save minimal
            GuestCustomerOrder.objects.create(
                customer=customer,
                product=ProdutItemMaster.objects.get(product_name="5 Gallon"),
                no_bottles_required=bottle_count,
                delivery_date=get_effective_date(),
            )
            reply = (
                f"✅ Your request for {bottle_count} bottle(s) has been received.\n"
                "💧 Our team will contact you shortly to confirm your details."
            )

        else:
            # Registered customer order
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
                "UR": "✅ {bottle_count} بوتلوں کا آرڈر موصول ہوا۔\n📅 ترسیل: {delivery_date}\n💧 شکریہ!",
                "BG": "✅ {bottle_count} বোতলের অর্ডার গৃহীত হয়েছে।\n📅 ডেলিভারি: {delivery_date}\n💧 ধন্যবাদ!",
                "MA": "✅ {bottle_count} ബോട്ടിലുകളുടെ ഓർഡർ ലഭിച്ചു.\n📅 ഡെലിവറി: {delivery_date}\n💧 നന്ദി!",
            }
            t = translations.get(lang, translations["EN"])
            reply = t.format(
                bottle_count=bottle_count,
                delivery_date=data.delivery_date.strftime("%d-%m-%Y")
            )

    # ======================================================
    # REGISTER NEW CUSTOMER
    # ======================================================
    elif clean_message.startswith("NEW"):
        details = msg[4:].strip()
        pattern = r'^([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*(.+)$'
        match = re.match(pattern, details, re.IGNORECASE)

        if match:
            name, building, house_no, floor, location, emirate = match.groups()
            customer.customer_name = name.strip()
            customer.building_name = building.strip()
            customer.door_house_no = house_no.strip()
            customer.floor_no = floor.strip()
            customer.location = LocationMaster.objects.get(location_name__iexact=location.strip())
            customer.emirate = EmirateMaster.objects.get(name__iexact=emirate.strip())
            customer.is_guest = True   # ✅ keep guest until approved
            customer.save()

            reply = (
                f"✅ Welcome {customer.customer_name}! "
                "You are now registered as a guest.\n\n"
                "Our team will verify your details. Once approved, you can place regular orders."
            )
        else:
            reply = (
                "⚠️ Invalid format.\n\n"
                "Example:\nNEW John, Palm Tower, A-102, 10th, Marina, Dubai"
            )

    # ======================================================
    # COMPLAINT HANDLING
    # ======================================================
    elif match := re.match(r'^complaint\s+(.+)$', msg, re.IGNORECASE):
        complaint_text = match.group(1).strip()
        CustomerComplaints.objects.create(customer=customer, complaint=complaint_text)

        replies = {
            "EN": "📩 Your complaint has been registered. Our support team will contact you shortly.",
            "AR": "📩 تم تسجيل شكواك. سيتواصل معك فريق الدعم قريبًا.",
            "HD": "📩 आपकी शिकायत दर्ज कर ली गई है। हमारी सहायता टीम जल्द ही आपसे संपर्क करेगी।",
            "UR": "📩 آپ کی شکایت درج کر لی گئی ہے۔ ہماری ٹیم جلد ہی آپ سے رابطہ کرے گی۔",
            "BG": "📩 আপনার অভিযোগ নিবন্ধিত হয়েছে। আমাদের সাপোর্ট টিম দ্রুত যোগাযোগ করবে।",
            "MA": "📩 നിങ്ങളുടെ പരാതിയെ രജിസ്റ്റർ ചെയ്തിട്ടുണ്ട്. ഞങ്ങളുടെ സഹായസംഘം ഉടൻ തന്നെ ബന്ധപ്പെടും.",
        }
        reply = replies.get(lang, replies["EN"])

    # ======================================================
    # UNKNOWN COMMAND
    # ======================================================
    else:
        reply = RESPONSES["UNKNOWN"].get(lang, RESPONSES["UNKNOWN"]["EN"])

    # ======================================================
    # Save & send response
    # ======================================================
    WhatsappResponse.objects.create(
        whatsapp_data=whatsapp_data,
        send_to=number,
        message=remove_emojis(reply),
        created_by="system"
    )
    send_whatsapp_simple(number, reply)

    return JsonResponse({"message": reply})
