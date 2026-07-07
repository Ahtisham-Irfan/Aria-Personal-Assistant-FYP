class LanguageSupport:
    def __init__(self):
        self.current_language = 'english'

        # Urdu to English command mappings
        self.urdu_commands = {
            # Greetings
            'ہیلو': 'hello',
            'السلام علیکم': 'hello',
            'سلام': 'hello',
            'کیا حال ہے': 'how are you',

            # Time & Date
            'وقت کیا ہے': 'what time is it',
            'ابھی وقت کیا ہے': 'what time is it',
            'آج کی تاریخ': 'what is today date',
            'آج کون سا دن ہے': 'what day is it',

            # Apps
            'کروم کھولو': 'open chrome',
            'نوٹ پیڈ کھولو': 'open notepad',
            'کیلکولیٹر کھولو': 'open calculator',
            'فائل ایکسپلورر کھولو': 'open file explorer',
            'سیٹنگز کھولو': 'open settings',

            # Music
            'گانا چلاو': 'play music',
            'موسیقی چلاو': 'play music',
            'گانا بند کرو': 'stop music',
            'گانا روکو': 'pause music',
            'گانا جاری رکھو': 'resume music',

            # Volume
            'آواز بڑھاو': 'volume up',
            'آواز کم کرو': 'volume down',
            'آواز بند کرو': 'mute volume',

            # System
            'کمپیوٹر بند کرو': 'shutdown',
            'ری اسٹارٹ کرو': 'restart',
            'اسکرین لاک کرو': 'lock screen',
            'سکرین شاٹ لو': 'take screenshot',
            'بیٹری چیک کرو': 'battery status',
            'نیند موڈ': 'sleep',

            # Search
            'سرچ کرو': 'search',
            'ڈھونڈو': 'find',
            'یوٹیوب کھولو': 'open youtube',
            'موسم کیا ہے': 'weather today',

            # Jokes
            'لطیفہ سناو': 'tell me a joke',
            'مجھے ہنساو': 'make me laugh',

            # Goodbye
            'الوداع': 'goodbye aria',
            'خدا حافظ': 'goodbye aria',
            'بند کرو': 'exit aria',

            # Thanks
            'شکریہ': 'thank you',
            'بہت شکریہ': 'thank you so much',
        }

        # Romanized Urdu mappings
        self.roman_urdu_commands = {
            'salam': 'hello',
            'hello aria': 'hello',
            'kya haal hai': 'how are you',
            'waqt kya hai': 'what time is it',
            'chrome kholo': 'open chrome',
            'notepad kholo': 'open notepad',
            'gaana chalao': 'play music',
            'gaana band karo': 'stop music',
            'gaana roko': 'pause music',
            'awaz badhao': 'volume up',
            'awaz kam karo': 'volume down',
            'computer band karo': 'shutdown',
            'restart karo': 'restart',
            'screen lock karo': 'lock screen',
            'screenshot lo': 'take screenshot',
            'battery check karo': 'battery status',
            'latifa sunao': 'tell me a joke',
            'shukriya': 'thank you',
            'alvida': 'goodbye aria',
            'khuda hafiz': 'goodbye aria',
            'mausam kaisa hai': 'weather today',
            'youtube kholo': 'open youtube',
        }

    def set_language(self, language):
        self.current_language = language.lower()
        print(f"Language set to: {language}")

    def translate_to_english(self, text):
        text = text.strip()
        text_lower = text.lower()

        # Check Urdu script
        for urdu, english in \
                self.urdu_commands.items():
            if urdu in text:
                print(
                    f"Urdu: '{urdu}' → '{english}'"
                )
                return english

        # Check Roman Urdu
        for roman, english in \
                self.roman_urdu_commands.items():
            if roman in text_lower:
                print(
                    f"Roman Urdu: "
                    f"'{roman}' → '{english}'"
                )
                return english

        return text

    def is_urdu(self, text):
        urdu_chars = set('اآبپتثجچحخدذرزژسشصضطظعغفقکگلمنوہھیے')
        return any(c in urdu_chars for c in text)

    def get_language(self):
        return self.current_language