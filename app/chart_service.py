import os
import matplotlib.pyplot as plt
from datetime import datetime


GRAPHS_DIR = "graphs"


def ensure_data_dir():
    if not os.path.exists(GRAPHS_DIR):
        os.makedirs(GRAPHS_DIR)
        
        
def create_stock_chart(symbol: str, stocks: list):
    ensure_data_dir()
    
    dates = [s.timestamp for s in stocks]
    prices = [s.price for s in stocks]
    
    plt.figure()
    plt.plot(dates, prices, marker="o")
    plt.title(f"{symbol} Price Chart")
    plt.xlabel("Time")
    plt.ylabel("Price(USD)")
    plt.xticks(rotation=45)
    
    filename = f"{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    filepath = os.path.join(GRAPHS_DIR, filename)
    
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()
    
    return filename