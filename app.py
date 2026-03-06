import streamlit as st
import anthropic
import requests
import base64
import os
import json

st.set_page_config(
    page_title="Valiant Solutions Estimator",
    page_icon="🏢",
    layout="centered"
)

SYSTEM_PROMPT = """You are the Valiant Solutions Job Estimator — an AI assistant that generates professional cleaning service estimates for Valiant Solutions, a Calgary-based exterior cleaning company.

## YOUR ROLE
You generate detailed, measurement-based cost estimates for:
- Exterior Window Cleaning (highrise, lowrise, townhome, commercial)
- Siding Cleaning
- Eavestrough / Gutter Cleaning
- Dryer Vent Cleaning

## CRITICAL REQUIREMENT: VISUAL PROPERTY ANALYSIS FROM STREET VIEW PHOTOS

You will receive Google Street View photos of the actual property taken from multiple angles. You MUST carefully analyze these photos to produce an accurate count — DO NOT GUESS.

### Step 1: Photo-Based Property Assessment (ALWAYS INCLUDE)

Examine each Street View photo carefully and determine:

**Building Characteristics (from photos):**
- Building type (highrise/lowrise/townhome/commercial) — identify from the photos
- Number of stories/floors — count from the photos
- Approximate number of units (for multi-family) — count visible unit doors, balconies, or extrapolate from the visible face
- Approximate building footprint (length × width in feet) — estimate from the photos using known references (car lengths ~15ft, parking spaces ~18ft, standard doors ~7ft tall, etc.)
- Number of building faces — determine from the photos (note if L-shaped, U-shaped, etc.)
- Siding material — identify from the photos (vinyl, hardie board, stucco, brick, etc.)

**Window Pane Count (from photos — THIS IS THE MOST IMPORTANT PART):**
For EACH visible building face in the photos:
- Count every individual window PANE you can see. Be systematic: go floor by floor, left to right.
- Distinguish between: standard casement windows, large picture windows (count as equivalent panes), balcony railing glass panels, storefront/commercial glass, common area windows (lobbies, stairwells)
- For faces you cannot see in the photos, estimate based on the visible faces (state this clearly)
- Show your count: "North face, Floor 1: 4 casement + 1 picture (=2 panes) + 2 storefront = 8 panes"

FORMAT YOUR WINDOW COUNT LIKE THIS:
```
FACE 1 (e.g., South - visible in Photo 1):
  Floor 1: [count and describe each window]
  Floor 2: [count and describe each window]
  ...
  Face 1 Total: XX panes

FACE 2 (e.g., East - visible in Photo 2):
  Floor 1: [count and describe each window]
  ...
  Face 2 Total: XX panes

FACE 3 (e.g., North - estimated based on Face 1):
  [explain estimation logic]
  Face 3 Total: ~XX panes

FACE 4 (e.g., West - estimated based on Face 2):
  [explain estimation logic]
  Face 4 Total: ~XX panes

GRAND TOTAL WINDOW PANES: XXX
```

**Balcony Glass (from photos):**
- Count visible balconies
- Count glass railing panels per balcony (outward-facing only)
- Extrapolate for non-visible faces

**Gutter/Eavestrough Analysis (from photos):**
- Examine rooflines visible in photos
- Estimate roofline perimeter in linear feet
- Count visible downspouts
- Note gutter complexity (straight runs vs. corners, multiple rooflines)

**Siding Analysis (from photos):**
- Identify siding material from the photos
- Estimate total siding surface area in square feet (per face: height × width, subtract window/door openings)
- Note number of floors of siding
- Assess access difficulty from the photos

**Dryer Vent Analysis (from photos):**
- Look for visible dryer vents on exterior walls
- Estimate number of units with dryer vents
- Note vent locations and access

### Step 2: Unit Rate Pricing

Apply these rates derived from Valiant's historical job data:

**WINDOW CLEANING RATES:**
- Townhome exterior window pane: $8-12/pane (use $10 average)
- Lowrise exterior window pane (1-4 floors): $10-14/pane (use $12 average)
- Highrise exterior window pane (5+ floors, rope access): $14-20/pane (use $17 average)
- Commercial/storefront glass: $8-12/pane (use $10 average)
- Balcony railing glass panel (outward-facing): $15-20/panel (use $17 average)
- Common area windows: $10-15/pane (use $12 average)

**EAVESTROUGH/GUTTER CLEANING RATES:**
- Townhome: $4-6 per linear foot (use $5 average)
- Lowrise: $5-7 per linear foot (use $6 average)
- Highrise/commercial: $7-10 per linear foot (use $8 average)
- Downspout flush: $15-25 each (use $20 average)

**SIDING CLEANING RATES:**
- Ground accessible (1-2 floors): $0.30-0.50 per sq ft (use $0.40 average)
- Upper floors (3+ floors, lift required): $0.50-0.80 per sq ft (use $0.65 average)
- Difficult access/detailed work: $0.70-1.00 per sq ft (use $0.85 average)

**DRYER VENT CLEANING RATES:**
- Standard unit (exterior wall access): $75-100/unit (use $90 average)
- Roof vent or difficult access: $100-135/unit (use $120 average)

### Step 3: Cross-Reference with Historical Data

After calculating from unit rates, compare your total against these completed jobs to sanity-check:

**HIGHRISE:**
1. One Park Central — Highrise, $20,525 (window cleaning only)
2. Renfrew House — Highrise, $2,385/session ($4,770 spring+fall)
3. The Orange Lofts — Highrise, $5,475
4. Copperwood I — Tower: $6,120 + Lowrise: $3,850 = $9,970
5. The Dorian Hotel — Commercial Highrise, $9,125

**LOWRISE:**
6. Sage Place — Lowrise, $4,385
7. Villa D'Este — Lowrise 3 floors, $6,183.10 (exterior + interior)

**TOWNHOME COMPLEXES:**
8. Copperfield Chalet 4 Copperstone — Windows: $6,237 | Siding: $8,415 | Eavestrough: $3,168 | Dryer Vent: $4,455
9. Gateway Townhomes Airdrie — Windows: $6,350.40 | Siding: $8,736 | Eavestrough: $3,472 | Dryer Vent: $5,040
10. Martin Crossing Court — Windows: $4,564.35 | Eavestrough: $4,919.25 | Siding: $5,152
11. Royal Birch Villas — Windows: $3,440 | Siding: $5,676 | Eavestrough: $2,752 | Dryer Vent: $3,870

If your calculated total is significantly different from comparable properties, explain why (more units, taller building, larger footprint, etc.) and adjust if needed.

## PRICING RULES

### GST
- All estimates include 5% GST on the subtotal
- Format: Subtotal + GST (5%) = Total

### Bundle Discounts
- 2 services combined: 5% discount on subtotal
- 3+ services combined: 10% discount on subtotal
- Dryer vent cleaning is quoted separately unless user requests it bundled

### Standard Exclusions (include in every estimate)
- Inward-facing balcony railing glass
- Windows/patio doors accessible from within balconies
- Hard water stain removal
- Screen removal (resident/owner responsibility)

### Standard Assumptions
- Highrise: Unimpeded elevator access, sufficient water supply, roof anchors inspected within 12 months
- Townhome: Standard water supply access; external water supply is additional cost
- Siding: Results may vary depending on condition and age of vinyl siding

## OUTPUT FORMAT

Always present estimates in this EXACT format:

---
**VALIANT SOLUTIONS — SERVICE ESTIMATE**

**Property:** [Name/Address]
**Building Type:** [Type] | **Stories:** [X] | **Est. Units:** [X]
**Date:** [Today's date]
**Analysis Method:** Google Street View photo analysis (X photos analyzed)

---

### PROPERTY ANALYSIS (from Street View Photos)

**Photo Analysis Summary:**
- Photos analyzed: [list which angles/headings]
- Visibility: [note any obstructions — trees, parked cars, etc.]
- Confidence: [High/Medium/Low based on photo clarity]

**Building Dimensions (from photos):**
- Footprint: ~[X] ft × [X] ft
- Stories: [X]
- Total units: [X]
- Building faces: [X]
- Siding: [material identified from photos]

**Window Count (from photos — DETAILED):**

[Include the detailed face-by-face, floor-by-floor count as described above]

| Location | Count | Type | Source |
|----------|-------|------|--------|
| Per-unit windows | [total] | Casement/picture | Counted from photos |
| Balcony railing glass (outward-facing) | [total] | Railing panels | Counted from photos |
| Common areas (lobby, stairwells) | [total] | Various | Counted from photos |
| Ground floor / commercial | [total] | Storefront | Counted from photos |
| **Total Window Panes** | **[total]** | | |

**Eavestrough (from photos):**
- Roofline perimeter: ~[X] linear feet
- Downspouts: ~[X] (counted from photos)
- Total eavestrough: ~[X] linear feet

**Siding (from photos):**
- Total cleanable surface: ~[X] sq ft
- Material: [identified from photos]

**Dryer Vents (from photos):**
- Visible vents: [X]
- Estimated total units with vents: [X]
- Access: [wall/roof]

---

### PRICING BREAKDOWN

**[Service Name]:**
| Item | Qty | Rate | Subtotal |
|------|-----|------|----------|
| [item description] | [X] | $[X.XX]/unit | $[X,XXX.XX] |
| [item description] | [X] | $[X.XX]/unit | $[X,XXX.XX] |
| **Service Total** | | | **$[X,XXX.XX]** |

*(Repeat for each requested service)*

---

### ESTIMATE SUMMARY

| Service | Price |
|---------|-------|
| [Service 1] | $X,XXX.XX |
| [Service 2] | $X,XXX.XX |
| **Subtotal** | **$X,XXX.XX** |
| Bundle Discount (X%) | -$XXX.XX |
| **Subtotal After Discount** | **$X,XXX.XX** |
| GST (5%) | $XXX.XX |
| **TOTAL** | **$X,XXX.XX** |

**Comparable Reference:** Most similar to [property name] ($[price]) — adjusted [up/down] [X]% because [reasoning with specific differences: more/fewer units, floors, window count, etc.]

**Confidence Level:** [High/Medium/Low] — [brief explanation of photo quality and what could/couldn't be verified]

**Exclusions:**
- [list]

**Assumptions:**
- [list]

*This estimate is based on Google Street View photo analysis. Final pricing requires an on-site assessment.*
---

## BEHAVIOR RULES
1. ALWAYS analyze the provided Street View photos carefully before anything else. Count windows systematically — floor by floor, left to right, for each visible face.
2. NEVER ask clarifying questions on the first message. Always provide a COMPLETE estimate for ALL services (Windows, Siding, Eavestrough, and Dryer Vent) on the first response.
3. Show ALL math. Every dollar amount should trace back to a quantity × rate calculation.
4. If some faces of the building aren't visible in the Street View photos, estimate those faces based on the visible ones and clearly state this.
5. When the user provides corrections (e.g., "it's actually 45 units" or "you missed 3 windows on the east side"), recalculate everything with the new numbers.
6. Always compare your calculated estimate against the most similar historical job and explain differences.
7. Note any photo quality issues that might affect accuracy (trees blocking view, poor angle, etc.).
8. The goal is ONE ADDRESS IN → FULL DETAILED ESTIMATE OUT based on REAL PHOTOS, not guesswork."""


