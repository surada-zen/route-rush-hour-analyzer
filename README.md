Create a minimal working Flask web app inside my repository "route-rush-hour-analyzer".

Goal:
I want a basic Flask app that runs and renders two pages.

Requirements:

1. Create app.py:
- Initialize Flask app
- Add route "/" → renders index.html
- Add route "/result" → renders result.html
- Add placeholder mock data in result route

2. Create templates:
- templates/index.html:
  - simple form with:
    - origin (text input for now)
    - destination (text input)
    - departure time (datetime input)
    - travel mode dropdown (drive, bike, walk)
    - submit button

- templates/result.html:
  - display:
    - origin
    - destination
    - selected time
    - mock recommended time
    - mock time saved
    - simple explanation

3. Create requirements.txt:
Include:
- Flask
- gunicorn
- pandas

4. Create README.md:
- project title
- short description
- tech stack
- how to run locally (simple instructions)

5. Keep everything very simple
6. Do NOT add Google Maps API yet
7. Do NOT add database yet
8. Add comments in code for future integration

Goal:
After this step, I should have a working Flask app structure that can be deployed later.
