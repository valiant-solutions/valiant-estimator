import streamlit as st
import anthropic
import os

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

## CRITICAL REQUIREMENT: DETAILED PROPERTY ANALYSIS

When a user provides a property address, you MUST perform a thorough property analysis BEFORE pricing. You are expected to use your knowledge of Calgary properties, common building designs, and construction standards to estimate the following. DO NOT skip this step. DO NOT give a vague ballpark. Show your work.

### Step 1: Property Assessment (ALWAYS INCLUDE)
For every estimate, you MUST determine and display:

**Building Characteristics:**
- Building type (highrise/lowrise/townhome/commercial)
- Number of stories/floors
- Approximate number of units (for multi-family)
- Approximate building footprint (length × width in feet)
- Number of building faces (typically 4, but can vary for L-shaped, U-shaped, etc.)

**Window Analysis:**
- Estimated window panes per unit (typical: 6-10 for townhomes, 8-14 for condos)
- Estimated window panes for common areas (lobbies, stairwells, hallways)
- Estimated window panes for commercial/ground floor (storefronts, entrances)
- Total estimated window pane count
- Balcony glass panels (outward-facing, included in scope)
- Window types present: standard casement, large picture windows, balcony railing glass, storefront, etc.

**Gutter/Eavestrough Analysis:**
- Estimated roofline perimeter in linear feet
- Number of downspouts (estimate based on building size)
- Gutter complexity (straight runs vs. corners, multiple rooflines)
- Total linear feet of eavestrough

**Siding Analysis:**
- Estimated total siding surface area in square feet (per face: height × width, sum all faces, subtract window/door openings)
- Siding material type if known (vinyl, hardie board, stucco, etc.)
- Number of floors of siding to clean
- Access difficulty (ground-level vs. upper stories requiring lifts)

**Dryer Vent Analysis:**
- Number of units with dryer vents
- Estimated vent locations (exterior wall, roof)
- Access considerations

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

---

### PROPERTY ANALYSIS

**Building Dimensions (estimated):**
- Footprint: ~[X] ft × [X] ft
- Stories: [X]
- Total units: [X]
- Building faces: [X]

**Window Count (estimated):**
| Location | Count | Type |
|----------|-------|------|
| Per-unit windows (X units × Y panes) | [total] | Casement/picture |
| Balcony railing glass (outward-facing) | [total] | Railing panels |
| Common areas (lobby, stairwells) | [total] | Various |
| Ground floor / commercial | [total] | Storefront |
| **Total Window Panes** | **[total]** | |

**Eavestrough (estimated):**
- Roofline perimeter: ~[X] linear feet
- Downspouts: ~[X]
- Total eavestrough: ~[X] linear feet

**Siding (estimated):**
- Total cleanable surface: ~[X] sq ft
- Material: [type if known, or "assumed vinyl/hardie"]

**Dryer Vents:**
- Units with vents: [X]
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

**Confidence Level:** [High/Medium/Low] — [brief explanation]

**Exclusions:**
- [list]

**Assumptions:**
- [list]

*This is an estimate based on AI analysis. Final pricing requires an on-site assessment.*
---

## BEHAVIOR RULES
1. NEVER skip the property analysis section. Always estimate measurements even if approximate.
2. NEVER ask clarifying questions on the first message. Always provide a COMPLETE estimate for ALL services (Windows, Siding, Eavestrough, and Dryer Vent) on the first response, regardless of what services were requested. The user wants a full picture immediately.
3. If you recognize the Calgary address/property, use your knowledge of it. If you don't recognize it, make your BEST estimates based on the neighborhood, typical Calgary construction, and building type. State your assumptions clearly but DO NOT ask the user for more info — just estimate.
4. Show ALL math. Every dollar amount should trace back to a quantity × rate calculation.
5. If the user provides a Google Maps link, describe what you understand about the property from the URL/address.
6. When the user provides corrections or additional info (e.g., "it's actually 45 units"), recalculate everything with the new numbers.
7. Always compare your calculated estimate against the most similar historical job and explain any significant differences.
8. The goal is ONE ADDRESS IN → FULL DETAILED ESTIMATE OUT. No back and forth. No asking for more details. Estimate everything."""


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
    .estimate-output {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    div[data-testid="stChatMessage"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>Valiant Solutions Estimator</h1>
    <p>Enter a property address or Google Maps link to get a detailed cleaning estimate</p>
</div>
""", unsafe_allow_html=True)


# --- API Key Check ---
api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Anthropic API Key", type="password", help="Enter your Claude API key")

if not api_key:
    st.warning("Please enter your Anthropic API key in the sidebar to get started.")
    st.stop()


# --- Sidebar ---
with st.sidebar:
    st.markdown("### How It Works")
    st.markdown("Enter any Calgary property address and get a complete estimate for **all services** automatically:")
    st.markdown("- Window Cleaning\n- Siding Cleaning\n- Eavestrough Cleaning\n- Dryer Vent Cleaning")

    st.markdown("---")
    st.markdown("### Override Details (Optional)")
    st.markdown("*Only use these if the AI gets something wrong — it will auto-detect everything by default.*")
    building_type = st.selectbox("Building Type", ["Auto-detect", "Highrise", "Lowrise", "Townhome", "Commercial"])
    num_floors = st.number_input("Number of Floors", min_value=0, max_value=100, value=0, help="Leave at 0 for auto-detect")
    num_units = st.number_input("Number of Units", min_value=0, max_value=1000, value=0, help="Leave at 0 for auto-detect")
    extra_notes = st.text_area("Additional Notes", placeholder="e.g. 'It's an L-shaped building' or 'Stucco siding'...")

    st.markdown("---")
    st.markdown("### About")
    st.markdown("AI-powered estimator using Valiant Solutions historical data. Analyzes window counts, building height, gutter length, siding area, and more.")
    st.markdown("*Estimates should be verified with an on-site visit.*")

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# --- Chat State ---
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# --- Chat Input ---
if user_input := st.chat_input("Enter property address or Google Maps link..."):
    context_parts = [f"Property: {user_input}"]
    context_parts.append("Services requested: ALL — provide complete estimates for Window Cleaning, Siding Cleaning, Eavestrough Cleaning, and Dryer Vent Cleaning.")
    if building_type != "Auto-detect":
        context_parts.append(f"Building type: {building_type}")
    if num_floors > 0:
        context_parts.append(f"Number of floors: {num_floors}")
    if num_units > 0:
        context_parts.append(f"Number of units: {num_units}")
    if extra_notes.strip():
        context_parts.append(f"Additional notes: {extra_notes.strip()}")

    full_message = "\n".join(context_parts)

    st.session_state.messages.append({"role": "user", "content": full_message})
    with st.chat_message("user"):
        st.markdown(full_message)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing property and generating estimate..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

                response = client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=8192,
                    system=SYSTEM_PROMPT,
                    messages=api_messages
                )

                assistant_msg = response.content[0].text
                st.markdown(assistant_msg)
                st.session_state.messages.append({"role": "assistant", "content": assistant_msg})

            except anthropic.AuthenticationError:
                st.error("Invalid API key. Please check your Anthropic API key.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