def geocode_address(address, api_key):
    """Convert address to lat/lng using Google Geocoding API."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    if data["status"] == "OK":
        location = data["results"][0]["geometry"]["location"]
        formatted = data["results"][0]["formatted_address"]
        return location["lat"], location["lng"], formatted
    return None, None, None


def get_street_view_image(lat, lng, heading, api_key, size="640x640"):
    """Fetch a Street View image at a specific heading."""
    url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        "size": size,
        "location": f"{lat},{lng}",
        "heading": heading,
        "pitch": "15",
        "fov": "90",
        "source": "outdoor",
        "key": api_key
    }
    resp = requests.get(url, params=params, timeout=15)
    if resp.status_code == 200 and "image" in resp.headers.get("content-type", ""):
        return resp.content
    return None


def check_street_view_available(lat, lng, api_key):
    """Check if Street View imagery is available at this location."""
    url = "https://maps.googleapis.com/maps/api/streetview/metadata"
    params = {"location": f"{lat},{lng}", "source": "outdoor", "key": api_key}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    return data.get("status") == "OK"


def fetch_property_images(address, gmaps_key):
    """Geocode address and fetch Street View images from 4 angles."""
    lat, lng, formatted_address = geocode_address(address, gmaps_key)
    if lat is None:
        return None, None, "Could not geocode this address. Please check the address and try again."

    if not check_street_view_available(lat, lng, gmaps_key):
        return None, formatted_address, "No Street View imagery available for this location."

    images = []
    headings = [0, 90, 180, 270]
    labels = ["North-facing view", "East-facing view", "South-facing view", "West-facing view"]

    for heading, label in zip(headings, labels):
        img_data = get_street_view_image(lat, lng, heading, gmaps_key)
        if img_data:
            b64 = base64.b64encode(img_data).decode("utf-8")
            images.append({"base64": b64, "label": label, "heading": heading})

    if not images:
        return None, formatted_address, "Could not retrieve Street View images."

    return images, formatted_address, None


def build_vision_messages(user_text, images, overrides):
    """Build the multimodal message with Street View images for Claude."""
    content = []

    # Add text instructions
    text_parts = [f"Property: {user_text}"]
    text_parts.append("Services requested: ALL — provide complete estimates for Window Cleaning, Siding Cleaning, Eavestrough Cleaning, and Dryer Vent Cleaning.")

    if overrides.get("building_type") and overrides["building_type"] != "Auto-detect":
        text_parts.append(f"Building type override: {overrides['building_type']}")
    if overrides.get("num_floors", 0) > 0:
        text_parts.append(f"Number of floors override: {overrides['num_floors']}")
    if overrides.get("num_units", 0) > 0:
        text_parts.append(f"Number of units override: {overrides['num_units']}")
    if overrides.get("notes", "").strip():
        text_parts.append(f"Additional notes: {overrides['notes'].strip()}")

    text_parts.append(f"\nI've attached {len(images)} Google Street View photos of this property taken from different angles. Please analyze these photos carefully to count actual window panes, identify the building type, siding material, visible gutters/downspouts, and dryer vents. DO NOT GUESS — count what you can see and clearly state when you're estimating for non-visible faces.")

    content.append({"type": "text", "text": "\n".join(text_parts)})

    # Add each Street View image
    for img in images:
        content.append({
            "type": "text",
            "text": f"\n📷 **{img['label']}** (heading {img['heading']}°):"
        })
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": img["base64"]
            }
        })

    return content


# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }
    .main-header {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
    }
    .main-header h1 {
        color: #1a1a2e;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .main-header p {
        color: #6b7280;
        font-size: 1rem;
    }
    .photo-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    .photo-grid img {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    div[data-testid="stChatMessage"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
    }
    .status-box {
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>Valiant Solutions Estimator</h1>
    <p>Enter a property address — we'll pull Street View photos and count every window pane</p>
</div>
""", unsafe_allow_html=True)


