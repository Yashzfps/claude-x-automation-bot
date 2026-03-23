import os
import time
import logging
import schedule
import feedparser
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from google import genai

# Setup Professional Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

class TwitterBot:
    def __init__(self):
        self.user = os.getenv("TWITTER_USER")
        self.password = os.getenv("TWITTER_PASS")
        self.email = os.getenv("TWITTER_EMAIL")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.gemini_key)
        self.driver = None

    def fetch_news(self):
        """Fetches the latest tech headlines from RSS feeds."""
        feeds = [
            "https://www.theverge.com/rss/index.xml",
            "https://www.tomshardware.com/feeds/all",
            "https://hnrss.org/frontpage"
        ]
        headlines = []
        for url in feeds:
            try:
                feed = feedparser.parse(url)
                if feed.entries:
                    headlines.append(feed.entries[0].title)
            except Exception as e:
                logging.error(f"Error fetching RSS: {e}")
        return headlines

    def generate_content(self, news_item):
        """Uses Gemini 2.0 to create a viral tweet from news."""
        prompt = f"Rewrite this tech news into a viral tweet: {news_item}. Rules: <160 chars, 2 hashtags, no links."
        try:
            response = self.client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            return response.text.strip().replace('"', '')
        except Exception as e:
            logging.error(f"Gemini generation failed: {e}")
            return "Innovation is moving fast in tech today! #Tech #Future"

    def init_driver(self):
        """Initializes Chrome with anti-detection and session persistence."""
        options = Options()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        user_data_path = os.path.join(script_dir, "Twitter_Profile")
        
        options.add_argument(f"user-data-dir={user_data_path}")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--start-maximized")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        stealth(self.driver, languages=["en-US"], vendor="Google Inc.", platform="Win32", fix_hairline=True)

    def login(self):
        """Handles the login flow including email verification checks."""
        wait = WebDriverWait(self.driver, 25)
        self.driver.get("https://x.com/login")
        time.sleep(5)
        
        try:
            # Check if already logged in via session
            if len(self.driver.find_elements(By.XPATH, "//div[@data-testid='tweetTextarea_0']")) > 0:
                logging.info("Already logged in via profile.")
                return
            
            user_input = wait.until(EC.presence_of_element_located((By.NAME, "text")))
            user_input.send_keys(self.user + Keys.ENTER)
            time.sleep(3)

            # Check for extra email verification
            if len(self.driver.find_elements(By.NAME, "text")) > 0:
                self.driver.find_element(By.NAME, "text").send_keys(self.email + Keys.ENTER)
                time.sleep(3)

            pass_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            pass_input.send_keys(self.password + Keys.ENTER)
            logging.info("Login process complete.")
        except Exception as e:
            logging.warning(f"Login interrupted: {e}")

    def post_tweet(self, text):
        """Posts the generated text to X."""
        wait = WebDriverWait(self.driver, 20)
        try:
            box = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='tweetTextarea_0']")))
            box.click()
            for char in text:
                box.send_keys(char)
                time.sleep(0.05)
            
            time.sleep(2)
            self.driver.find_element(By.XPATH, "//div[@data-testid='tweetButtonInline']").click()
            logging.info(f"Successfully posted: {text[:50]}...")
        except Exception as e:
            logging.error(f"Post failed: {e}")

    def run_cycle(self):
        logging.info("--- Starting Automation Cycle ---")
        news = self.fetch_news()
        if not news: 
            logging.warning("No news found.")
            return
        
        self.init_driver()
        try:
            self.login()
            tweet = self.generate_content(news[0])
            self.post_tweet(tweet)
        finally:
            self.driver.quit()
            logging.info("Cycle complete. Driver closed.")

if __name__ == "__main__":
    bot = TwitterBot()
    # Initial run on startup
    bot.run_cycle() 
    
    # Schedule to run every 2 hours
    schedule.every(2).hours.do(bot.run_cycle)
    
    while True:
        schedule.run_pending()
        time.sleep(1)