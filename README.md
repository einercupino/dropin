# Toronto Drop‑In Sports Finder

This is a minimal web application that allows you to search for drop‑in badminton and pickleball sessions at City of Toronto recreation facilities.

## Features

- A simple HTML front‑end with three inputs: **start date**, **end date**, and **sport**.
- A serverless API built with Python that fetches data from the City of Toronto drop‑in schedules and filters it based on your selections.
- Deployable to [Vercel](https://vercel.com/) with zero configuration. Vercel will automatically detect the `api/` folder and build a Python serverless function, while serving `index.html` as a static front‑end.

## Project structure

```
.
├── api/
│   └── dropin.py         # Python serverless function
├── drop_in.py            # Shared Python helper functions
├── index.html            # Front‑end interface
├── requirements.txt      # Python dependencies (requests library)
└── README.md             # This file
```

## Deploying

1. Make sure you have the [Vercel CLI](https://vercel.com/docs/cli) installed:
   ```sh
   npm install -g vercel
   ```
2. From within the project directory (`dropin-vercel`), run:
   ```sh
   vercel
   ```
   Vercel will prompt you to set up a new project or link to an existing one. Follow the on‑screen instructions.
3. When asked for a framework, choose **Other**. Vercel will detect the `api/` directory and build the Python function automatically. The `requirements.txt` file tells Vercel to install the `requests` package.
4. Once deployed, navigate to your Vercel URL. You should see the form to search for drop‑in sessions.

## Local testing

If you have Python installed locally, you can run the backend directly for quick testing:

```sh
pip install -r requirements.txt
python drop_in.py
```

This will not serve the HTML front‑end, but you can experiment with the helper functions.

## Notes

- The age filter used by default includes ages **6+, 16+, 17+, 18+, 19+**. Feel free to adjust this behaviour in `drop_in.py` under `get_events`.
- The City of Toronto data sources can occasionally be slow to respond. If a request fails, simply try again later.