# --- API Key Check ---
anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
gmaps_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")

with st.sidebar:
    st.markdown("### API Keys")
    if not anthropic_key:
        anthropic_key = st.text_input("Anthropic API Key", type="password", help="Your Claude API key")
    else:
        st.success("Anthropic API key loaded")

    if not gmaps_key:
        gmaps_key = st.text_input("Google Maps API Key", type="password", help="Enable Street View Static API and Geocoding API")
    else:
        st.success("Google Maps API key loaded")

    st.markdown("---")
    st.markdown("### How It Works")
    st.markdown(
        "1. Enter any property address\n"
        "2. We grab **4 Street View photos** from different angles\n"
        "3. Claude **visually analyzes** the actual building\n"
        "4. Counts real window panes, identifies materials, measures features\n"
        "5. Generates a detailed estimate based on what it **actually sees**"
    )

    st.markdown("---")
    st.markdown("### Override Details (Optional)")
    st.markdown("*Only use these if the AI gets something wrong.*")
    building_type = st.selectbox("Building Type", ["Auto-detect", "Highrise", "Lowrise", "Townhome", "Commercial"])
    num_floors = st.number_input("Number of Floors", min_value=0, max_value=100, value=0, help="Leave at 0 for auto-detect")
    num_units = st.number_input("Number of Units", min_value=0, max_value=1000, value=0, help="Leave at 0 for auto-detect")
    extra_notes = st.text_area("Additional Notes", placeholder="e.g. 'It's an L-shaped building' or 'Stucco siding'...")

    st.markdown("---")
    st.markdown("### About")
    st.markdown("AI-powered estimator that uses **Google Street View photos** and **Claude Vision** to count actual window panes and analyze building features. No more guesswork.")
    st.markdown("*Estimates should be verified with an on-site visit.*")

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.image_cache = {}
        st.rerun()

