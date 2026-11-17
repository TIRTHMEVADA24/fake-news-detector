"""
Comprehensive NLP Engine for Project 4: Fake News Detection and News Sentiment Analysis
Features:
1. Gibberish & Random Typing Detection (consonant clustering, vowel ratio, dictionary overlap)
2. Broad-Coverage Real vs Fake News Training Corpus across Politics, Tech, Health, Crime, Finance, Viral Hoaxes
3. Sublinear TF-IDF (1-2 N-grams) with Logistic Regression, Multinomial Naive Bayes, and Ensemble
4. Fine-grained Sentiment Polarity & Subjectivity Analysis
5. Journalistic Credibility Markers vs Sensational Clickbait Cue Matching
6. Explainable Word/Phrase Highlights
"""

import re
import math
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# English Stopwords
STOPWORDS = set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've",
    "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
    'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them',
    'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll",
    'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
    'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
    'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
    'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've",
    'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn',
    'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn',
    'wasn', 'weren', 'won', 'wouldn'
])

# Common English dictionary vocabulary sample for gibberish detection
COMMON_VOCAB = set([
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with",
    "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her",
    "she", "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up",
    "out", "if", "about", "who", "get", "which", "go", "me", "when", "make", "can", "like", "time",
    "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could",
    "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think",
    "also", "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even",
    "new", "want", "because", "any", "these", "give", "day", "most", "us", "is", "was", "are",
    "has", "had", "been", "were", "said", "reported", "police", "court", "government", "minister",
    "president", "prime", "official", "hospital", "doctor", "health", "case", "death", "trial",
    "science", "space", "launch", "satellite", "bank", "market", "economy", "growth", "study",
    "research", "university", "school", "students", "country", "state", "city", "public", "world",
    "news", "report", "media", "claim", "video", "photo", "viral", "post", "online", "found", "showed",
    "india", "delhi", "mumbai", "us", "china", "election", "vote", "party", "bjp", "congress",
    "leader", "arrest", "attack", "security", "army", "border", "warns", "announces", "plans"
])

# Journalistic Credibility Markers (Strong Real Indicators)
CREDIBILITY_MARKERS = [
    "according to", "spokesperson", "spokesman", "official statement", "press release",
    "confirmed by", "study published", "researchers found", "in an interview", "reuters",
    "associated press", "reported by", "data shows", "authorized officials", "police said",
    "court ruled", "investigation revealed", "peer-reviewed", "statistics indicate",
    "ministry of", "department of", "director general", "supreme court", "high court",
    "officially announced", "statement said", "press conference", "government data"
]

# Sensationalist & Clickbait Markers (Strong Fake / Deceptive Indicators)
CLICKBAIT_MARKERS = [
    "shocking", "miracle cure", "miracle remedy", "secret revealed", "they don't want you to know",
    "100% cure", "100% proven", "banned by government", "wake up sheeple", "share before deleted",
    "forward this", "bomb revelation", "illuminati", "alien invasion", "chemtrails", "5g towers",
    "hidden truth", "cure for cancer", "magic pill", "instant weight loss", "get rich overnight",
    "guaranteed returns", "leaked tape", "mind control", "doctors are hiding", "unbelievable truth",
    "unesco declared", "unesco awarded", "microchip in vaccine", "nanobots", "share to all groups",
    "forward to 10", "forward to all", "viral video reveals", "delete immediately"
]

POSITIVE_WORDS = set([
    "good", "great", "excellent", "positive", "fortunate", "correct", "superior", "remarkable",
    "growth", "success", "innovative", "triumph", "breakthrough", "progress", "peace", "win",
    "beneficial", "promising", "advancement", "verified", "authentic", "confirmed", "stable",
    "recovery", "solution", "optimistic", "impressive", "historic", "constructive", "healthy",
    "safe", "effective", "achieved", "developed", "supported", "approved", "honored", "celebrated"
])

NEGATIVE_WORDS = set([
    "bad", "terrible", "horrible", "negative", "unfortunate", "wrong", "inferior", "shocking",
    "disaster", "crisis", "threat", "failure", "danger", "scandal", "collapse", "corrupt",
    "fraud", "conspiracy", "hoax", "outrage", "panic", "toxic", "deadly", "catastrophe",
    "exposed", "illegal", "criminal", "devastating", "alarming", "fake", "ruin", "arrested",
    "killed", "victim", "destroyed", "banned", "guilty", "suffered", "shameful", "deceived"
])

