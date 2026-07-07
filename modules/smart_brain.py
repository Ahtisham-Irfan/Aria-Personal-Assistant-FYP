import json
import os
import random
import threading


class SmartBrain:
    def __init__(self):
        self.model = None
        self.embeddings = None
        self.intents = []
        self.responses = {}
        self.use_transformers = False
        self._ready = False
        self._loading = True

        self._load_data()

        thread = threading.Thread(
            target=self._load_model_background,
            daemon=True
        )
        thread.start()
        print("Smart Brain: Starting in background...")

    def _load_model_background(self):
        try:
            from sentence_transformers import (
                SentenceTransformer, util
            )
            self.util = util
            print("Smart Brain: Loading AI model...")
            self.model = SentenceTransformer(
                'all-MiniLM-L6-v2'
            )
            self._build_embeddings()
            self.use_transformers = True
            self._ready = True
            self._loading = False
            print("Smart Brain: AI mode ready!")
        except Exception as e:
            self._loading = False
            self._ready = True
            self.use_transformers = False
            print(f"Smart Brain: Keyword mode. ({e})")

    def _load_data(self):
        path = os.path.join('data', 'intents.json')
        if not os.path.exists(path):
            self._create_default_intents()

        try:
            with open(
                path, 'r', encoding='utf-8'
            ) as f:
                data = json.load(f)

            for intent in data.get('intents', []):
                tag = intent['tag']
                patterns = intent.get('patterns', [])
                responses = intent.get('responses', [])
                for pattern in patterns:
                    self.intents.append({
                        'pattern': pattern.lower(),
                        'tag': tag
                    })
                self.responses[tag] = responses

            print(
                f"Smart Brain: Loaded "
                f"{len(self.intents)} patterns "
                f"across {len(self.responses)} intents!"
            )
        except Exception as e:
            print(f"Load error: {e}")

    def _build_embeddings(self):
        if not self.intents:
            return
        try:
            patterns = [
                i['pattern'] for i in self.intents
            ]
            self.embeddings = self.model.encode(
                patterns,
                convert_to_tensor=True,
                show_progress_bar=False
            )
            print(
                f"Smart Brain: "
                f"Built {len(patterns)} embeddings!"
            )
        except Exception as e:
            print(f"Embedding error: {e}")
            self.use_transformers = False

    def get_response(self, text, threshold=0.42):
        text = text.lower().strip()

        if self.use_transformers and \
                self.embeddings is not None:
            return self._ai_match(text, threshold)
        else:
            return self._keyword_match(text)

    def _ai_match(self, text, threshold):
        try:
            query_emb = self.model.encode(
                text,
                convert_to_tensor=True,
                show_progress_bar=False
            )
            scores = self.util.cos_sim(
                query_emb, self.embeddings
            )[0]
            best_score = float(scores.max())
            best_idx = int(scores.argmax())

            print(f"AI score: {best_score:.2f}")

            if best_score >= threshold:
                tag = self.intents[best_idx]['tag']
                if tag in self.responses:
                    responses = self.responses[tag]
                    # Pick a random response
                    # avoid repeating last one
                    if len(responses) > 1:
                        return random.choice(
                            responses
                        )
                    return responses[0]
            return None
        except Exception:
            return self._keyword_match(text)

    def _keyword_match(self, text):
        best_tag = None
        best_count = 0

        for intent in self.intents:
            pattern = intent['pattern']
            tag = intent['tag']

            if pattern == text:
                best_tag = tag
                break

            if pattern in text or text in pattern:
                words = pattern.split()
                count = sum(
                    1 for w in words if w in text
                )
                if count > best_count:
                    best_count = count
                    best_tag = tag

        if best_tag and best_count > 0:
            if best_tag in self.responses:
                return random.choice(
                    self.responses[best_tag]
                )
        return None

    def is_ready(self):
        return self._ready

    def is_loading(self):
        return self._loading

    def _create_default_intents(self):
        os.makedirs('data', exist_ok=True)
        default = {"intents": [
            {
                "tag": "greeting",
                "patterns": ["hello", "hi", "hey"],
                "responses": [
                    "Hey! What can I help with?"
                ]
            }
        ]}
        with open(
            os.path.join('data', 'intents.json'),
            'w', encoding='utf-8'
        ) as f:
            json.dump(default, f, indent=4)
