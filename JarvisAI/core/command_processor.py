# command_processor.py
"""
Smarter CommandProcessor using keyword groups + simple fuzzy/token overlap scoring.
No external ML libraries required.

API:
    cp = CommandProcessor()
    intent = cp.process("what's the time please")
    # -> {'action': 'time', 'params': {}}
"""

import re
from collections import Counter

# helper: common filler words to remove for cleaner matching
_FILLERS = r'\b(please|could you|would you|hey|jarvis|ok|okay|so|um|uh|the|a|an)\b'

def _normalize(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)             # remove punctuation
    text = re.sub(_FILLERS, " ", text)               # remove filler words
    text = re.sub(r"\s+", " ", text).strip()         # collapse whitespace
    return text

def _tokens(text: str):
    return text.split()

def _overlap_score(tokens, keywords):
    """Simple score: number of keyword tokens present divided by number of keywords."""
    if not keywords:
        return 0.0
    tset = set(tokens)
    kset = set(keywords)
    overlap = len(tset & kset)
    return overlap / len(kset)

class CommandProcessor:
    def __init__(self):
        # Primary actions and their keyword sets or matcher functions
        # keywords: list of representative tokens used for overlap scoring
        self.intent_definitions = {
            'time': {
                'keywords': ['time', 'clock'],
                'patterns': [r'\bwhat.?time\b', r'\btell.*time\b', r'\btime now\b', r'\bcurrent time\b']
            },
            'date': {
                'keywords': ['date', 'day', 'today'],
                'patterns': [r'\bwhat.?date\b', r'\btell.*date\b', r"\bwhat's today\b", r'\bcurrent date\b']
            },
            'weather': {
                'keywords': ['weather', 'temperature', 'forecast', 'rain', 'hot', 'cold'],
                'patterns': [r'\bweather\b', r'\bhow.*temperature\b', r'\bforecast\b']
            },
            'wikipedia': {
                'keywords': ['who', 'what', 'wikipedia', 'wiki', 'tell', 'about'],
                'patterns': [r'\b(who|what)\b.*\b(is|was|are)\b', r'\btell me about\b', r'\bwikipedia\b', r'\bwiki\b']
            },
            'search': {
                'keywords': ['search', 'google', 'find', 'look', 'lookup', 'searching'],
                'patterns': [r'\bsearch\b', r'\blook up\b', r'\bgoogle\b', r'\bfind\b']
            },
            'open_app': {
                'keywords': ['open', 'launch', 'start', 'run'],
                'patterns': [r'\bopen\b', r'\blaunch\b', r'\bstart\b', r'\brun\b']
            },
            'system_status': {
                'keywords': ['cpu', 'battery', 'memory', 'ram', 'network', 'internet', 'status'],
                'patterns': [r'\bsystem\b.*\b(status|info)\b', r'\b(cpu|battery|memory|ram|network|internet)\b']
            },
            'reminder': {
                'keywords': ['remind', 'reminder', 'remember', 'remind me'],
                'patterns': [r'\b(remind|reminder)\b', r'\bremember\b']
            },
            'volume': {
                'keywords': ['volume', 'louder', 'softer', 'mute', 'unmute', 'quieter'],
                'patterns': [r'\b(louder|softer|mute|unmute|volume|quieter)\b']
            },
            'voice_style': {
                'keywords': ['voice', 'style', 'formal', 'casual', 'robotic'],
                'patterns': [r'\b(voice|style)\b', r'\bformal\b', r'\bcasual\b', r'\brobotic\b']
            },
            'help': {
                'keywords': ['help', 'commands', 'features', 'what can you do'],
                'patterns': [r'\bhelp\b', r'\bwhat can you do\b', r'\bcommands\b']
            },
            'exit': {
                'keywords': ['exit', 'quit', 'bye', 'goodbye', 'stop'],
                'patterns': [r'\b(exit|quit|bye|goodbye|stop)\b']
            },
            'listening': {
                'keywords': ['start', 'stop', 'listening'],
                'patterns': [r'\bstart listening\b', r'\bstop listening\b']
            }
        }

        # Additional helper regexes for extracting parameters
        self._regex_city = re.compile(r'in\s+([a-z\s]+)$')     # "weather in lagos"
        self._regex_search = re.compile(r'(?:search\s+for|search|google|find)\s+(.+)$')
        self._regex_open = re.compile(r'(?:open|launch|start|run)\s+(.+)$')
        self._regex_reminder = re.compile(r'remind me (?:to\s+)?(.+?) (?:in|at|on|after)\s+(.+)$')
        self._regex_simple_remind = re.compile(r'remind me to (.+)$')
        self._regex_time_seconds = re.compile(r'(\d+)\s*(second|seconds|minute|minutes|hour|hours)')

    def process(self, text: str):
        """
        Process input text and return intent dict: {'action': str, 'params': {}}
        """
        if not text:
            return {'action': 'unknown', 'params': {'text': text}}

        raw = text
        text = _normalize(text)
        tokens = _tokens(text)

        # Quick exact pattern checks (fast wins)
        for intent, spec in self.intent_definitions.items():
            for pat in spec.get('patterns', []):
                if re.search(pat, text):
                    params = self._extract_params(intent, text, raw)
                    return {'action': intent, 'params': params}

        # If no pattern matched, use keyword overlap scoring
        scores = []
        for intent, spec in self.intent_definitions.items():
            keywords = spec.get('keywords', [])
            score = _overlap_score(tokens, keywords)
            scores.append((intent, score))

        # pick best scored intent (if score is reasonably high)
        scores.sort(key=lambda x: x[1], reverse=True)
        best_intent, best_score = scores[0]

        # threshold: need at least some overlap (e.g., 0.25)
        if best_score >= 0.25:
            params = self._extract_params(best_intent, text, raw)
            return {'action': best_intent, 'params': params}

        # More robust fallback: try keyword membership (contains required tokens)
        for intent, spec in self.intent_definitions.items():
            required = spec.get('keywords', [])[:2]  # simple heuristic
            if required and all(k in tokens for k in required):
                params = self._extract_params(intent, text, raw)
                return {'action': intent, 'params': params}

        # Final fallback: unknown with original text
        return {'action': 'unknown', 'params': {'text': raw}}

    def _extract_params(self, intent: str, text: str, raw: str):
        """Extract parameters for specific intents"""
        params = {}

        if intent == 'weather':
            city_m = self._regex_city.search(text)
            if city_m:
                params['city'] = city_m.group(1).strip()
            else:
                params['city'] = None

        if intent == 'search':
            m = self._regex_search.search(text)
            if m:
                params['query'] = m.group(1).strip()
            else:
                params['query'] = text

        if intent == 'wikipedia':
            # Try common patterns: "who is X", "what is X", "tell me about X", "wiki X"
            # We'll extract the last noun-phrase-ish chunk
            # fallback: use raw stripped phrase after known keywords
            keywords = ['who is', 'what is', 'tell me about', 'wikipedia', 'wiki']
            for kw in keywords:
                if kw in text:
                    phrase = text.split(kw, 1)[1].strip()
                    if phrase:
                        params['query'] = phrase
                        return params
            # otherwise, use entire raw
            params['query'] = raw

        if intent == 'open_app':
            m = self._regex_open.search(text)
            if m:
                params['app'] = m.group(1).strip()
            else:
                params['app'] = text

        if intent == 'reminder':
            m = self._regex_reminder.search(raw.lower())
            if m:
                params['message'] = m.group(1).strip()
                params['time'] = m.group(2).strip()
            else:
                m2 = self._regex_time_seconds.search(raw.lower())
                if m2:
                    params['value'] = int(m2.group(1))
                    params['unit'] = m2.group(2)
                else:
                    # simple fallback: entire raw text as message
                    m3 = self._regex_simple_remind.search(raw.lower())
                    params['message'] = m3.group(1).strip() if m3 else raw

        if intent == 'volume':
            if 'louder' in text or 'increase' in text or 'up' in text:
                params['adjustment'] = 'louder'
            elif 'softer' in text or 'down' in text or 'quieter' in text:
                params['adjustment'] = 'softer'
            elif 'mute' in text or 'silence' in text or 'quiet' in text:
                params['adjustment'] = 'mute'
            else:
                params['adjustment'] = None

        if intent == 'voice_style':
            if 'formal' in text:
                params['style'] = 'formal'
            elif 'casual' in text:
                params['style'] = 'casual'
            elif 'robotic' in text or 'robot' in text:
                params['style'] = 'robotic'
            else:
                params['style'] = None

        if intent == 'system_status':
            if 'cpu' in text:
                params['type'] = 'cpu'
            elif 'battery' in text:
                params['type'] = 'battery'
            elif 'network' in text or 'internet' in text or 'connection' in text:
                params['type'] = 'network'
            else:
                params['type'] = 'all'

        if intent == 'listening':
            if 'start' in text:
                params['mode'] = 'start'
            elif 'stop' in text:
                params['mode'] = 'stop'
            else:
                params['mode'] = None

        return params
