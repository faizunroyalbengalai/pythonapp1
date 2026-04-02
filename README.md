# AtlasAuth Flask App

A simple Python web app with:

- landing page
- registration
- login
- logout
- protected dashboard
- MongoDB Atlas support

## 1. Create a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 2. Install dependencies

```powershell
pip install -r requirements.txt
```

## 3. Configure MongoDB Atlas

Copy `.env.example` to `.env` and update:

```env
SECRET_KEY=your-random-secret
MONGO_URI=your-mongodb-atlas-connection-string
DATABASE_NAME=auth_app
```

Notes:

- In MongoDB Atlas, allow your IP address in `Network Access`
- Create a database user in `Database Access`
- Use the connection string from Atlas and replace the username, password, and cluster values

## 4. Run the app

```powershell
python app.py
```

Open `http://127.0.0.1:5000`

## Project structure

```text
app.py
templates/
static/
requirements.txt
.env.example
```