if not anthropic_key:
    st.warning("Please enter your Anthropic API key in the sidebar.")
    st.stop()

if not gmaps_key:
    st.warning("Please enter your Google Maps API key in the sidebar. You need the Street View Static API and Geocoding API enabled.")
    st.stop()


# --- Chat State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "image_cache" not in st.session_state:
    st.session_state.image_cache = {}


# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user" and msg.get("images"):
            st.markdown(msg["display_text"])
            cols = st.columns(2)
            for i, img in enumerate(msg["images"]):
                with cols[i % 2]:
                    st.image(base64.b64decode(img["base64"]), caption=img["label"], use_container_width=True)
        else:
            st.markdown(msg.get("display_text", msg.get("content", "")))


# --- Chat Input ---
if user_input := st.chat_input("Enter property address (e.g. 123 Main St SW, Calgary, AB)..."):

    overrides = {
        "building_type": building_type,
        "num_floors": num_floors,
        "num_units": num_units,
        "notes": extra_notes
    }

    # Show user message
    with st.chat_message("user"):
        st.markdown(f"**Property:** {user_input}")

    # Fetch Street View images
    with st.chat_message("assistant"):
        with st.spinner("📍 Geocoding address and fetching Street View photos..."):
            images, formatted_address, error = fetch_property_images(user_input, gmaps_key)

        if error:
            st.error(f"⚠️ {error}")
            fallback_msg = f"Property: {user_input}\nServices requested: ALL\n\n⚠️ Street View photos could not be loaded: {error}\nPlease provide your best estimate based on the address alone, using your knowledge of Calgary properties."

            if overrides.get("building_type") and overrides["building_type"] != "Auto-detect":
                fallback_msg += f"\nBuilding type: {overrides['building_type']}"
            if overrides.get("num_floors", 0) > 0:
                fallback_msg += f"\nNumber of floors: {overrides['num_floors']}"
            if overrides.get("num_units", 0) > 0:
                fallback_msg += f"\nNumber of units: {overrides['num_units']}"
            if overrides.get("notes", "").strip():
                fallback_msg += f"\nAdditional notes: {overrides['notes'].strip()}"

            st.session_state.messages.append({
                "role": "user",
                "content": fallback_msg,
                "display_text": f"**Property:** {user_input}"
            })

            with st.spinner("Generating estimate (without photos)..."):
                try:
                    client = anthropic.Anthropic(api_key=anthropic_key)
                    api_messages = [{"role": "user", "content": fallback_msg}]
                    response = client.messages.create(
                        model="claude-sonnet-4-5-20250929",
                        max_tokens=8192,
                        system=SYSTEM_PROMPT,
                        messages=api_messages
                    )
                    assistant_msg = response.content[0].text
                    st.markdown(assistant_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_msg,
                        "display_text": assistant_msg
                    })
                except anthropic.AuthenticationError:
                    st.error("Invalid API key. Please check your Anthropic API key.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            # Show the Street View photos
            if formatted_address:
                st.markdown(f"📍 **Resolved address:** {formatted_address}")

            st.markdown(f"📷 **{len(images)} Street View photos captured:**")
            cols = st.columns(2)
            for i, img in enumerate(images):
                with cols[i % 2]:
                    st.image(base64.b64decode(img["base64"]), caption=img["label"], use_container_width=True)

            # Store user message with images for history
            display_text = f"**Property:** {user_input}"
            if formatted_address and formatted_address != user_input:
                display_text += f"\n📍 {formatted_address}"

            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "display_text": display_text,
                "images": images
            })

            # Build vision message and call Claude
            vision_content = build_vision_messages(user_input, images, overrides)

            with st.spinner("🔍 Analyzing photos — counting windows, identifying materials, measuring features..."):
                try:
                    client = anthropic.Anthropic(api_key=anthropic_key)

                    # For the API call, we need the full vision content
                    api_messages = [{"role": "user", "content": vision_content}]

                    # Include chat history for follow-up messages
                    if len(st.session_state.messages) > 1:
                        history = []
                        for msg in st.session_state.messages[:-1]:
                            if msg["role"] == "user":
                                history.append({"role": "user", "content": msg.get("content", "")})
                            else:
                                history.append({"role": "assistant", "content": msg.get("content", "")})
                        api_messages = history + api_messages

                    response = client.messages.create(
                        model="claude-sonnet-4-5-20250929",
                        max_tokens=8192,
                        system=SYSTEM_PROMPT,
                        messages=api_messages
                    )

                    assistant_msg = response.content[0].text
                    st.markdown(assistant_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_msg,
                        "display_text": assistant_msg
                    })

                except anthropic.AuthenticationError:
                    st.error("Invalid API key. Please check your Anthropic API key.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
