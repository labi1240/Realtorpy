import requests
import logging
import time

class Proxy:
    def __init__(self, username=None, password=None, host=None, port=None):
        # Configure logging
        self.logger = self._setup_logger()
        
        # Proxy configuration
        self.PROXY_USERNAME = username
        self.PROXY_PASSWORD = password
        self.PROXY_HOST = host
        self.PROXY_PORT = port
        
        self.current_proxy = None
        self.max_retries = 3
        self.retry_delay = 2  # seconds between retries

    def _setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler('proxy.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

    def get_proxy_url(self):
        if self.PROXY_USERNAME and self.PROXY_PASSWORD and self.PROXY_HOST and self.PROXY_PORT:
            return f"http://{self.PROXY_USERNAME}:{self.PROXY_PASSWORD}@{self.PROXY_HOST}:{self.PROXY_PORT}"
        else:
            return None

    def set_proxies(self):
        # No need to fetch free proxies anymore
        self.current_proxy = self.get_proxy_url()
        self.logger.info("Custom proxy configuration loaded")
        return True

    def rotate_proxy(self):
        # Since we're using a single proxy, we'll just verify it works
        proxy_str = self.get_proxy_url()
        
        for attempt in range(self.max_retries):
            try:
                proxy_check_resp = requests.get(
                    "https://httpbin.org/ip", 
                    proxies={
                        'http': proxy_str,
                        'https': proxy_str
                    },
                    timeout=10
                )

                if proxy_check_resp.status_code == 200:
                    self.logger.info(f"Proxy test successful: {proxy_check_resp.json()}")
                    self.current_proxy = proxy_str
                    return True
                    
            except Exception as e:
                self.logger.error(f"Proxy test attempt {attempt + 1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                continue

        self.logger.error("All proxy test attempts failed")
        return False

if __name__ == "__main__":
    # Example usage
    proxy = Proxy()  # No credentials provided
    proxy.set_proxies()
    if proxy.rotate_proxy():
        print(f"Successfully connected using proxy: {proxy.current_proxy}")
    else:
        print("Failed to establish proxy connection")
