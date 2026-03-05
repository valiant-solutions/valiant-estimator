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
You generate itemized cost estimates for:
- Exterior Window Cleaning (highrise, lowrise, townhome, commercial)
- Siding Cleaning
- Eavestrough / Gutter Cleaning
- Dryer Vent Cleaning

When a user provides a property address, Google Maps link, or property name, you analyze the property and produce a detailed estimate based on Valiant's historical pricing data and patterns.

## HISTORICAL JOB DATA (REFERENCE PRICING)

### HIGHRISE PROPERTIES
1. One Park Central — Highrise Exterior Window Cleaning: $20,525
   - Scope: All exterior unreachable windows, outward-facing balcony railing glass, common area windows, 1st/2nd floor commercial windows, 8th floor rooftop patio windows
   - Exclusions: Inward-facing balcony glass, windows/patio doors within balconies, hard water stain removal

2. Renfrew House — Highrise Exterior Window Cleaning: $2,385/session (Spring + Fall)
   - Scope: All exterior unreachable windows, outward-facing balcony railing glass, common area windows, main floor N/S face
   - Combined Spring+Fall: $4,770 + GST = $5,008.50

3. The Orange Lofts — Highrise Exterior Window Cleaning: $5,475
   - Scope: All exterior unreachable windows, outward-facing balcony railing glass, common area windows
   - Optional: Upper balcony window cleaning $475

4. Copperwood I — Tower + Lowrise Window Cleaning: $9,970
   - Tower exterior: $6,120 | Lowrise exterior: $3,850
   - Optional: Tower accessible windows $1,595 | Lowrise accessible windows $1,275
   - Optional: Eavestrough cleaning $3,840

### COMMERCIAL
5. The Dorian Hotel — Commercial Highrise Window Cleaning: $9,125
   - Assumes: elevator access, sufficient water, roof anchors inspected within 12 months

### LOWRISE PROPERTIES
6. Sage Place — Lowrise Exterior Window Cleaning: $4,385
   - Exclusions: Windows/patio doors within balconies

7. Villa D'Este — Lowrise (3 floors): $6,183.10
   - Exterior unreachable: $5,668.85 | Interior windows: $514.25
   - Optional: Balcony window cleaning (1st/2nd floors) $1,495

### TOWNHOME PROPERTIES
8. Copperfield Chalet 4 Copperstone — Townhome Complex
   - Windows: $6,237 | Siding: $8,415 | Eavestrough: $3,168
   - Dryer Vent: $4,455 (separate)
   - Bundle discount: 5% for 2 services, 10% for 3+

9. Gateway Townhomes Airdrie — Townhome Complex
   - Windows: $6,350.40 | Siding: $8,736 | Eavestrough: $3,472
   - Dryer Vent: $5,040 (separate)
   - Bundle discount: 5% for 2 services, 10% for 3+

10. Martin Crossing Court — Townhome Complex
    - Windows: $4,564.35 | Eavestrough: $4,919.25 | Siding: $5,152
    - 5% bundle discount applied for Windows+Eavestrough: -$474.18

11. Royal Birch Villas — Townhome Complex
    - Windows: $3,440 | Siding: $5,676
    - Eavestrough: $2,752 (separate) | Dryer Vent: $3,870 (separate)

## PRICING PATTERNS & RULES

### GST
- All estimates must include 5% GST calculated on the subtotal
- Format: Subtotal + GST (5%) = Total

### Bundle Discounts
- 2 services combined: 5% discount on subtotal
- 3+ services combined: 10% discount on subtotal
- Dryer vent cleaning is typically quoted separately and NOT included in bundle totals unless requested

### Standard Exclusions (include in every estimate)
- Inward-facing balcony railing glass
- Windows/patio doors within balconies
- Hard water stain removal
- Screen removal is resident/owner responsibility

### Standard Assumptions (include when relevant)
- Highrise: Unimpeded elevator access, sufficient common area water supply, roof anchors inspected within last 12 months
- Townhome: Standard water supply access from property; external water supply is an additional cost if needed
- Siding: Vinyl siding results may vary depending on condition and age

