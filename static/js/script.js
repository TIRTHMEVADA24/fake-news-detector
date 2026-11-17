// Frontend script for Fake News Detection & Sentiment Analysis

const form = document.getElementById('newsForm');
const textArea = document.getElementById('news_text');
const charCount = document.getElementById('charCount');
const loader = document.getElementById('loader');
const errorAlert = document.getElementById('errorAlert');
const resultsSection = document.getElementById('resultsSection');
const analyzeBtn = document.getElementById('analyzeBtn');

// Real-time character & word counter
textArea.addEventListener('input', updateCharCount);

function updateCharCount() {
    const text = textArea.value;
    const chars = text.length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    charCount.textContent = `${chars} characters | ${words} words`;
}

function clearText() {
    textArea.value = '';
    updateCharCount();
    resultsSection.classList.add('hidden');
    errorAlert.classList.add('hidden');
}

// 1-Click Sample Loader
async function loadSample(sampleId) {
    try {
        const res = await fetch(`/api/sample/${sampleId}`);
        const data = await res.json();
        if (data.success) {
            textArea.value = data.data.text.trim();
            updateCharCount();
            errorAlert.classList.add('hidden');
        }
    } catch (err) {
        showError("Failed to load sample: " + err.message);
    }
}

function showError(msg) {
    errorAlert.textContent = msg;
    errorAlert.classList.remove('hidden');
    loader.classList.add('hidden');
    analyzeBtn.disabled = false;
}

// Form Submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorAlert.classList.add('hidden');

    const text = textArea.value.trim();
    if (!text || text.length < 10) {
        showError("Please enter at least 10 characters of news text or choose a sample above.");
        return;
    }

    loader.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    analyzeBtn.disabled = true;

    const formData = new FormData(form);

    try {
        const res = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        const json = await res.json();

        loader.classList.add('hidden');
        analyzeBtn.disabled = false;

        if (!json.success) {
            showError(json.error || "Prediction failed.");
            return;
        }

        renderResults(json.data);
    } catch (err) {
        showError("Network error: " + err.message);
    }
});

function renderResults(data) {
    resultsSection.classList.remove('hidden');

    // Handle Gibberish / Invalid Random Inputs
    if (data.is_gibberish) {
        showError(data.error_message || "Input is unrecognized as valid text (random keyboard characters or gibberish detected). Please enter a coherent news headline or article.");
        resultsSection.classList.add('hidden');
        return;
    }

    // 1. Verdict Card Styling
    const vCard = document.getElementById('verdictCard');
    const vText = document.getElementById('verdictText');
    const vIcon = document.getElementById('verdictIcon');
    const vBadge = document.getElementById('verdictBadge');

    vCard.classList.remove('verdict-real', 'verdict-fake');
    vBadge.classList.remove('badge-real', 'badge-fake');

    if (data.is_fake) {
        vCard.classList.add('verdict-fake');
        vBadge.classList.add('badge-fake');
        vText.textContent = "FAKE NEWS DETECTED";
        vIcon.className = "fa-solid fa-triangle-exclamation";
    } else {
        vCard.classList.add('verdict-real');
        vBadge.classList.add('badge-real');
        vText.textContent = "VERIFIED REAL NEWS";
        vIcon.className = "fa-solid fa-circle-check";
    }

    document.getElementById('confidenceTag').textContent = `Confidence: ${data.confidence}%`;
    document.getElementById('realPct').textContent = `${data.real_probability}%`;
    document.getElementById('fakePct').textContent = `${data.fake_probability}%`;
    document.getElementById('realFill').style.width = `${data.real_probability}%`;
    document.getElementById('fakeFill').style.width = `${data.fake_probability}%`;

    // 2. Sentiment Analysis
    const sent = data.sentiment;
    document.getElementById('sentimentBadge').textContent = sent.sentiment_label;
    document.getElementById('polarityVal').textContent = sent.polarity.toFixed(2);
    document.getElementById('sentimentTone').textContent = sent.sentiment_label;
    document.getElementById('wordCountsSummary').textContent = `Positive Words: ${sent.positive_words_count} | Negative: ${sent.negative_words_count}`;

    // Polarity pointer (-1.0 to +1.0 maps to 0% to 100%)
    const pointerPercent = ((sent.polarity + 1.0) / 2.0) * 100;
    document.getElementById('polarityPointer').style.left = `${pointerPercent}%`;

    // 3. Subjectivity
    document.getElementById('subjectivityBadge').textContent = sent.subjectivity_label;
    document.getElementById('subjectivityScore').textContent = sent.subjectivity.toFixed(2);
    document.getElementById('subjectivityLabel').textContent = sent.subjectivity_label;
    document.getElementById('clickbaitHits').textContent = `Clickbait Triggers: ${sent.clickbait_hits}`;
    document.getElementById('subjectivityFill').style.width = `${sent.subjectivity * 100}%`;

    // 4. Stylometric Cues
    const cues = data.linguistic_cues;
    document.getElementById('uppercaseRatio').textContent = `${cues.uppercase_ratio}%`;
    document.getElementById('exclamationCount').textContent = cues.exclamation_count;
    document.getElementById('questionCount').textContent = cues.question_count;
    document.getElementById('sensationalismScore').textContent = `${cues.sensationalism_score} / 100`;

    const trigContainer = document.getElementById('triggerTags');
    trigContainer.innerHTML = '';
    
    // Display Clickbait Triggers or Credibility Attribution Markers
    let hasTags = false;
    if (cues.detected_clickbait && cues.detected_clickbait.length > 0) {
        cues.detected_clickbait.forEach(trig => {
            trigContainer.innerHTML += `<span class="tag-pill" style="background:rgba(239,68,68,0.2); color:#f87171; border:1px solid rgba(239,68,68,0.3);"><i class="fa-solid fa-flag"></i> Clickbait: "${trig}"</span>`;
            hasTags = true;
        });
    }
    if (cues.detected_credibility && cues.detected_credibility.length > 0) {
        cues.detected_credibility.forEach(cred => {
            trigContainer.innerHTML += `<span class="tag-pill" style="background:rgba(16,185,129,0.2); color:#34d399; border:1px solid rgba(16,185,129,0.3);"><i class="fa-solid fa-check"></i> Attribution: "${cred}"</span>`;
            hasTags = true;
        });
    }
    if (!hasTags) {
        trigContainer.innerHTML = '<span class="text-secondary" style="font-size:12px;">Standard vocabulary detected. No extreme clickbait or formal journalistic attribution phrases found.</span>';
    }

    // 5. Diagnostics
    document.getElementById('engineTag').textContent = `Classifier: ${data.active_model}`;
    document.getElementById('diagTokens').textContent = data.token_count;
    document.getElementById('diagSample').textContent = data.cleaned_sample;

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}
