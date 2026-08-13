# 🎬 ShowTime - Streamlit Movie Ticketing Web App

ShowTime is a modern, full-featured movie ticket booking platform built with **Streamlit**, **FastAPI**, **SQLite**, and custom glassmorphism UI styling.

---

## ✨ Features

- 🍿 **Movie Catalog & City Selector**: Browse movies in Mumbai, Delhi NCR, Bengaluru, Hyderabad, Chennai, etc.
- 🔍 **Language & Genre Filtering**: Filter blockbusters by Tamil, Telugu, Hindi, English, Action, Sci-Fi, Comedy.
- 🎬 **Detailed Movie View & Trailers**: Embedded YouTube trailers, duration, certificate, and synopsis.
- 🌟 **100% Genuine Cast & Crew Headshots**: Real local headshots for Thalapathy Vijay, Trisha, Sanjay Dutt, Pradeep Ranganathan, Ivana, Allu Arjun, Rashmika, Prabhas, Shah Rukh Khan, etc.
- 🎟️ **Interactive Seat Matrix Picker**: Choose Recliner (₹450), Prime (₹300), or Classic (₹180) seats with real-time status.
- 🥤 **Food & Beverages Drawer**: Add Popcorn combos, Pepsi, Nachos to your order.
- 💳 **Promo Code & Checkout**: Enter `SHOWTIME20` for instant ₹150 discount.
- 🎫 **Digital E-Ticket Generator**: Instant E-ticket confirmation with booking ID and QR Code.
- 🤖 **AI Recommendation Assistant**: Chatbot for instant movie suggestions.

---

## 🚀 How to Run Locally

```bash
# 1. Run Streamlit App
streamlit run streamlit_app.py

# 2. Or Run FastAPI Backend
python -m uvicorn app:app --port 8000
```

- Streamlit App: `http://localhost:8501`
- FastAPI Web App: `http://127.0.0.1:8000`

---

## 🌐 Deploying to Streamlit Community Cloud (Free 1-Click Hosting)

### Repository URL:
`https://github.com/71382502139saieeswar-tony/showtime`

### Step 1: Push Code to GitHub
Run `push_to_github.bat` or run in terminal:
```bash
git init
git add .
git commit -m "Deploy ShowTime Streamlit Application"
git branch -M main
git remote add origin https://github.com/71382502139saieeswar-tony/showtime.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io).
2. Log in with your GitHub account: **`71382502139saieeswar-tony`**.
3. Click **New app**.
4. Select repository: `71382502139saieeswar-tony/showtime`.
5. Branch: `main` | Main file path: `streamlit_app.py`.
6. Click **Deploy!** 🚀

Your app will be live globally at `https://showtime.streamlit.app`!