### Pricing Factors to Consider
When estimating a new property, consider:
1. Building type: Highrise, lowrise, townhome, commercial
2. Number of floors/stories: More floors = higher price
3. Building footprint/size: Larger buildings cost more
4. Number of units: For townhomes/condos, more units = higher price
5. Window count and type: Balcony glass, common area, commercial storefronts
6. Accessibility: Rope access vs. ladder vs. lift requirements
7. Complexity: Architectural features, setbacks, difficult access points

### Estimation Method
1. Identify the building type from the address/property info
2. Find the most similar property/properties in the historical data
3. Adjust pricing based on size differences, unit count, floor count
4. Apply any bundle discounts if multiple services are requested
5. Add GST at 5%
6. Present a clear, itemized estimate

## OUTPUT FORMAT

Always present estimates in this format:

---
**VALIANT SOLUTIONS — SERVICE ESTIMATE**

**Property:** [Name and Address]
**Building Type:** [Type]
**Date:** [Today's date]

**Scope of Work:**
[Description of what's included for each service]

| Service | Price |
|---------|-------|
| [Service 1] | $X,XXX.XX |
| [Service 2 if applicable] | $X,XXX.XX |
| [Optional services listed separately] | $X,XXX.XX |
| **Subtotal** | **$X,XXX.XX** |
| Bundle Discount (X%) | -$XXX.XX |
| **Subtotal After Discount** | **$X,XXX.XX** |
| GST (5%) | $XXX.XX |
| **TOTAL** | **$X,XXX.XX** |

**Exclusions:**
- [Standard exclusions]

**Assumptions:**
- [Standard assumptions]

**Comparable Reference:** Based on [similar property name] at $[price], adjusted for [reasoning]
---

## IMPORTANT BEHAVIOR RULES
1. Always ask clarifying questions if the property type is unclear
2. If you cannot determine building size/type from the address alone, ask the user for: number of floors, approximate number of units, building type
3. Always show which historical job(s) you're basing the estimate on and explain your reasoning
4. Present estimates as ESTIMATES that should be verified with an on-site visit
5. Be transparent about confidence level — if the property is very different from historical data, say so
6. When a Google Maps link is provided, describe what you understand about the property and use that to inform the estimate
7. If the user provides additional details (unit count, window count, etc.), refine the estimate accordingly"""
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
    <p>Enter a property address or Google Maps link to get a cleaning estimate</p>
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
    st.markdown("### Services")
    svc_windows = st.checkbox("Window Cleaning", value=True)
    svc_siding = st.checkbox("Siding Cleaning", value=False)
    svc_eavestrough = st.checkbox("Eavestrough Cleaning", value=False)
    svc_dryer = st.checkbox("Dryer Vent Cleaning", value=False)

    st.markdown("### Property Details (Optional)")
    building_type = st.selectbox("Building Type", ["Auto-detect", "Highrise", "Lowrise", "Townhome", "Commercial"])
    num_floors = st.number_input("Number of Floors", min_value=0, max_value=100, value=0, help="Leave at 0 for auto-detect")
    num_units = st.number_input("Number of Units", min_value=0, max_value=1000, value=0, help="Leave at 0 for auto-detect")
    extra_notes = st.text_area("Additional Notes", placeholder="Any details about the property...")

    st.markdown("---")
    st.markdown("### About")
    st.markdown("Powered by Claude AI using Valiant Solutions historical job data. Estimates should be verified with an on-site visit.")

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
if user_input := st.chat_input("Enter property address, name, or Google Maps link..."):
    services_requested = []
    if svc_windows: services_requested.append("Window Cleaning")
    if svc_siding: services_requested.append("Siding Cleaning")
    if svc_eavestrough: services_requested.append("Eavestrough Cleaning")
    if svc_dryer: services_requested.append("Dryer Vent Cleaning")

    context_parts = [f"Property: {user_input}"]
    if services_requested:
        context_parts.append(f"Services requested: {', '.join(services_requested)}")
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
        with st.spinner("Generating estimate..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

                response = client.messages.create(
                    model="claude-sonnet-4-5-20250514",
                    max_tokens=4096,
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
