# Hiring test template

## Requirements

- Python 3
- uv ([installation instructions](https://docs.astral.sh/uv/getting-started/installation/))
- Node

## Instructions

1. In the Python `/backend` folder, implement the following routes required by the front-end in the Flask API
   - `GET /tags`
   - `GET /posts`
   - `GET /posts/featured`
   - `POST /like/<post_id>`
2. In the Vue.js `/frontend` folder, implement a Like button for posts following the design in the supplied Figma file (`technical-assessment-design.fig`)
   - should have default, hover, focus visible and active states 
   - clicking the Like button should send a request to the API
   - the Like button should update to reflect latest source of truth from API

## Deliverables

- A link to your source code (eg. in a GitHub repo).
- Talking through your process and result (in the follow-up interview).
- Demoing your working solution (in the follow-up interview).

## Usage

Install front end dependencies:

```bash
cd frontend
npm i
```

Run backend:

```bash
uv run backend/backend.py
```

Run frontend:

```bash
cd frontend
npm start
```