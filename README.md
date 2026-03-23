# 🤖 Claude X-Automation Bot
An open-source automation engine using Gemini 2.0 and Selenium to curate and post trending tech news to X (Twitter).

## 🌟 Key Features
- **AI Content Generation:** Uses Gemini 2.0 Flash to turn RSS headlines into engaging tweets.
- **Anti-Detection:** Implements `selenium-stealth` and user-profile persistence to mimic human behavior.
- **Automated Scheduling:** Runs 24/7 using the Python `schedule` library.

## 🛠️ Setup
1. Clone the repo.
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your `TWITTER_USER`, `TWITTER_PASS`, and `GEMINI_API_KEY`.
4. Run `python main.py`.

## 📜 License
This project is licensed under the MIT License.
