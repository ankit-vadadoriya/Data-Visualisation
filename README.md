EcoMove Mobility Project

Files
- analysis.py runs all six standalone analyses.
- visual_01_time_trend.py creates the monthly demand figure.
- visual_02_city_demand.py creates the city demand figure.
- visual_03_delay_distribution.py creates the delay distribution figure.
- visual_04_correlation.py creates the correlation figure.
- visual_05_financial_performance.py creates the financial figure.
- visual_06_accessibility_sustainability.py creates the accessibility and sustainability figure.
- dashboard.py runs the interactive dashboard.
- [5442] EcoMoveMobility.xlsx is the source dataset.

Setup
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run:
   python -m pip install -r requirements.txt

All figures
Run:
python analysis.py

One figure
Run any visual_*.py file directly.

The PNG figures are saved in the outputs folder.

Dashboard
Double-click run_dashboard.bat

If needed, run:
python -m streamlit run dashboard.py

Keep [5442] EcoMoveMobility.xlsx in the same folder as the Python files.
