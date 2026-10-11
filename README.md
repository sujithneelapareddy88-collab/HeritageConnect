# HeritageConnect — Group 9 Prototype

## Run on macOS
1. Install Python 3 if needed.
2. Open Terminal and enter this folder.
3. Create and activate a virtual environment:
   `python3 -m venv venv`
   `source venv/bin/activate`
4. Install packages:
   `pip install -r requirements.txt`
5. Run:
   `streamlit run app.py`

## Prototype notes
- Hampi attraction coordinates and stakeholder relationships are demonstration data and should be verified before final submission.
- Guide/accommodation entries are sample listings, not real providers or live availability.
- OSRM routing requires internet access. If unavailable, the app shows a dashed connector and clearly labels it as not a road route.
- Community reports and booking requests are demo-only and are not persisted or sent to providers.
