from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    whatsapp_phone_number: str = Field(default="")
    whatsapp_apikey: str = Field(default="")
    
    poll_interval_seconds: int = 30
    database_path: str = "data/monitor.db"
    dashboard_port: int = 8000
    
    # Generic CSS Selectors for Scraper
    pincode_input_selector: str = "#pincode-input"
    pincode_submit_selector: str = "#pincode-submit"
    availability_status_selector: str = ".availability-status"
    in_stock_text: str = "In Stock"

    class Config:
        env_file = ".env"

settings = Settings()