# Expanded, diverse multi-domain training dataset
TRAINING_ARTICLES = [
    # --- REAL NEWS ARTICLES (0) ---
    # Space & Tech
    ("The National Aeronautics and Space Administration (NASA) launched its newest climate monitoring satellite from Vandenberg Space Force Base on Tuesday. The mission aims to gather precision atmospheric data on carbon dioxide emissions and sea-level fluctuations to assist global meteorologists.", 0),
    ("The Indian Space Research Organisation (ISRO) successfully accomplished the orbital insertion of its lunar orbiter following a twenty-two minute thruster burn. Telemetry stations confirmed all solar arrays deployed according to nominal schedules, with onboard spectrometers commencing scientific transmission.", 0),
    ("Apple and Google announced a joint technical specification to combat unwanted tracking by Bluetooth location tags. The standard was submitted to the Internet Engineering Task Force (IETF) following industry reviews.", 0),
    ("Telecom operators rolled out commercial 5G spectrum networks in metro regions after completing statutory spectrum auctions managed by the Department of Telecommunications.", 0),
    ("The European Space Agency confirmed the successful rendezvous of its Jupiter Icy Moons Explorer (Juice) spacecraft following a gravity-assist flyby of the Earth and Moon.", 0),
    ("Semiconductor chip manufacturers announced a multi-billion dollar investment in new fabrication units in Gujarat, according to the official statement released by the Ministry of Electronics and IT.", 0),

    # Health & Medicine
    ("The World Health Organization confirmed the conclusion of clinical phase three trials for a next-generation malaria vaccine. According to peer-reviewed data published in the Lancet medical journal, the vaccine demonstrated a seventy-seven percent efficacy rate in randomized trials.", 0),
    ("Researchers at Oxford University published findings documenting antibiotic resistance patterns across four hospital networks. The peer-reviewed study recommended rationalized prescribing standards and enhanced microbiological surveillance.", 0),
    ("The Ministry of Health reported a seasonal increase in dengue cases across suburban districts and advised municipal corporations to carry out anti-larval fogging and public awareness campaigns.", 0),
    ("A clinical trial evaluating a novel monoclonal antibody therapy for Alzheimer's disease showed a modest twenty-seven percent reduction in cognitive decline over eighteen months, according to trial results presented at the International Conference.", 0),
    ("Doctors at AIIMS hospital successfully performed a complex pediatric heart surgery using 3D printed heart models, authorities said in a medical bulletin on Monday.", 0),

    # Politics, Law & Governance
    ("The Supreme Court issued a constitutional ruling affirming statutory data privacy boundaries for commercial software applications. The nine-justice bench delivered a unanimous opinion underscoring user consent and encrypted audit logging.", 0),
    ("The Election Commission announced election schedules for state legislative assemblies across five states, enforcing the model code of conduct with immediate effect.", 0),
    ("Parliament passed the new digital telecommunications bill following three days of debate in the upper house, establishing streamlined licensing rules for satellite broadband providers.", 0),
    ("Finance ministers from G20 economies gathered in Geneva to ratify a standardized corporate taxation framework. The official communique emphasized equitable digital service taxes, anti-evasion protocols, and cooperative enforcement across member jurisdictions.", 0),
    ("The central bank raised benchmark interest rates by twenty-five basis points following annualized consumer price index data. Economists noted that monetary tightening is designed to stabilize inflation towards the long-term two percent target over four fiscal quarters.", 0),
    ("Prime Minister inaugurated the new international airport terminal, stating that the project will boost regional tourism and cargo connectivity according to official government reports.", 0),
    ("Police arrested three suspects in connection with a corporate financial fraud case after a six-month investigation, police commissioner confirmed in a press conference.", 0),

    # Environment, Sports & Society
    ("Renewable energy capacity expanded by fifteen percent worldwide during the previous calendar year, according to the International Energy Agency. Solar photovoltaic installations accounted for three quarters of newly added electric generation capacity.", 0),
    ("The United Nations General Assembly adopted a resolution establishing formal maritime conservation guidelines in international waters. Representatives from one hundred and twenty nations voted affirmatively following bilateral negotiations.", 0),
    ("Automobile manufacturers announced joint investments in battery recycling facilities across regional industrial corridors to reduce lithium supply dependency and support circular manufacturing supply chains.", 0),
    ("The national cricket team secured qualification for the championship final after defeating Australia by four wickets in the semi-final match held at the international stadium.", 0),
    ("Meteorological department issued rainfall alerts for coastal areas due to a low-pressure depression forming over the Bay of Bengal, advising fishermen to avoid venturing into deep waters.", 0),

    # --- FAKE NEWS & HOAXES (1) ---
    # Health Hoaxes
    ("SHOCKING: Scientists discover secret ancient herb that cures all cancers overnight! Pharmaceutical companies and corrupt doctors are desperately hiding this miracle cure from the public to protect their trillion-dollar profits! Share before it gets deleted!", 1),
    ("MIRACLE DISCOVERY: Drinking raw saltwater mixed with boiled garlic eliminates all viral infections within fifteen minutes! Hospitals are furious because this zero dollar remedy makes medicines obsolete!", 1),
    ("ALERT: Government is secretly putting nanobots into public drinking water to control citizen thoughts and manipulate heart rates! Drink boiled vinegar immediately to deactivate the microchips before midnight!", 1),
    ("Doctors reveal this one secret fruit removes all blockages in heart arteries in three hours without surgery! Big Pharma is threatening to take this video down immediately!", 1),
    ("SHOCKING HOAX EXPOSED: Doctors secretly inject digital tracking chips into newborn babies! Corrupt pharmaceutical cabal profits billions while parents are kept in total darkness!", 1),
    ("Eating raw onions kept in your socks absorbs all deadly toxins and cures pneumonia overnight! Doctors don't want you to know this simple secret remedy!", 1),

    # Conspiracies & WhatsApp Viral Hoaxes
    ("BREAKING BOMBSHELL: Secret leaked documents prove that world leaders are secretly building a subterranean city on Mars using alien technology and tax dollars! Mainstream media refuses to report the truth! Wake up sheeple!", 1),
    ("You won't believe what this politician did! Hidden camera catches top official admitting that the election was completely staged by holographic projections! Government insiders are running in panic!", 1),
    ("EXPOSED: Billionaire elite caught admitting climate change is a complete hoax invented to ban all motor vehicles and enforce global curfew! Download this video before authorities take it down forever!", 1),
    ("UNBELIEVABLE: Astronaut returns from moon and reveals he encountered reptilian humanoid creatures guarding secret golden pyramids! NASA ordered him to stay silent under threat of execution!", 1),
    ("WARNING: 5G cellular antennas are emitting classified psychological frequencies designed to trigger mass hysteria and force citizens to surrender their bank accounts to offshore cartels!", 1),
    ("Secret military whistleblower exposes hidden electromagnetic weapon that can manufacture earthquakes and volcanic eruptions on demand against innocent nations! The truth is finally out!", 1),
    ("UNESCO has officially declared India's national anthem as the best national anthem in the world! Forward this message to all groups to make every citizen proud! Jai Hind!", 1),
    ("Forward this urgent message: If you don't forward this message to twenty contacts immediately, your messaging account will be deleted by midnight and you will be fined fifty thousand rupees!", 1),
    ("Breaking: RBI just announced that all pink 2000 rupee notes have a GPS microchip embedded inside them that transmits location directly to satellite even when kept 120 meters underground!", 1),
    ("Click this link to receive free thousand gigabytes of high-speed internet data and five hundred rupee mobile recharge approved directly by the prime minister for everyone!", 1),
    ("NASA satellite captured real photos of mythical flying dragons flying over the Himalayas! Government immediately covered it up and threatened the scientists with execution! Watch before it's deleted!", 1),
    ("World Health Organization secretly admits that all medicines were a massive psychological experiment! Stop taking your pills immediately and share this truth to save your family!", 1)
]

