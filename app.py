import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
import time
import json
import io
import math
import random
import struct
import wave

st.set_page_config(
    page_title="ARCHIVE - Lebanon Under Pressure",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"

def find_image(name):
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        path = IMAGE_DIR / f"{name}{ext}"
        if path.exists():
            return str(path)
    if IMAGE_DIR.exists():
        for path in IMAGE_DIR.iterdir():
            if path.is_file() and path.stem.lower() == name.lower():
                return str(path)
    return None

@st.cache_data
def make_boom_wav():
    """Create a short cinematic low-frequency boom as WAV bytes."""
    sample_rate = 44100
    duration = 1.35
    total = int(sample_rate * duration)
    rng = random.Random(1982)
    frames = bytearray()

    for i in range(total):
        t = i / sample_rate
        attack = min(1.0, t / 0.018)
        decay = math.exp(-3.4 * t)
        envelope = attack * decay

        freq = 62 - 23 * min(1.0, t / duration)
        low = math.sin(2 * math.pi * freq * t)
        sub = 0.55 * math.sin(2 * math.pi * (freq * 0.52) * t)

        noise_env = math.exp(-8.0 * t)
        noise = rng.uniform(-1.0, 1.0) * noise_env

        crack_env = math.exp(-18.0 * t)
        crack = math.sin(2 * math.pi * 145 * t) * crack_env

        sample = envelope * (0.72 * low + 0.38 * sub) + 0.28 * noise + 0.18 * crack
        sample = max(-1.0, min(1.0, sample))
        frames.extend(struct.pack('<h', int(sample * 32767)))

    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(bytes(frames))
    return buffer.getvalue()

st.markdown("""
<style>

.stApp {
    background-color: #F1F1EF;
    color: #171717;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 5rem;
}

/* Hide the boom audio control; playback is triggered by the reveal click. */
div[data-testid="stAudio"] {
    display: none !important;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: 0.22;
    background-image:
        radial-gradient(circle, rgba(23,23,23,0.055) 0.45px, transparent 0.6px),
        radial-gradient(circle, rgba(122,31,31,0.022) 0.45px, transparent 0.65px),
        repeating-linear-gradient(
            0deg,
            rgba(0,0,0,0.012) 0px,
            rgba(0,0,0,0.012) 1px,
            transparent 1px,
            transparent 4px
        );
    background-size: 8px 8px, 13px 15px, auto;
    background-position: 0 0, 4px 7px, 0 0;
}


/* Editorial two-column design notes */
.design-notes-kicker {
    margin: 2px 0 18px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #8E8E89;
    font-size: 9px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #7A1F1F;
    font-weight: 700;
}

.design-notes-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 0;
    align-items: start;
}

.design-note-col {
    min-width: 0;
    padding: 4px 30px 8px 2px;
}

.design-note-col + .design-note-col {
    border-left: 1px solid #B8B8B2;
    padding-left: 30px;
    padding-right: 2px;
}

.interaction-index {
    margin-bottom: 7px;
    font-size: 9px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #7A1F1F;
    font-weight: 700;
}

.design-note-col h4 {
    margin: 0 0 14px 0;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 24px;
    line-height: 1.15;
    font-weight: 500;
    color: #1B1B1B;
}

.design-note-col p {
    margin: 0 0 13px 0;
    font-size: 13px;
    line-height: 1.7;
    color: #444440;
}

.design-note-label {
    margin: 18px 0 6px 0;
    padding-top: 9px;
    border-top: 1px solid rgba(122,31,31,0.38);
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #7A1F1F;
    font-weight: 700;
}

.design-note-course {
    font-family: Georgia, "Times New Roman", serif;
    font-style: italic;
    color: #2F2F2C !important;
}

@media (max-width: 760px) {
    .design-notes-grid {
        grid-template-columns: 1fr;
    }
    .design-note-col {
        padding: 4px 2px 22px 2px;
    }
    .design-note-col + .design-note-col {
        border-left: 0;
        border-top: 1px solid #B8B8B2;
        padding: 24px 2px 8px 2px;
    }
}

.cover-wrap {
    position: relative;
}

.cover-wrap::before {
    content: "01";
    position: absolute;
    top: 36px;
    right: 20px;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 150px;
    color: rgba(0,0,0,0.025);
    font-weight: 700;
    z-index: 0;
}

.cover-content {
    position: relative;
    z-index: 1;
}

.top-rule {
    border-top: 3px solid #171717;
    border-bottom: 1px solid #171717;
    height: 5px;
    margin-bottom: 16px;
}

.issue-strip {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    align-items: center;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 28px;
    color: #353535;
}

.issue-left {
    text-align: left;
}

.issue-center {
    text-align: center;
}

.issue-right {
    text-align: right;
}

.archive-name {
    text-align: center;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 20px;
    letter-spacing: 9px;
    font-weight: 600;
    margin-top: 15px;
    margin-bottom: 20px;
}

.dossier {
    text-align: center;
    margin-bottom: 20px;
}

.dossier span {
    display: inline-block;
    border: 1px solid #721C1C;
    color: #721C1C;
    padding: 5px 12px 4px 12px;
    font-size: 10px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    transform: rotate(-1.5deg);
}

.main-title {
    text-align: center;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 68px;
    line-height: 1;
    font-weight: 500;
    letter-spacing: -2px;
    margin-bottom: 13px;
}

.subtitle {
    text-align: center;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 3px;
    color: #686868;
    margin-bottom: 22px;
}

.cover-deck {
    text-align: center;
    max-width: 650px;
    margin: 0 auto 28px auto;
    font-size: 13px;
    line-height: 1.6;
    letter-spacing: 0.4px;
    color: #575757;
}

.double-rule {
    max-width: 900px;
    margin: 30px auto;
    border-top: 1px solid #1E1E1E;
    border-bottom: 1px solid #1E1E1E;
    height: 4px;
}

.intro {
    max-width: 830px;
    margin: 35px auto 55px auto;
    text-align: center;
    font-family: Georgia, "Times New Roman", serif;
    font-size: 21px;
    line-height: 1.8;
    color: #323232;
}

.archive-meta {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    max-width: 900px;
    margin: 36px auto 0 auto;
    padding-top: 10px;
    border-top: 1px solid #9A9A9A;
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #777777;
}

.archive-meta div:nth-child(1) {
    text-align: left;
}

.archive-meta div:nth-child(2) {
    text-align: center;
}

.archive-meta div:nth-child(3) {
    text-align: right;
}

</style>
""", unsafe_allow_html=True)
st.html("""
<style>

/* ARCHIVAL PHOTO TREATMENT */

div[data-testid="stImage"] img {
    width: 100%;
    height: 330px;
    object-fit: cover;

    filter:
        grayscale(100%)
        contrast(1.08)
        sepia(8%);

    border-radius: 0px;
    border: 1px solid #B8B8B3;

    animation: archiveReveal 0.8s ease both;
}


/* IMAGE CAPTIONS */

div[data-testid="stCaptionContainer"] {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 10px;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #6B6B68;
    padding-top: 5px;
}


/* SUBTLE PHOTO REVEAL */

@keyframes archiveReveal {

    from {
        opacity: 0;
        transform: translateY(18px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

</style>
""")












st.html("""
<div class="cover-wrap">
    <div class="cover-content">

        <div class="top-rule"></div>

        <div class="issue-strip">
            <div class="issue-left">VOL. I - NO. 01</div>
            <div class="issue-center">BEIRUT</div>
            <div class="issue-right">SEPTEMBER 2026</div>
        </div>

        <div class="archive-name">ARCHIVE</div>

        <div class="dossier">
            <span>Special Dossier</span>
        </div>

        <div class="main-title">Lebanon Under Pressure</div>

        <div class="subtitle">
            What conflict looks like in data
        </div>

        <div class="cover-deck">
            A visual record of conflict, disruption and change -
            told through historical archives and data.
        </div>

        <div class="double-rule"></div>

        <div class="intro">
            <em>A country's history can be read in more than headlines.</em><br>
            <em>Sometimes, it appears in a falling line, a sudden spike,</em><br>
            <em>or in a pattern that only becomes clear over time.</em>
        </div>

        <div class="archive-meta">
            <div>Archive / Lebanon</div>
            <div>Issue 01</div>
            <div>Data & History</div>
        </div>

    </div>
</div>
""")
# ---------------------------------
# SECTION 01 — WAR & LIFE EXPECTANCY
# ---------------------------------

st.html("""
<style>

.section-start {
    margin-top: 110px;
    padding-top: 18px;
    border-top: 3px solid #171717;
}

.section-label {
    font-size: 10px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #777777;
    margin-bottom: 14px;
}

.section-title {
    font-family: Georgia, "Times New Roman", serif;
    font-size: 48px;
    line-height: 1.05;
    font-weight: 500;
    margin-bottom: 14px;
}

.section-copy {
    max-width: 690px;
    font-size: 15px;
    line-height: 1.7;
    color: #555555;
    margin-bottom: 38px;
}

.selector-label {
    font-size: 10px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #555555;
    margin-bottom: 8px;
}

/* Make Streamlit dropdown more editorial */
div[data-baseweb="select"] > div {
    background-color: transparent;
    border: 1px solid #6F6F6F;
    border-radius: 0px;
}

</style>

<div class="section-start">

    <div class="section-label">
        Archive 01 / War & Life Expectancy
    </div>

    <div class="section-title">
        When war enters the data.
    </div>

    <div class="section-copy">
        Three moments of conflict. Three points in Lebanon's history.
        Select one to open its archive before examining what appears in the data.
    </div>

    <div class="selector-label">
        Choose an archive to open
    </div>

</div>
""")


# ---------------------------------
# INTERACTION 1 — CHOOSE A CONFLICT
# ---------------------------------

conflicts = {
    "1976 - Civil War Escalation": 1976,
    "1982 - Lebanon War": 1982,
    "2006 - Lebanon War": 2006
}

selected_conflict = st.selectbox(
    "Choose conflict",
    list(conflicts.keys()),
    label_visibility="collapsed"
)

conflict_year = conflicts[selected_conflict]


# ---------------------------------
# INTERACTION 1 — DYNAMIC ARCHIVE TEXT
# ---------------------------------

if conflict_year == 1976:

    col1, col2 = st.columns(2, gap="large")

    with col1:
        karantina_img = find_image("karantina_1976")
        if karantina_img:
            st.image(karantina_img, use_container_width=True)
            st.caption("Karantina, 18 January 1976 | Image source: Filiu (2022)")
        else:
            st.warning("Karantina image not found in the images folder.")

    with col2:
        damour_img = find_image("damour_1976")
        if damour_img:
            st.image(damour_img, use_container_width=True)
            st.caption("Damour, 20 January 1976 | Image source: Damour Massacre (1976)")
        else:
            st.warning("Damour image not found in the images folder.")

    st.html("""
    <div style="margin-top:45px; border-top:1px solid #999; padding-top:18px;">

        <div style="
            font-size:10px;
            letter-spacing:3px;
            text-transform:uppercase;
            color:#777;
            margin-bottom:10px;">
            Beirut / January 1976 / Archive File
        </div>

        <div style="
            font-family:Georgia, 'Times New Roman', serif;
            font-size:38px;
            margin-bottom:18px;">
            1976 — Civil War Escalation
        </div>

        <div style="
            font-size:16px;
            line-height:1.8;
            max-width:800px;">
            Two massacres, two days apart, marked a rapid escalation
            of violence during the Lebanese Civil War.
            On January 18, Kataeb and PNL militias attacked
            Maslakh-Karantina. Estimates of casualties range from
            approximately 600 to 1,500, while at least 20,000 civilians
            were evacuated.
            <br><br>
            On January 20, militias associated with the Lebanese
            National Movement and the PLO attacked Damour.
            Estimates place civilian deaths between approximately
            150 and 500.
        </div>

        <div style="
            margin-top:18px;
            font-size:10px;
            letter-spacing:1px;
            color:#777;">
            SOURCE / Centre for Social Science Research & Action
        </div>

    </div>
    """)


elif conflict_year == 1982:

    img_1982 = find_image("1982")
    if img_1982:
        st.image(img_1982, use_container_width=True)
        st.caption("Lebanon, 1982 | Image source: Burke (2024)")
    else:
        st.warning("1982 image not found in the images folder.")

    st.html("""
    <div style="margin-top:45px; border-top:1px solid #999; padding-top:18px;">

        <div style="
            font-size:10px;
            letter-spacing:3px;
            text-transform:uppercase;
            color:#777;
            margin-bottom:10px;">
            Lebanon / 1982 / Archive File
        </div>

        <div style="
            font-family:Georgia, 'Times New Roman', serif;
            font-size:38px;
            margin-bottom:18px;">
            1982 — Lebanon War
        </div>

        <div style="
            font-size:16px;
            line-height:1.8;
            max-width:800px;">
            The 1982 Lebanon War followed the Israeli invasion of
            Lebanon. Israel sought to weaken the Palestine Liberation
            Organization militarily and politically and alter the balance
            of the Lebanese Civil War in favour of its allies.
            <br><br>
            Estimates place the number of Lebanese, Palestinians and
            Syrians killed — civilians and armed personnel — at roughly
            17,000 to 19,000.
        </div>

        <div style="
            margin-top:18px;
            font-size:10px;
            letter-spacing:1px;
            color:#777;">
            SOURCE / Michael Fischbach — Interactive Encyclopedia of the Palestine Question
        </div>

    </div>
    """)


elif conflict_year == 2006:

    img_2006 = find_image("2006")
    if img_2006:
        st.image(img_2006, use_container_width=True)
        st.caption("Lebanon, 2006 | Image source: Ghadir Hamadi (2023)")
    else:
        st.warning("2006 image not found in the images folder.")

    st.html("""
    <div style="margin-top:45px; border-top:1px solid #999; padding-top:18px;">

        <div style="
            font-size:10px;
            letter-spacing:3px;
            text-transform:uppercase;
            color:#777;
            margin-bottom:10px;">
            Lebanon / July-August 2006 / Archive File
        </div>

        <div style="
            font-family:Georgia, 'Times New Roman', serif;
            font-size:38px;
            margin-bottom:18px;">
            2006 — Lebanon War
        </div>

        <div style="
            font-size:16px;
            line-height:1.8;
            max-width:800px;">
            The 2006 Lebanon War was a 34-day conflict between Israel
            and Hezbollah, lasting from July 12 to August 14.
            <br><br>
            Human Rights Watch reported at least 1,109 Lebanese deaths,
            4,399 people injured and approximately one million displaced.
        </div>

        <div style="
            margin-top:18px;
            font-size:10px;
            letter-spacing:1px;
            color:#777;">
            SOURCE / Encyclopaedia Britannica & Human Rights Watch
        </div>

    </div>
    """)
# ---------------------------------
# INTERACTION 2 — PRE-CONFLICT GRAPH
# ---------------------------------

st.html("""
<div style="
    margin-top:90px;
    padding-top:18px;
    border-top:3px solid #171717;
">

    <div style="
        font-size:10px;
        letter-spacing:3px;
        text-transform:uppercase;
        color:#777777;
        margin-bottom:12px;">
        Data Plate 01 / Life Expectancy
    </div>

    <div style="
        font-family:Georgia, 'Times New Roman', serif;
        font-size:42px;
        line-height:1.1;
        margin-bottom:12px;">
        What did this look like in the data?
    </div>

    <div style="
        font-size:15px;
        color:#555555;
        margin-bottom:30px;">
        First, examine the pattern before the conflict enters the timeline.
    </div>

</div>
""")


# LOAD LIFE EXPECTANCY DATA

df = pd.read_csv(
    BASE_DIR / "a4d014e19fafac6625936d7255215a6d_20240909_180030.csv"
)

life = df[
    df["Indicator Code"].isin([
        "SP.DYN.LE00.FE.IN",
        "SP.DYN.LE00.MA.IN"
    ])
].copy()

life["Gender"] = life["Indicator Code"].replace({
    "SP.DYN.LE00.FE.IN": "Female",
    "SP.DYN.LE00.MA.IN": "Male"
})

life["refPeriod"] = pd.to_numeric(
    life["refPeriod"],
    errors="coerce"
)

life["Value"] = pd.to_numeric(
    life["Value"],
    errors="coerce"
)

life = life.dropna(
    subset=["refPeriod", "Value"]
)

life["refPeriod"] = life["refPeriod"].astype(int)


# ONLY SHOW 10 YEARS BEFORE THE CONFLICT

pre_conflict = life[
    (life["refPeriod"] >= conflict_year - 10) &
    (life["refPeriod"] < conflict_year)
]

st.html('<div id="impact-anchor" style="scroll-margin-top: 16px;"></div>')

# ---------------------------------
# REVEAL BUTTON + DRAMATIC IMPACT
# ---------------------------------

# Reset the reveal whenever the reader chooses a different conflict.
if "revealed_conflict" not in st.session_state:
    st.session_state.revealed_conflict = None

if "last_conflict_choice" not in st.session_state:
    st.session_state.last_conflict_choice = conflict_year

if st.session_state.last_conflict_choice != conflict_year:
    st.session_state.revealed_conflict = None
    st.session_state.last_conflict_choice = conflict_year

impact_names = {
    1976: "CIVIL WAR ESCALATION",
    1982: "LEBANON WAR",
    2006: "LEBANON WAR"
}

# Style the reveal button like an archival control rather than a dashboard button.
st.html("""
<style>
div.stButton > button {
    width: 100%;
    background: transparent;
    color: #6E1F1F;
    border: 1px solid #6E1F1F;
    border-radius: 0;
    padding: 0.85rem 1rem;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2.2px;
    text-transform: uppercase;
}

div.stButton > button:hover {
    background: #6E1F1F;
    color: #F1F1EF;
    border-color: #6E1F1F;
}
</style>
""")

just_revealed = False

if st.session_state.revealed_conflict != conflict_year:
    if st.button("REVEAL THE CONFLICT →", key=f"reveal_{conflict_year}"):
        st.session_state.revealed_conflict = conflict_year
        just_revealed = True
else:
    st.html(
        f"""
        <div style="
            margin: 10px 0 18px 0;
            padding: 10px 14px;
            border-top: 1px solid #6E1F1F;
            border-bottom: 1px solid #6E1F1F;
            color: #6E1F1F;
            font-size: 10px;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            text-align: center;">
            Archive opened / {conflict_year}
        </div>
        """
    )

revealed = st.session_state.revealed_conflict == conflict_year

# Play one cinematic boom exactly when the reveal is triggered.
if just_revealed:
    st.audio(
        make_boom_wav(),
        format="audio/wav",
        autoplay=True,
    )

# Keep the reveal in view. Streamlit reruns the script after a button click,
# so we explicitly scroll the parent page back to the graph anchor.
if just_revealed:
    components.html(
        """
        <script>
        (function () {
            function jumpToImpact() {
                try {
                    const parentDoc = window.parent.document;
                    const anchor = parentDoc.getElementById('impact-anchor');
                    if (anchor) {
                        anchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        return;
                    }
                    const frames = Array.from(parentDoc.querySelectorAll('iframe'));
                    const thisFrame = frames.find((frame) => frame.contentWindow === window);
                    if (thisFrame) {
                        thisFrame.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                } catch (err) {
                    // If parent access is unavailable, keep the reveal itself compact
                    // so the user is not pushed farther away from the graph.
                }
            }
            jumpToImpact();
            setTimeout(jumpToImpact, 120);
            setTimeout(jumpToImpact, 350);
        })();
        </script>
        """,
        height=0,
        scrolling=False,
    )

# Keep the same axes before and after reveal so the visual change feels like
# the historical event is entering the existing chart rather than replacing it.
full_context = life[
    (life["refPeriod"] >= conflict_year - 10) &
    (life["refPeriod"] <= conflict_year + 10)
].copy()

if full_context.empty:
    y_min, y_max = 0, 100
else:
    y_min = float(full_context["Value"].min()) - 2
    y_max = float(full_context["Value"].max()) + 2


def build_life_figure(
    chart_data,
    show_impact=False,
    pulse_size=30,
    band_opacity=0.14,
    x_jitter=0.0,
    y_jitter=0.0,
    flash=False,
):
    """Build the editorial life-expectancy chart for the current reveal stage."""

    fig = go.Figure()

    female = chart_data[chart_data["Gender"] == "Female"]
    male = chart_data[chart_data["Gender"] == "Male"]

    fig.add_trace(
        go.Scatter(
            x=female["refPeriod"],
            y=female["Value"],
            mode="lines+markers",
            name="Female",
            line=dict(width=3, color="#7A1F1F"),
            marker=dict(size=6, color="#7A1F1F"),
            hovertemplate="Female<br>%{x}: %{y:.1f} years<extra></extra>"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=male["refPeriod"],
            y=male["Value"],
            mode="lines+markers",
            name="Male",
            line=dict(width=3, color="#333333"),
            marker=dict(size=6, color="#333333"),
            hovertemplate="Male<br>%{x}: %{y:.1f} years<extra></extra>"
        )
    )

    if not show_impact:
        # A faint sealed section makes the unrevealed future feel intentionally hidden.
        fig.add_vrect(
            x0=conflict_year - 0.15,
            x1=conflict_year + 10.35,
            fillcolor="rgba(20,20,20,0.035)",
            line_width=0,
            layer="below"
        )

        fig.add_annotation(
            x=conflict_year + 5,
            y=0.5,
            xref="x",
            yref="paper",
            text="ARCHIVE SEALED",
            showarrow=False,
            textangle=-90,
            font=dict(
                family="Helvetica Neue, Arial",
                size=10,
                color="rgba(40,40,40,0.35)"
            )
        )

    if show_impact:
        # Deep-red impact band on the conflict year.
        fig.add_vrect(
            x0=conflict_year - 0.35,
            x1=conflict_year + 0.35,
            fillcolor=f"rgba(122,31,31,{band_opacity})",
            line_width=0,
            layer="below"
        )

        fig.add_vline(
            x=conflict_year,
            line_width=1.5,
            line_dash="dot",
            line_color="#7A1F1F"
        )

        fig.add_annotation(
            x=conflict_year,
            y=1.04,
            xref="x",
            yref="paper",
            text=f"<b>{conflict_year}</b><br>ARCHIVE EVENT",
            showarrow=False,
            align="center",
            font=dict(
                family="Helvetica Neue, Arial",
                size=11,
                color="#7A1F1F"
            )
        )

        # Concentric rings create the shockwave around the conflict-year points.
        for gender, ring_color in [("Female", "#7A1F1F"), ("Male", "#333333")]:
            point = full_context[
                (full_context["Gender"] == gender) &
                (full_context["refPeriod"] == conflict_year)
            ]

            if not point.empty:
                y_value = float(point.iloc[0]["Value"])

                for ring_size, opacity in [
                    (pulse_size + 52, 0.18),
                    (pulse_size + 30, 0.30),
                    (pulse_size + 12, 0.46),
                    (pulse_size, 0.68)
                ]:
                    fig.add_trace(
                        go.Scatter(
                            x=[conflict_year],
                            y=[y_value],
                            mode="markers",
                            showlegend=False,
                            hoverinfo="skip",
                            marker=dict(
                                size=ring_size,
                                color=f"rgba(0,0,0,0)",
                                line=dict(
                                    width=2,
                                    color=ring_color
                                ),
                                opacity=opacity
                            )
                        )
                    )

                fig.add_trace(
                    go.Scatter(
                        x=[conflict_year],
                        y=[y_value],
                        mode="markers",
                        showlegend=False,
                        hoverinfo="skip",
                        marker=dict(
                            size=12,
                            color=ring_color,
                            line=dict(width=2, color="#F1F1EF")
                        )
                    )
                )

    fig.update_layout(
        title=(
            f"Life Expectancy Around {conflict_year}"
            if show_impact
            else f"Life Expectancy Before {conflict_year}"
        ),
        title_x=0,
        title_font=dict(
            family="Georgia",
            size=25,
            color="#171717"
        ),
        hovermode="x unified",
        paper_bgcolor="#F1F1EF",
        plot_bgcolor=("rgba(122,31,31,0.10)" if flash else "#F1F1EF"),
        font=dict(
            family="Helvetica Neue, Arial",
            color="#222222"
        ),
        legend=dict(
            orientation="h",
            y=1.08,
            x=1,
            xanchor="right"
        ),
        xaxis_title="Year",
        yaxis_title="Life Expectancy (Years)",
        margin=dict(l=40, r=30, t=95, b=40),
        transition=dict(duration=250, easing="cubic-in-out")
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor="#888888",
        tickmode="linear",
        dtick=1,
        range=[
            conflict_year - 10.5 + x_jitter,
            conflict_year + 10.5 + x_jitter,
        ]
    )

    fig.update_yaxes(
        gridcolor="rgba(0,0,0,0.08)",
        linecolor="#888888",
        range=[y_min + y_jitter, y_max + y_jitter]
    )

    return fig


# ---------------------------------
# IMPACT SEQUENCE
# ---------------------------------

chart_slot = st.empty()

if just_revealed:
    # Keep the impact INSIDE the chart area so the page does not grow and push
    # the reader away from the moment they just triggered.
    impact_data = life[
        (life["refPeriod"] >= conflict_year - 10) &
        (life["refPeriod"] <= conflict_year)
    ].copy()

    impact_fig = build_life_figure(
        impact_data,
        show_impact=True,
        pulse_size=150,
        band_opacity=0.48,
        flash=True,
    )

    # We progressively reveal the aftermath after the initial boom.
    reveal_frames = []
    for end_year in range(conflict_year + 1, conflict_year + 11):
        frame = life[
            (life["refPeriod"] >= conflict_year - 10) &
            (life["refPeriod"] <= end_year)
        ]
        f = frame[frame["Gender"] == "Female"]
        m = frame[frame["Gender"] == "Male"]
        reveal_frames.append({
            "fx": f["refPeriod"].tolist(),
            "fy": [round(float(v), 4) for v in f["Value"].tolist()],
            "mx": m["refPeriod"].tolist(),
            "my": [round(float(v), 4) for v in m["Value"].tolist()],
        })

    frames_json = json.dumps(reveal_frames)

    post_script = f"""
    const gd = document.getElementById('{{plot_id}}');
    const frames = {frames_json};

    // Draw the aftermath forward after the impact lands.
    let frameIndex = 0;
    function revealAftermath() {{
        if (frameIndex >= frames.length) return;
        const fr = frames[frameIndex];
        Plotly.restyle(gd, {{
            x: [fr.fx, fr.mx],
            y: [fr.fy, fr.my]
        }}, [0, 1]);
        frameIndex += 1;
        setTimeout(revealAftermath, 115);
    }}

    // Let the BOOM be visible first, then let the timeline continue.
    setTimeout(revealAftermath, 1180);

    // Let the giant Plotly data-point rings settle after the first impact.
    setTimeout(() => {{
        const ringTraces = [2,3,4,5,7,8,9,10];
        ringTraces.forEach(i => {{
            try {{ Plotly.restyle(gd, {{opacity: 0.08}}, [i]); }} catch(e) {{}}
        }});
    }}, 1750);
    """

    plot_html = impact_fig.to_html(
        full_html=False,
        include_plotlyjs=True,
        config={"displayModeBar": False, "responsive": True},
        post_script=post_script,
    )

    impact_name = impact_names[conflict_year]

    dramatic_html = f"""
    <div class="boom-shell">
        <div class="boom-flash"></div>
        <div class="boom-vignette"></div>

        <div class="smoke smoke-1"></div>
        <div class="smoke smoke-2"></div>
        <div class="smoke smoke-3"></div>
        <div class="smoke smoke-4"></div>
        <div class="smoke smoke-5"></div>
        <div class="smoke smoke-6"></div>

        <div class="shockwave shockwave-1"></div>
        <div class="shockwave shockwave-2"></div>
        <div class="shockwave shockwave-3"></div>
        <div class="shockwave shockwave-4"></div>

        <div class="impact-stamp">
            <div class="impact-stamp-small">ARCHIVE EVENT</div>
            <div class="impact-stamp-year">{conflict_year}</div>
            <div class="impact-stamp-name">{impact_name}</div>
        </div>

        <div class="plot-holder">{plot_html}</div>
    </div>

    <style>
    html, body {{ margin:0; padding:0; background:#F1F1EF; overflow:hidden; }}

    .boom-shell {{
        position: relative;
        width: 100%;
        min-height: 585px;
        overflow: hidden;
        transform-origin: 50% 50%;
        animation: graphQuake 1.18s cubic-bezier(.36,.07,.19,.97) both;
        background: #F1F1EF;
    }}

    .plot-holder {{
        position: relative;
        z-index: 4;
        animation: plotHit 1.05s ease-out both;
    }}

    .boom-flash {{
        position:absolute;
        inset:0;
        z-index:9;
        pointer-events:none;
        background:
            radial-gradient(circle at 50% 48%, rgba(122,31,31,.58) 0%, rgba(122,31,31,.18) 18%, rgba(122,31,31,0) 52%),
            rgba(122,31,31,.22);
        animation: impactFlash .72s ease-out forwards;
    }}

    .boom-vignette {{
        position:absolute;
        inset:0;
        z-index:8;
        pointer-events:none;
        box-shadow: inset 0 0 120px rgba(25,8,8,.52);
        animation: vignetteHit 1.2s ease-out forwards;
    }}

    .impact-stamp {{
        position:absolute;
        left:50%;
        top:49%;
        transform:translate(-50%,-50%);
        z-index:12;
        color:#6E1F1F;
        text-align:center;
        pointer-events:none;
        text-shadow: 0 1px 0 rgba(241,241,239,.8);
        animation: stampHit 1.55s cubic-bezier(.2,.75,.25,1) forwards;
    }}
    .impact-stamp-small {{
        font: 700 10px/1 "Helvetica Neue", Arial, sans-serif;
        letter-spacing:4px;
    }}
    .impact-stamp-year {{
        margin-top:4px;
        font: 700 92px/.88 Georgia, "Times New Roman", serif;
        letter-spacing:-4px;
    }}
    .impact-stamp-name {{
        margin-top:9px;
        font: 700 11px/1 "Helvetica Neue", Arial, sans-serif;
        letter-spacing:4px;
    }}

    .shockwave {{
        position:absolute;
        z-index:10;
        left:50%;
        top:49%;
        width:42px;
        height:42px;
        margin:-21px 0 0 -21px;
        border:2px solid rgba(122,31,31,.82);
        border-radius:50%;
        pointer-events:none;
        opacity:0;
        animation: shockExpand 1.35s ease-out forwards;
    }}
    .shockwave-2 {{ animation-delay:.10s; border-width:3px; }}
    .shockwave-3 {{ animation-delay:.20s; }}
    .shockwave-4 {{ animation-delay:.30s; border-color:rgba(30,30,30,.55); }}

    .smoke {{
        position:absolute;
        z-index:7;
        pointer-events:none;
        border-radius:50%;
        filter: blur(16px);
        opacity:0;
        background: radial-gradient(circle,
            rgba(75,72,68,.42) 0%,
            rgba(95,90,85,.24) 45%,
            rgba(120,115,110,0) 72%);
        animation: smokeRise 2.55s ease-out forwards;
    }}
    .smoke-1 {{ width:230px;height:150px;left:35%;top:55%;animation-delay:.16s; }}
    .smoke-2 {{ width:260px;height:175px;left:47%;top:51%;animation-delay:.24s; }}
    .smoke-3 {{ width:190px;height:130px;left:26%;top:49%;animation-delay:.32s; }}
    .smoke-4 {{ width:210px;height:150px;left:56%;top:57%;animation-delay:.38s; }}
    .smoke-5 {{ width:150px;height:115px;left:41%;top:61%;animation-delay:.44s; }}
    .smoke-6 {{ width:175px;height:125px;left:53%;top:43%;animation-delay:.50s; }}

    @keyframes graphQuake {{
        0%   {{ transform:translate(0,0) rotate(0deg) scale(1); }}
        6%   {{ transform:translate(-18px, 8px) rotate(-1.15deg) scale(1.008); }}
        12%  {{ transform:translate(21px,-10px) rotate(1.25deg) scale(1.012); }}
        18%  {{ transform:translate(-17px,-7px) rotate(-.95deg) scale(1.008); }}
        25%  {{ transform:translate(16px, 8px) rotate(.8deg) scale(1.006); }}
        33%  {{ transform:translate(-12px, 5px) rotate(-.62deg); }}
        42%  {{ transform:translate(10px,-5px) rotate(.48deg); }}
        53%  {{ transform:translate(-7px,3px) rotate(-.32deg); }}
        66%  {{ transform:translate(5px,-2px) rotate(.20deg); }}
        80%  {{ transform:translate(-2px,1px) rotate(-.08deg); }}
        100% {{ transform:translate(0,0) rotate(0deg) scale(1); }}
    }}

    @keyframes plotHit {{
        0% {{ filter:contrast(1) brightness(1); }}
        10% {{ filter:contrast(1.7) brightness(.68); }}
        28% {{ filter:contrast(1.25) brightness(.88); }}
        100% {{ filter:contrast(1) brightness(1); }}
    }}

    @keyframes impactFlash {{
        0% {{ opacity:0; }}
        5% {{ opacity:1; }}
        16% {{ opacity:.72; }}
        34% {{ opacity:.22; }}
        100% {{ opacity:0; }}
    }}

    @keyframes vignetteHit {{
        0% {{ opacity:0; }}
        8% {{ opacity:1; }}
        55% {{ opacity:.38; }}
        100% {{ opacity:0; }}
    }}

    @keyframes shockExpand {{
        0% {{ opacity:.95; transform:scale(.18); }}
        18% {{ opacity:.9; }}
        100% {{ opacity:0; transform:scale(18); }}
    }}

    @keyframes stampHit {{
        0% {{ opacity:0; transform:translate(-50%,-50%) scale(.72); filter:blur(3px); }}
        11% {{ opacity:1; transform:translate(-50%,-50%) scale(1.17); filter:blur(0); }}
        22% {{ transform:translate(-50%,-50%) scale(.98); }}
        66% {{ opacity:1; }}
        100% {{ opacity:0; transform:translate(-50%,-50%) scale(1.03); }}
    }}

    @keyframes smokeRise {{
        0% {{ opacity:0; transform:translate(0,35px) scale(.55); }}
        16% {{ opacity:.58; }}
        58% {{ opacity:.34; }}
        100% {{ opacity:0; transform:translate(-15px,-165px) scale(1.75); }}
    }}

    @media (prefers-reduced-motion: reduce) {{
        .boom-shell,.plot-holder,.boom-flash,.boom-vignette,.impact-stamp,.shockwave,.smoke {{
            animation-duration:.01ms !important;
            animation-iteration-count:1 !important;
        }}
    }}
    </style>
    """

    # This component contains the YEAR, BOOM, SHAKE, SMOKE and the graph in ONE
    # fixed-height region, so nothing is inserted above the graph and the page
    # does not jump away from the reveal.
    components.html(dramatic_html, height=610, scrolling=False)

else:
    if revealed:
        chart_data = full_context
        final_fig = build_life_figure(
            chart_data,
            show_impact=True,
            pulse_size=30,
            band_opacity=0.14
        )
    else:
        chart_data = pre_conflict
        final_fig = build_life_figure(
            chart_data,
            show_impact=False
        )

    chart_slot.plotly_chart(
        final_fig,
        use_container_width=True,
        config={"displayModeBar": False},
        key=f"life_chart_{conflict_year}_{revealed}"
    )


# ---------------------------------
# WHY THESE INTERACTIONS?
# ---------------------------------

# Editorial insight — Archive 01
st.html("""
<div style="margin:28px 0 18px 0; padding:20px 24px; border-top:1px solid #7A1F1F; border-bottom:1px solid #A8A8A4; position:relative;">
    <div style="font-size:9px; letter-spacing:3px; text-transform:uppercase; color:#7A1F1F; margin-bottom:8px;">Field Note 01 / What the archive reveals</div>
    <div style="font-family:Georgia, 'Times New Roman', serif; font-size:21px; line-height:1.45; color:#252525; font-style:italic; max-width:860px;">
        <strong>When Lebanon breaks, its people feel it in their lifespans.</strong> The sharpest collapses in life expectancy line up precisely with the country’s darkest years, 1976 and 1982, where the lines plunge like scars on the timeline.
    </div>
</div>
""")

with st.expander("Why these interactions?"):
    st.html("""
<div class="design-notes-kicker">Design Notes / Why these interactions</div>
<div class="design-notes-grid">
    <section class="design-note-col">
        <div class="interaction-index">Interaction 01</div>
        <h4>Choose a conflict</h4>
        <p>A dropdown lets the reader step into one moment of Lebanon’s history. Picking a conflict instantly reshapes the entire visualization: new photographs, new historical context, new sources and a new highlighted year. Rather than searching across every year, the reader chooses from a handful of defining events. It turns a broad timeline into a single focused story, giving the reader the context needed to understand the data before analyzing it.</p>
        <p>I chose a drop-down rather than a year slider because it lets readers choose one of three defining conflicts and see the archive update around that moment, rather than exploring every year in the dataset.</p>
        <div class="design-note-label">Why this widget</div>
        <p>The story centers on three specific events, not on browsing every year. A dropdown makes those choices easy to scan and keeps the reader focused on the history that matters.</p>
        <div class="design-note-label">Course concept</div>
        <p class="design-note-course">It provides <strong>context</strong> and helps <strong>focus attention</strong> on meaningful moments in the time series.</p>
    </section>

    <section class="design-note-col">
        <div class="interaction-index">Interaction 02</div>
        <h4>Reveal the Conflict</h4>
        <p>After a conflict is selected, the chart pauses at the years leading up to it. Clicking <strong>“Reveal the Conflict”</strong> brings the event and its aftermath into view, letting readers take in the build-up before seeing the break in the pattern. The reveal is tied to the selected conflict, so each choice opens a different chapter in Lebanon’s history.</p>
        <div class="design-note-label">Why this widget</div>
        <p>The button makes the reveal feel intentional. It gives readers a moment to notice the lead-up before seeing how the pattern changes.</p>
        <div class="design-note-label">Course concept</div>
        <p class="design-note-course">It <strong>reduces clutter</strong> and helps <strong>focus attention</strong> on the moment of impact.</p>
    </section>
</div>
    """)

# ---------------------------------
# ARCHIVE 02 — ECONOMIC PRESSURE
# ---------------------------------

st.html("""
<div style="
    margin-top:120px;
    padding-top:18px;
    border-top:3px solid #171717;
">

    <div style="
        font-size:10px;
        letter-spacing:3px;
        text-transform:uppercase;
        color:#777777;
        margin-bottom:14px;">
        Archive 02 / Economic Pressure
    </div>

    <div style="
        font-family:Georgia, 'Times New Roman', serif;
        font-size:48px;
        line-height:1.05;
        font-weight:500;
        margin-bottom:18px;">
        When one crisis becomes many.
    </div>

    <div style="
        max-width:790px;
        font-size:16px;
        line-height:1.8;
        color:#555555;
        margin-bottom:45px;">
        By 2019, Lebanon was sliding into one of the most severe economic and financial crises in its history,
        and in 2020 the COVID-19 pandemic compounded the shock. This archive traces how two indicators,
        female unemployment and the refugee population, moved through those years of mounting pressure,
        revealing how ordinary lives absorb a country’s collapse.
    </div>

</div>
""")

# ---------------------------------
# VISUALIZATION 02 — FEMALE UNEMPLOYMENT VS REFUGEE POPULATION
# ---------------------------------

female_unemployment = df[
    df["Indicator Code"] == "SL.UEM.TOTL.FE.ZS"
][["refPeriod", "Value"]].copy()

female_unemployment = female_unemployment.rename(
    columns={"Value": "Female Unemployment"}
)

refugees = df[
    df["Indicator Code"] == "SM.POP.REFG"
][["refPeriod", "Value"]].copy()

refugees = refugees.rename(
    columns={"Value": "Refugee Population"}
)

female_unemployment["refPeriod"] = pd.to_numeric(
    female_unemployment["refPeriod"], errors="coerce"
)
female_unemployment["Female Unemployment"] = pd.to_numeric(
    female_unemployment["Female Unemployment"], errors="coerce"
)
refugees["refPeriod"] = pd.to_numeric(
    refugees["refPeriod"], errors="coerce"
)
refugees["Refugee Population"] = pd.to_numeric(
    refugees["Refugee Population"], errors="coerce"
)

pressure = pd.merge(
    female_unemployment,
    refugees,
    on="refPeriod",
    how="inner"
).dropna().sort_values("refPeriod")

pressure["refPeriod"] = pressure["refPeriod"].astype(int)

# Keep the interaction and chart together so the effect is visible immediately.
st.html('<div id="pressure-anchor" style="scroll-margin-top: 18px;"></div>')

# ---------------------------------
# INTERACTION 1 — CHOOSE A CRISIS YEAR
# ---------------------------------

st.html("""
<div style="
    margin-top:30px;
    margin-bottom:10px;
    font-size:10px;
    letter-spacing:2.5px;
    text-transform:uppercase;
    color:#555555;">
    Choose a crisis year
</div>
""")

crisis_moments = {
    "2019 — Economic collapse": 2019,
    "2020 — COVID-19 compounds the crisis": 2020,
    "2021 — Continued pressure": 2021,
}

selected_pressure_event = st.selectbox(
    "Choose crisis year",
    list(crisis_moments.keys()),
    label_visibility="collapsed",
    key="pressure_event",
)

pressure_year = crisis_moments[selected_pressure_event]

# ---------------------------------
# INTERACTION 2 — TRACE THE PRESSURE
# ---------------------------------

st.html("""
<div style="
    margin-top:18px;
    margin-bottom:10px;
    font-size:10px;
    letter-spacing:2.5px;
    text-transform:uppercase;
    color:#555555;">
    Trace the pressure
</div>
""")

trace_choice = st.selectbox(
    "Trace the pressure",
    ["2 years before", "4 years before", "Full lead-up"],
    label_visibility="collapsed",
    key="pressure_trace",
)

# Track interaction changes so the graph is brought back into view immediately.
if "pressure_interactions_ready" not in st.session_state:
    st.session_state.pressure_interactions_ready = True
    st.session_state.last_pressure_year = pressure_year
    st.session_state.last_trace_choice = trace_choice
    pressure_changed = False
else:
    pressure_changed = (
        st.session_state.last_pressure_year != pressure_year
        or st.session_state.last_trace_choice != trace_choice
    )
    st.session_state.last_pressure_year = pressure_year
    st.session_state.last_trace_choice = trace_choice

if pressure_changed:
    components.html(
        """
        <script>
        (function () {
            function returnToPressureGraph() {
                try {
                    const parentDoc = window.parent.document;
                    const anchor = parentDoc.getElementById('pressure-anchor');
                    if (anchor) {
                        anchor.scrollIntoView({behavior: 'smooth', block: 'start'});
                    }
                } catch (err) {}
            }
            returnToPressureGraph();
            setTimeout(returnToPressureGraph, 120);
            setTimeout(returnToPressureGraph, 320);
        })();
        </script>
        """,
        height=0,
        scrolling=False,
    )

# Choose how much of the build-up is shown.
if trace_choice == "2 years before":
    start_year = pressure_year - 2
elif trace_choice == "4 years before":
    start_year = pressure_year - 4
else:
    start_year = int(pressure["refPeriod"].min())

trace_data = pressure[
    (pressure["refPeriod"] >= start_year)
    & (pressure["refPeriod"] <= pressure_year)
].copy()

selected_point = pressure[pressure["refPeriod"] == pressure_year]

# Fix the axes across all selections so the movement in the data is comparable.
x_min = float(pressure["Refugee Population"].min())
x_max = float(pressure["Refugee Population"].max())
y_min = float(pressure["Female Unemployment"].min())
y_max = float(pressure["Female Unemployment"].max())

x_pad = max((x_max - x_min) * 0.07, 1)
y_pad = max((y_max - y_min) * 0.10, 0.5)

# ---------------------------------
# BUILD THE LINKED SCATTERPLOT
# ---------------------------------

fig_pressure = go.Figure()

fig_pressure.add_trace(
    go.Scatter(
        x=trace_data["Refugee Population"],
        y=trace_data["Female Unemployment"],
        mode="lines+markers",
        customdata=trace_data["refPeriod"],
        line=dict(
            color="rgba(70,70,70,0.45)",
            width=2,
        ),
        marker=dict(
            size=14,
            color=trace_data["refPeriod"],
            colorscale=[
                [0.0, "#BDBDB8"],
                [0.65, "#777777"],
                [1.0, "#7A1F1F"],
            ],
            line=dict(color="#F1F1EF", width=1.5),
        ),
        hovertemplate=(
            "<b>%{customdata}</b><br>"
            "Refugee Population: %{x:,.0f}<br>"
            "Female Unemployment: %{y:.1f}%"
            "<extra></extra>"
        ),
        showlegend=False,
    )
)

if not selected_point.empty:
    crisis_x = float(selected_point.iloc[0]["Refugee Population"])
    crisis_y = float(selected_point.iloc[0]["Female Unemployment"])

    fig_pressure.add_trace(
        go.Scatter(
            x=[crisis_x],
            y=[crisis_y],
            mode="markers+text",
            text=[str(pressure_year)],
            textposition="top center",
            marker=dict(
                size=28,
                color="#7A1F1F",
                line=dict(color="#F1F1EF", width=3),
            ),
            textfont=dict(
                family="Georgia",
                size=16,
                color="#7A1F1F",
            ),
            hovertemplate=(
                f"<b>{pressure_year}</b><br>"
                "Refugee Population: %{x:,.0f}<br>"
                "Female Unemployment: %{y:.1f}%"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

fig_pressure.update_layout(
    title=f"Pressure Trajectory Into {pressure_year}",
    title_x=0,
    title_font=dict(
        family="Georgia",
        size=25,
        color="#171717",
    ),
    paper_bgcolor="#F1F1EF",
    plot_bgcolor="#F1F1EF",
    font=dict(
        family="Helvetica Neue, Arial",
        color="#222222",
    ),
    xaxis_title="Refugee Population",
    yaxis_title="Female Unemployment Rate (%)",
    margin=dict(l=55, r=35, t=90, b=55),
    hovermode="closest",
)

fig_pressure.update_xaxes(
    showgrid=False,
    linecolor="#888888",
    tickformat=",",
    range=[x_min - x_pad, x_max + x_pad],
)

fig_pressure.update_yaxes(
    gridcolor="rgba(0,0,0,0.08)",
    linecolor="#888888",
    range=[y_min - y_pad, y_max + y_pad],
)

# ---------------------------------
# DIRECT VISUAL EFFECT OVER THE GRAPH
# ---------------------------------

plot_html = fig_pressure.to_html(
    full_html=False,
    include_plotlyjs=True,
    config={"displayModeBar": False, "responsive": True},
)

if pressure_year == 2019:
    effect_markup = """
        <div class="a2-fx-layer">
            <span class="bill b1">💵</span><span class="bill b2">💵</span>
            <span class="bill b3">💵</span><span class="bill b4">💵</span>
            <span class="bill b5">💵</span><span class="bill b6">💵</span>
            <span class="bill b7">💵</span><span class="bill b8">💵</span>
            <span class="bill b9">💵</span><span class="bill b10">💵</span>
        </div>
    """
elif pressure_year == 2020:
    effect_markup = """
        <div class="a2-fx-layer">
            <span class="virus v1">🦠</span><span class="virus v2">🦠</span>
            <span class="virus v3">🦠</span><span class="virus v4">🦠</span>
            <span class="virus v5">🦠</span><span class="virus v6">🦠</span>
            <span class="virus v7">🦠</span><span class="virus v8">🦠</span>
            <span class="virus v9">🦠</span><span class="virus v10">🦠</span>
        </div>
    """
else:
    effect_markup = """
        <div class="a2-fx-layer smoke-layer">
            <div class="haze h1"></div>
            <div class="haze h2"></div>
            <div class="haze h3"></div>
            <div class="haze h4"></div>
            <div class="haze h5"></div>
        </div>
    """

crisis_label = {
    2019: "THE COLLAPSE BEGINS",
    2020: "ANOTHER SHOCK ARRIVES",
    2021: "THE PRESSURE LINGERS",
}[pressure_year]

pressure_html = f"""
<div class="a2-shell">
    {effect_markup}
    <div class="a2-event-stamp">
        <span>{pressure_year}</span>
        <small>{crisis_label}</small>
    </div>
    <div class="a2-plot">{plot_html}</div>
</div>

<style>
html, body {{
    margin:0;
    padding:0;
    background:#F1F1EF;
    overflow:hidden;
}}

.a2-shell {{
    position:relative;
    width:100%;
    min-height:565px;
    overflow:hidden;
    background:#F1F1EF;
}}

.a2-plot {{
    position:relative;
    z-index:2;
}}

.a2-fx-layer {{
    position:absolute;
    inset:0;
    z-index:7;
    pointer-events:none;
    overflow:hidden;
}}

.a2-event-stamp {{
    position:absolute;
    top:18px;
    right:20px;
    z-index:8;
    text-align:right;
    color:#7A1F1F;
    pointer-events:none;
    opacity:0;
    animation:a2Stamp 2.1s ease-out forwards;
}}

.a2-event-stamp span {{
    display:block;
    font:600 31px/1 Georgia, 'Times New Roman', serif;
}}

.a2-event-stamp small {{
    display:block;
    margin-top:5px;
    font:600 9px/1 'Helvetica Neue', Arial, sans-serif;
    letter-spacing:2.2px;
}}

@keyframes a2Stamp {{
    0% {{ opacity:0; transform:translateY(-8px); }}
    18% {{ opacity:1; transform:translateY(0); }}
    72% {{ opacity:1; }}
    100% {{ opacity:.55; }}
}}

.bill, .virus {{
    position:absolute;
    top:-62px;
    opacity:0;
    user-select:none;
}}

.bill {{
    font-size:34px;
    animation:a2BillFall 3.4s linear forwards;
}}

.virus {{
    font-size:31px;
    animation:a2VirusFall 3.7s ease-in forwards;
}}

@keyframes a2BillFall {{
    0% {{ transform:translateY(-20px) rotate(-8deg); opacity:0; }}
    8% {{ opacity:.96; }}
    100% {{ transform:translateY(620px) rotate(285deg); opacity:0; }}
}}

@keyframes a2VirusFall {{
    0% {{ transform:translateY(-20px) rotate(0deg) scale(.78); opacity:0; }}
    8% {{ opacity:.92; }}
    100% {{ transform:translateY(620px) rotate(310deg) scale(1.16); opacity:0; }}
}}

.b1,.v1 {{ left:5%; animation-delay:0s; }}
.b2,.v2 {{ left:15%; animation-delay:.28s; }}
.b3,.v3 {{ left:27%; animation-delay:.08s; }}
.b4,.v4 {{ left:38%; animation-delay:.50s; }}
.b5,.v5 {{ left:49%; animation-delay:.20s; }}
.b6,.v6 {{ left:60%; animation-delay:.64s; }}
.b7,.v7 {{ left:70%; animation-delay:.12s; }}
.b8,.v8 {{ left:80%; animation-delay:.42s; }}
.b9,.v9 {{ left:89%; animation-delay:.72s; }}
.b10,.v10 {{ left:95%; animation-delay:.34s; }}

.smoke-layer {{
    z-index:6;
}}

.haze {{
    position:absolute;
    bottom:-110px;
    width:310px;
    height:170px;
    border-radius:50%;
    filter:blur(22px);
    opacity:0;
    background:radial-gradient(
        ellipse at center,
        rgba(65,65,65,.34) 0%,
        rgba(95,95,95,.19) 40%,
        rgba(130,130,130,.05) 68%,
        transparent 78%
    );
    animation:a2HazeRise 4.5s ease-out forwards;
}}

.h1 {{ left:-4%; animation-delay:0s; }}
.h2 {{ left:20%; animation-delay:.25s; }}
.h3 {{ left:43%; animation-delay:.52s; }}
.h4 {{ left:66%; animation-delay:.18s; }}
.h5 {{ right:-8%; animation-delay:.70s; }}

@keyframes a2HazeRise {{
    0% {{ transform:translateY(70px) scale(.72); opacity:0; }}
    20% {{ opacity:.62; }}
    68% {{ opacity:.38; }}
    100% {{ transform:translateY(-250px) scale(1.55); opacity:0; }}
}}

@media (prefers-reduced-motion: reduce) {{
    .bill,.virus,.haze,.a2-event-stamp {{
        animation-duration:.01ms !important;
        animation-iteration-count:1 !important;
    }}
}}
</style>
"""

components.html(
    pressure_html,
    height=585,
    scrolling=False,
)

st.html("""
<div style="
    margin-top:8px;
    padding-top:12px;
    border-top:1px solid #A8A8A4;
    font-size:11px;
    line-height:1.6;
    color:#6A6A67;">
    <strong>Note:</strong> Refugee population refers to the total refugee population,
    while unemployment refers specifically to women. The visualization shows how the
    two indicators moved over time and does not imply that one caused the other.
</div>
""")

# ---------------------------------
# WHY THESE INTERACTIONS?
# ---------------------------------

# Editorial insight — Archive 02
st.html("""
<div style="margin:28px 0 18px 0; padding:20px 24px; border-top:1px solid #7A1F1F; border-bottom:1px solid #A8A8A4; position:relative;">
    <div style="font-size:9px; letter-spacing:3px; text-transform:uppercase; color:#7A1F1F; margin-bottom:8px;">Field Note 02 / What the pattern leaves unanswered</div>
    <div style="font-family:Georgia, 'Times New Roman', serif; font-size:21px; line-height:1.45; color:#252525; font-style:italic; max-width:860px;">
        <strong>The later crisis tells a quieter story.</strong> Through 2019–2020, female unemployment climbs and the refugee population shifts as economic pressure increases, but the chart only shows them moving together, not one causing the other. The pattern invites the question; the data alone cannot answer it.
    </div>
</div>
""")

with st.expander("Why these interactions?", expanded=False):
    st.html("""
<div class="design-notes-kicker">Design Notes / Why these interactions</div>
<div class="design-notes-grid">
    <section class="design-note-col">
        <div class="interaction-index">Interaction 01</div>
        <h4>Choose a crisis year</h4>
        <p>Use the dropdown to choose 2019, 2020, or 2021. Each year shows a different stage of Lebanon’s economic crisis. This scatterplot focuses on the year you choose, with a matching visual: falling dollar bills for 2019, green virus particles for 2020, and smoke or haze for 2021. This makes it easier to focus on one moment at a time. The interaction adds context and draws attention to the selected year.</p>
        <p>A dropdown lets readers select one of the three crisis years and anchors the visualization to that moment.</p>
        <div class="design-note-label">Why this widget</div>
        <p>Only three years are central to the story, which avoids offering a slider that suggests every date is equally important.</p>
        <div class="design-note-label">Course concept</div>
        <p class="design-note-course">It adds <strong>context</strong> and helps <strong>focus attention</strong> on one meaningful crisis moment at a time.</p>
    </section>

    <section class="design-note-col">
        <div class="interaction-index">Interaction 02</div>
        <h4>Trace the Pressure</h4>
        <p>After choosing a crisis year, the reader can decide how much of the period leading up to see, for example, two years before, four years before, or the full period. The data points connect in chronological order, making it easier to follow how female unemployment and the refugee population changed as Lebanon approached that crisis moment. This interaction is linked to the first one because the time window changes depending on which crisis year has been selected.</p>
        <div class="design-note-label">Why this widget</div>
        <p>Fixed windows make the comparison clear: readers can see how the build-up looks over different spans of time. The control also depends on the selected year, keeping the interaction focused on that event.</p>
        <div class="design-note-label">Course concept</div>
        <p class="design-note-course">It <strong>reduces clutter</strong> and uses <strong>progressive disclosure</strong> by showing only the amount of historical context the reader chooses.</p>
    </section>
</div>
    """)

