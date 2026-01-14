# AWS SAA-C03 Quiz App

This is a Streamlit application for practicing AWS Solutions Architect Associate (SAA-C03) questions. It parses a large Markdown file of questions and presents them in an interactive quiz format.

## Deployment to Streamlit Cloud

To deploy this app to Streamlit Cloud, follow these steps:
 
1.  **Push to GitHub**: ensure this repository is pushed to your GitHub account.
    ```bash
    git add .
    git commit -m "Initial commit for Quiz App"
    git push
    ``` 

2.  **Connect to Streamlit Cloud**:
    *   Go to [share.streamlit.io](https://share.streamlit.io/).
    *   Login with your GitHub account.
    *   Click "New app".
    *   Select your repository (`aws-ssa-c03` or whatever you named it).
    *   Select the branch (usually `main`).
    *   Main file path: `app.py`.
    *   Click "Deploy".

3.  **Data File**:
    The app reads `SAA_C03.md`. This file is included in the repository, so Streamlit Cloud will be able to access it directly.

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
