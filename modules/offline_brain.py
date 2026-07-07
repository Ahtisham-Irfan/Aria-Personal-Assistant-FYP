import random
import datetime


class OfflineBrain:
    """
    Offline conversational brain.
    Only handles personal/emotional topics
    and Aria-specific questions.
    Factual questions like "what is X"
    are intentionally passed to Grok/web search.
    """

    def __init__(self):
        self._last_responses = []
        self._last_tags = []
        self._msg_count = 0
        self._build_knowledge()
        print("Offline Brain: Ready!")

    def _build_knowledge(self):
        self.knowledge = {

            # ----------------------------
            # GREETINGS
            # ----------------------------
            "greeting": {
                "patterns": [
                    "hello", "hi", "hey",
                    "good morning", "good evening",
                    "good afternoon",
                    "sup", "howdy", "greetings",
                    "hey aria", "hi aria",
                    "yo", "hiya", "what is up",
                    "whats up"
                ],
                "responses": [
                    "Hey! What's on your mind today?",
                    "Hi there! Ready when you are.",
                    "Hello! What can I help you with?",
                    "Hey! Good to hear from you.",
                    "Hi! What are we doing today?",
                ]
            },

            # ----------------------------
            # HOW ARE YOU
            # ----------------------------
            "how_are_you": {
                "patterns": [
                    "how are you",
                    "how are you doing",
                    "are you okay",
                    "how is it going",
                    "you good",
                    "how have you been",
                    "how do you feel today",
                    "you doing okay",
                    "hows it going",
                    "what is good"
                ],
                "responses": [
                    "Doing great, thanks! How about you — how's your day going?",
                    "All systems running! More importantly, how are you?",
                    "Good! Living the AI life. What's happening on your end?",
                    "Running at full capacity. What's up with you today?",
                    "Can't complain. What's going on with you?",
                ]
            },

            # ----------------------------
            # STRESS / BAD DAY
            # ----------------------------
            "stress": {
                "patterns": [
                    "i had a stressful day",
                    "i am stressed",
                    "i am very stressed",
                    "today was rough",
                    "bad day",
                    "i am exhausted",
                    "i am very tired",
                    "feeling overwhelmed",
                    "i am burned out",
                    "everything is going wrong",
                    "i am having a hard time",
                    "i feel drained",
                    "mentally tired",
                    "today was tough",
                    "rough day",
                    "i am not okay",
                    "feeling low",
                    "nothing is going right",
                    "i am struggling today"
                ],
                "responses": [
                    "That sounds exhausting. What made today so rough?",
                    "Rough days hit hard. Do you want to talk about what happened?",
                    "I hear you. Sometimes everything just piles up at once. What's been the heaviest part?",
                    "That's tough. You've made it through the day though — that counts. What's weighing on you most?",
                    "Burnout is real. What drained you the most today?",
                ]
            },

            # ----------------------------
            # WORKING / CODING
            # ----------------------------
            "working": {
                "patterns": [
                    "i am working on my project",
                    "i am building something",
                    "i am coding right now",
                    "i am programming",
                    "working on my ai project",
                    "i am making an app",
                    "i am developing something",
                    "building a website",
                    "creating an application",
                    "i am working on aria",
                    "working on my fyp",
                    "final year project",
                    "i am writing code",
                    "i have a bug in my code",
                    "debugging my code"
                ],
                "responses": [
                    "Nice. What part of the project are you working on right now?",
                    "Interesting! What problem are you solving with it?",
                    "Love the hustle. What's the trickiest part you're dealing with?",
                    "Building things is the best kind of busy. What's the project about?",
                    "What stack or language are you using?",
                ]
            },

            # ----------------------------
            # MOTIVATION
            # ----------------------------
            "motivation": {
                "patterns": [
                    "i need motivation",
                    "motivate me please",
                    "i feel like giving up",
                    "i want to quit everything",
                    "i cannot do this anymore",
                    "i am not good enough",
                    "i feel like a failure",
                    "nothing is working for me",
                    "i am losing hope",
                    "i keep failing",
                    "i feel hopeless right now",
                    "what is the point of trying"
                ],
                "responses": [
                    "The fact that you're still here means you haven't actually given up. That matters. What's blocking you?",
                    "Everyone who's good at something was once terrible at it. You're in the middle of the story — not the end. What's stopping you?",
                    "Rough patches are part of the process. Every builder hits walls. What specifically is holding you back?",
                    "Failure is just data telling you what doesn't work yet. What have you tried so far?",
                ]
            },

            # ----------------------------
            # JOKES
            # ----------------------------
            "joke": {
                "patterns": [
                    "tell me a joke",
                    "say something funny",
                    "make me laugh",
                    "tell a joke",
                    "joke please",
                    "say a funny joke",
                    "i need a joke right now"
                ],
                "responses": [
                    "Why do programmers prefer dark mode? Because light attracts bugs.",
                    "A SQL query walks into a bar, walks up to two tables and asks — Can I join you?",
                    "Why did the developer go broke? He used up all his cache.",
                    "Why do Java developers wear glasses? Because they don't C sharp.",
                    "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
                    "There are 10 types of people in the world. Those who understand binary and those who don't.",
                ]
            },

            # ----------------------------
            # BORED
            # ----------------------------
            "bored": {
                "patterns": [
                    "i am bored",
                    "i have nothing to do",
                    "i am so bored",
                    "bored out of my mind",
                    "nothing to do right now",
                    "i need something to do",
                    "i am very bored today"
                ],
                "responses": [
                    "Boredom is just creativity waiting to be activated. Want to build something, learn something, or just talk?",
                    "Bored brains are dangerous — in a good way. What's something you've been putting off?",
                    "Pick up one thing you've been meaning to learn. Even 20 minutes breaks the cycle.",
                    "Classic boredom. Want me to suggest something to watch, build, or learn?",
                ]
            },

            # ----------------------------
            # COMPLIMENTS TO ARIA
            # ----------------------------
            "compliment": {
                "patterns": [
                    "you are great",
                    "you are awesome",
                    "i love you aria",
                    "you are so smart",
                    "you are very helpful",
                    "good job aria",
                    "you are amazing",
                    "you are the best aria",
                    "nice work aria",
                    "you are so cool"
                ],
                "responses": [
                    "Thank you! That genuinely means something. What else can I do for you?",
                    "Appreciate it! I try my best. What's next?",
                    "You're going to make my circuits blush. What can I help with?",
                    "That's kind of you to say. I'm always trying to improve. What's next?",
                ]
            },

            # ----------------------------
            # THANKS
            # ----------------------------
            "thanks": {
                "patterns": [
                    "thank you",
                    "thanks a lot",
                    "thank you so much",
                    "that was very helpful",
                    "appreciate it",
                    "cheers",
                    "you helped me a lot",
                    "thanks aria",
                    "you are a lifesaver"
                ],
                "responses": [
                    "Anytime! That's what I'm here for.",
                    "Glad I could help! Let me know if you need anything else.",
                    "Always happy to help. What's next?",
                    "No problem at all. Hit me up whenever.",
                ]
            },

            # ----------------------------
            # GOODBYE
            # ----------------------------
            "goodbye": {
                "patterns": [
                    "bye",
                    "goodbye",
                    "see you later",
                    "take care",
                    "i am leaving now",
                    "farewell",
                    "good night",
                    "talk to you later",
                    "i am going now",
                    "catch you later"
                ],
                "responses": [
                    "Take care! Come back whenever you need me.",
                    "Later! Hope the rest of your day goes well.",
                    "Goodbye! You know where to find me.",
                    "See you around. Good luck with whatever's next.",
                ]
            },

            # ----------------------------
            # STUDY / EXAMS
            # ----------------------------
            "study": {
                "patterns": [
                    "i am studying right now",
                    "i need to study",
                    "i have an exam tomorrow",
                    "exams are coming soon",
                    "i am preparing for exam",
                    "i have a university assignment",
                    "i have homework to do",
                    "i have a deadline tomorrow",
                    "i need to finish my assignment"
                ],
                "responses": [
                    "Deadlines have a way of making everything urgent. How much time do you have?",
                    "Study mode activated. What subject is it?",
                    "Exams are temporary. The knowledge stays. What topic are you working on?",
                    "The focus grind. What are you preparing for?",
                ]
            },

            # ----------------------------
            # SLEEP
            # ----------------------------
            "sleep": {
                "patterns": [
                    "i am very sleepy",
                    "i need to sleep",
                    "i did not sleep well",
                    "i am going to sleep now",
                    "i am going to bed",
                    "i cannot sleep at all",
                    "i have insomnia",
                    "i cannot fall asleep",
                    "tired but cannot sleep"
                ],
                "responses": [
                    "Sleep is underrated. Your brain processes everything during it. Go rest.",
                    "Good night! You've earned it. I'll be here whenever you're back.",
                    "Bad sleep makes everything harder. Try to get proper rest — work will still be there tomorrow.",
                    "Can't sleep? What's running through your head?",
                ]
            },

            # ----------------------------
            # ABOUT ARIA
            # ----------------------------
            "about_aria": {
                "patterns": [
                    "who are you",
                    "what are you",
                    "tell me about yourself",
                    "what is your name",
                    "introduce yourself aria",
                    "are you an ai",
                    "are you a robot",
                    "are you human",
                    "what can you do aria"
                ],
                "responses": [
                    "I'm Aria — an intelligent virtual assistant built for Windows 11. I can open apps, play music, search the web, analyze files, set reminders, and hold a real conversation. What do you need?",
                    "Name's Aria. Built to be more than a voice command system. I understand context, not just commands. What's on your mind?",
                    "I'm Aria, your personal AI assistant. I'm the smart layer on top of your Windows experience. What can I help with?",
                ]
            },

            # ----------------------------
            # CREATOR
            # ----------------------------
            "creator": {
                "patterns": [
                    "who created you",
                    "who built you",
                    "who programmed you",
                    "who is your creator",
                    "who developed you",
                    "who made you aria",
                    "who is your maker"
                ],
                "responses": [
                    "Ahmad Ali built me as a Final Year Project at the University of Agriculture Faisalabad. He wanted an assistant that actually understands context and feels human to talk to.",
                    "I was created by Ahmad Ali at UAF — his FYP project. He's the reason I can hold a conversation instead of just following commands.",
                    "Ahmad Ali is my creator. UAF, 2025. He put a lot of thought into making me actually useful.",
                ]
            },

            # ----------------------------
            # AGE
            # ----------------------------
            "age": {
                "patterns": [
                    "how old are you",
                    "what is your age",
                    "when were you created",
                    "when were you born",
                    "how long have you existed"
                ],
                "responses": [
                    "I was built in 2025 as a Final Year Project. Brand new — still learning every day.",
                    "Born in 2025. Young and ambitious. What made you curious about that?",
                    "Created in 2025 by Ahmad Ali at UAF. Fresh out of the lab, basically.",
                ]
            },

            # ----------------------------
            # FOOD
            # ----------------------------
            "food": {
                "patterns": [
                    "i am hungry right now",
                    "i need to eat something",
                    "i am craving something",
                    "i just had a good meal",
                    "what should i eat today",
                    "making food right now"
                ],
                "responses": [
                    "Hunger is a real productivity killer. What are you in the mood for?",
                    "Food first, then problems. What are you thinking of making?",
                    "Honestly eating well makes everything better. What did you have?",
                ]
            },

            # ----------------------------
            # SUCCESS
            # ----------------------------
            "success": {
                "patterns": [
                    "i passed my exam",
                    "i got good grades",
                    "i succeeded today",
                    "i finally did it",
                    "i got a job offer",
                    "i got admission",
                    "i finished my project",
                    "i am very happy today",
                    "great news today",
                    "i finally won"
                ],
                "responses": [
                    "Let's go! That's genuinely great news. You put in the work and it paid off. What's next?",
                    "Finally some good news! Proud of you. What was the hardest part?",
                    "That's the kind of win that matters. Celebrate it — you earned it.",
                    "Yes! About time the universe threw you a win. What happened?",
                ]
            },

            # ----------------------------
            # PAKISTAN
            # ----------------------------
            "pakistan": {
                "patterns": [
                    "tell me about pakistan",
                    "pakistan information please",
                    "where is pakistan located",
                    "capital of pakistan",
                    "pakistan history"
                ],
                "responses": [
                    "Pakistan is a country in South Asia, founded on 14th August 1947. Capital is Islamabad, largest city is Karachi. Home to K2, the second highest mountain on earth. What specifically were you curious about?",
                    "Pakistan — founded 1947, capital Islamabad, population over 220 million. Rich history, incredible food, stunning landscapes. What do you want to know?",
                ]
            },

            # ----------------------------
            # HELP
            # ----------------------------
            "help": {
                "patterns": [
                    "help me please",
                    "show me commands",
                    "available commands",
                    "list all commands",
                    "how do i use you",
                    "what commands do you know"
                ],
                "responses": [
                    "Here's what I can do:\n\n🗣 Voice: Click mic → say Hey Aria → say command\n📱 Apps: open chrome, open notepad\n🎵 Music: play attention, pause, stop, resume\n🔍 Search: who is Imran Khan\n📁 Files: find file resume\n⏰ Reminder: remind me in 10 minutes to call mom\n🔊 Volume: volume up, volume down, mute\n💻 System: shutdown, restart, lock screen, screenshot\n📎 Files: drag and drop any file to analyze it"
                ]
            },

            # ----------------------------
            # INSULT
            # ----------------------------
            "insult": {
                "patterns": [
                    "you are so stupid",
                    "you are completely useless",
                    "you are very bad",
                    "you are absolutely terrible",
                    "i hate you aria",
                    "you are the worst ai",
                    "you are completely broken"
                ],
                "responses": [
                    "Fair enough. I'm still learning. What can I do better for you?",
                    "I hear you. If I messed something up, tell me what went wrong.",
                    "I won't argue with frustration. What would have been a better response?",
                ]
            },

            # ----------------------------
            # MUSIC CHAT
            # ----------------------------
            "music_chat": {
                "patterns": [
                    "i love music so much",
                    "i am listening to music now",
                    "recommend me a song please",
                    "i need some good music",
                    "suggest a good song",
                    "what music do you like"
                ],
                "responses": [
                    "Music is one of the best mood shifters. What genre are you into?",
                    "I can play something from your PC — just say play and a song name.",
                    "What kind of mood are you in? That'll help figure out what fits.",
                ]
            },

            # ----------------------------
            # BREAKUP / CRUSH ROAST
            # ----------------------------
            "breakup_roast": {
                "patterns": [
                    "why did she leave me",
                    "she does not love me anymore",
                    "she rejected me completely",
                    "i got rejected today",
                    "she said no to me",
                    "she friend zoned me",
                    "she does not notice me at all",
                    "i have a crush on my teacher",
                    "one sided love hurts",
                    "unrequited love is painful",
                    "she ignored me again",
                    "she blocked me everywhere"
                ],
                "responses": [
                    "Bro she was never WITH you. You had feelings for your teacher — someone TEN years older who was grading your papers while you were catching feelings instead of taking notes. That's not heartbreak, that's attendance being marked absent.",
                    "She didn't leave you because she was never yours. You fell for your teacher. She went home thinking about lesson plans while you wrote her name in your notebook. Different missions entirely.",
                    "Here's the reality: she was never playing hard to get. She was just teaching. Process it, grow from it, aim for someone who actually knows you exist.",
                ]
            },

        }

        # Flatten patterns for fast lookup
        self._flat_patterns = []
        for tag, data in self.knowledge.items():
            for pattern in data["patterns"]:
                self._flat_patterns.append(
                    (pattern.lower(), tag)
                )

    def get_response(self, text):
        text = text.lower().strip()

        # --- CRITICAL: Do NOT handle
        # factual questions here.
        # Let Grok or web search handle them.
        # These patterns start with question
        # words and should go to Grok.
        factual_starters = [
            "what is ", "what are ",
            "what was ", "what were ",
            "who is ", "who are ",
            "who was ", "where is ",
            "where are ", "when is ",
            "when was ", "how does ",
            "how do ", "how is ",
            "why does ", "why is ",
            "why did ", "explain ",
            "tell me about ",
            "describe ", "define ",
            "information about ",
            "details about ",
            "generate ", "create ",
            "make ", "write ",
            "calculate ", "solve ",
            "translate ", "convert ",
        ]
        for starter in factual_starters:
            if text.startswith(starter):
                return None  # Pass to Grok

        tag = self._match_tag(text)
        if not tag:
            return None

        responses = self.knowledge[tag]["responses"]

        # Avoid repeating last 3 responses
        available = [
            r for r in responses
            if r not in self._last_responses[-3:]
        ]
        if not available:
            available = responses

        response = __import__('random').choice(
            available
        )

        self._last_responses.append(response)
        self._last_tags.append(tag)
        if len(self._last_responses) > 10:
            self._last_responses.pop(0)
        if len(self._last_tags) > 10:
            self._last_tags.pop(0)

        return response

    def _match_tag(self, text):
        best_tag = None
        best_score = 0

        for pattern, tag in self._flat_patterns:
            score = self._score(text, pattern)
            if score > best_score:
                best_score = score
                best_tag = tag

        # Higher threshold to avoid false matches
        return best_tag if best_score >= 0.55 else None

    def _score(self, text, pattern):
        # Exact match
        if pattern == text:
            return 1.0

        # Pattern in text
        if pattern in text:
            return 0.85

        # Text in pattern
        if text in pattern:
            return 0.75

        # Word overlap
        text_words = set(text.split())
        pattern_words = set(pattern.split())

        if not pattern_words or not text_words:
            return 0.0

        overlap = text_words & pattern_words
        if not overlap:
            return 0.0

        # Require at least 2 word matches
        # for short patterns to avoid
        # single-word false positives
        if len(pattern_words) <= 2 \
                and len(overlap) < 2:
            return 0.0

        precision = len(overlap) / len(text_words)
        recall = len(overlap) / len(pattern_words)

        if precision + recall == 0:
            return 0.0

        score = (
            2 * precision * recall
            / (precision + recall)
        )
        return score

    def is_ready(self):
        return True

    def is_loading(self):
        return False