class FakeNewsNLPEngine:
    def __init__(self):
        # 1. Logistic Regression Pipeline
        self.lr_pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                sublinear_tf=True,
                max_features=4000
            )),
            ('clf', LogisticRegression(C=1.2, solver='liblinear', random_state=42))
        ])

        # 2. Multinomial Naive Bayes Pipeline
        self.nb_pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                sublinear_tf=True,
                max_features=4000
            )),
            ('clf', MultinomialNB(alpha=0.15))
        ])

        self._train_models()

    def _train_models(self):
        texts = [x[0] for x in TRAINING_ARTICLES]
        labels = [x[1] for x in TRAINING_ARTICLES]
        
        self.lr_pipeline.fit(texts, labels)
        self.nb_pipeline.fit(texts, labels)

    def detect_gibberish(self, raw_text):
        """
        Detects random keyboard mashing (e.g., 'fnsdoivhsdvoinsd', 'asdfghjkl').
        Returns (is_gibberish: bool, reason: str).
        """
        stripped = raw_text.strip()
        if len(stripped) < 10:
            return True, "Input is too short to be a valid news article or headline."

        words = re.findall(r'[a-zA-Z]+', stripped.lower())
        if not words:
            return True, "No alphabetical words detected."

        # Check total word count
        if len(words) == 1 and len(words[0]) > 14:
            # Single extremely long continuous token (typical keyboard mash like 'fnsdoivhsdvoinsd')
            return True, "Single unbroken string of random characters detected."

        # Check vowel ratio
        total_letters = sum(len(w) for w in words)
        vowel_count = sum(c in 'aeiou' for w in words for c in w)
        if total_letters > 0:
            vowel_ratio = vowel_count / total_letters
            if vowel_ratio < 0.16 or vowel_ratio > 0.70:
                return True, "Abnormal consonant/vowel distribution (keyboard mash pattern detected)."

        # Check dictionary vocabulary overlap
        known_hits = sum(1 for w in words if w in COMMON_VOCAB or len(w) <= 2)
        vocab_overlap = known_hits / max(len(words), 1)

        # If text has 4+ words and less than 15% recognizable words
        if len(words) >= 4 and vocab_overlap < 0.15:
            return True, "Text contains very few recognizable dictionary words."
        elif len(words) < 4 and known_hits == 0:
            return True, "Unrecognized words or non-standard random character sequence."

        return False, ""

    def clean_text(self, text):
        """Standard NLP text preprocessing."""
        cleaned = text.lower()
        cleaned = re.sub(r'https?://\S+|www\.\S+', ' ', cleaned)
        cleaned = re.sub(r'[^a-zA-Z\s]', ' ', cleaned)
        tokens = cleaned.split()
        filtered_tokens = [w for w in tokens if w not in STOPWORDS and len(w) > 2]
        return filtered_tokens, " ".join(filtered_tokens)

    def compute_sentiment(self, text):
        """Sentiment Polarity (-1.0 to +1.0) and Subjectivity (0.0 to 1.0)."""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
        total_matched = pos_count + neg_count

        if total_matched == 0:
            polarity = 0.0
            sentiment_label = "Neutral"
        else:
            polarity = round((pos_count - neg_count) / total_matched, 2)
            if polarity > 0.2:
                sentiment_label = "Positive"
            elif polarity < -0.2:
                sentiment_label = "Negative"
            else:
                sentiment_label = "Neutral"

        total_words = max(len(words), 1)
        emotional_density = total_matched / total_words
        clickbait_hits = sum(1 for cb in CLICKBAIT_MARKERS if cb in text.lower())
        
        subjectivity = min(round((emotional_density * 3.0) + (clickbait_hits * 0.25), 2), 1.0)
        
        if subjectivity > 0.6:
            subjectivity_label = "Highly Subjective / Emotional"
        elif subjectivity > 0.3:
            subjectivity_label = "Moderately Subjective"
        else:
            subjectivity_label = "Objective & Factual"

        return {
            "polarity": polarity,
            "sentiment_label": sentiment_label,
            "positive_words_count": pos_count,
            "negative_words_count": neg_count,
            "subjectivity": subjectivity,
            "subjectivity_label": subjectivity_label,
            "clickbait_hits": clickbait_hits
        }

    def extract_linguistic_cues(self, raw_text):
        """Extract stylometric markers: Caps, exclamation, journalistic vs clickbait."""
        total_chars = max(len(raw_text), 1)
        uppercase_chars = sum(1 for c in raw_text if c.isupper())
        uppercase_ratio = round((uppercase_chars / total_chars) * 100, 1)

        exclamation_count = raw_text.count('!')
        question_count = raw_text.count('?')

        detected_clickbait = [cb for cb in CLICKBAIT_MARKERS if cb in raw_text.lower()]
        detected_credibility = [cr for cr in CREDIBILITY_MARKERS if cr in raw_text.lower()]

        sensationalism_score = min(
            round((uppercase_ratio * 1.5) + (exclamation_count * 8.0) + (len(detected_clickbait) * 22.0), 1),
            100.0
        )

        return {
            "uppercase_ratio": uppercase_ratio,
            "exclamation_count": exclamation_count,
            "question_count": question_count,
            "detected_clickbait": detected_clickbait,
            "detected_credibility": detected_credibility,
            "sensationalism_score": sensationalism_score
        }

    def predict(self, raw_text, model_type="lr"):
        """
        Classifies news as REAL (0) or FAKE (1).
        Handles gibberish inputs with clear explanatory errors.
        """
        # Step 1: Gibberish / Random Typing Validation
        is_gibberish, reason = self.detect_gibberish(raw_text)
        if is_gibberish:
            return {
                "is_gibberish": True,
                "error_message": f"Input unrecognized as valid news: {reason}",
                "prediction": "INVALID / UNVERIFIABLE",
                "is_fake": False,
                "confidence": 0.0,
                "real_probability": 0.0,
                "fake_probability": 0.0,
                "active_model": "Input Quality Filter",
                "sentiment": {
                    "polarity": 0.0,
                    "sentiment_label": "N/A",
                    "positive_words_count": 0,
                    "negative_words_count": 0,
                    "subjectivity": 0.0,
                    "subjectivity_label": "Unverifiable",
                    "clickbait_hits": 0
                },
                "linguistic_cues": {
                    "uppercase_ratio": 0.0,
                    "exclamation_count": 0,
                    "question_count": 0,
                    "detected_clickbait": [],
                    "detected_credibility": [],
                    "sensationalism_score": 0.0
                },
                "token_count": 0,
                "cleaned_sample": "N/A"
            }

        # Step 2: NLP Preprocessing
        tokens, cleaned_text = self.clean_text(raw_text)
        
        # Step 3: Probabilities from ML models
        lr_probs = self.lr_pipeline.predict_proba([cleaned_text])[0]
        nb_probs = self.nb_pipeline.predict_proba([cleaned_text])[0]

        if model_type == "nb":
            base_fake_prob = float(nb_probs[1])
            active_model = "Multinomial Naive Bayes"
        elif model_type == "lr":
            base_fake_prob = float(lr_probs[1])
            active_model = "Logistic Regression"
        else:
            base_fake_prob = float((lr_probs[1] * 0.55) + (nb_probs[1] * 0.45))
            active_model = "Ensemble Hybrid (LR + MNB)"

        # Step 4: Linguistic & Journalistic Rule Evidence Adjustment
        cues = self.extract_linguistic_cues(raw_text)
        adjusted_fake_prob = base_fake_prob

        # If strong credibility attribution markers are present (e.g. 'according to', 'spokesperson', 'study published')
        if len(cues["detected_credibility"]) > 0:
            cred_boost = len(cues["detected_credibility"]) * 0.20
            adjusted_fake_prob = max(adjusted_fake_prob - cred_boost, 0.03)

        # If strong clickbait markers or high sensationalism
        if len(cues["detected_clickbait"]) > 0:
            cb_boost = len(cues["detected_clickbait"]) * 0.25
            adjusted_fake_prob = min(adjusted_fake_prob + cb_boost, 0.98)
        elif cues["sensationalism_score"] > 40:
            adjusted_fake_prob = min(adjusted_fake_prob + 0.15, 0.95)

        # Bound probability
        adjusted_fake_prob = max(min(adjusted_fake_prob, 0.99), 0.01)

        real_prob = round((1.0 - adjusted_fake_prob) * 100, 1)
        fake_prob_pct = round(adjusted_fake_prob * 100, 1)

        is_fake = adjusted_fake_prob >= 0.5
        prediction_label = "FAKE NEWS DETECTED" if is_fake else "VERIFIED REAL NEWS"
        confidence = fake_prob_pct if is_fake else real_prob

        # Sentiment Analysis
        sentiment = self.compute_sentiment(raw_text)

        return {
            "is_gibberish": False,
            "prediction": prediction_label,
            "is_fake": is_fake,
            "confidence": confidence,
            "real_probability": real_prob,
            "fake_probability": fake_prob_pct,
            "active_model": active_model,
            "sentiment": sentiment,
            "linguistic_cues": cues,
            "token_count": len(tokens),
            "cleaned_sample": " ".join(tokens[:20]) + ("..." if len(tokens) > 20 else "")
        }
