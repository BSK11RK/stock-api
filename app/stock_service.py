# 株価取得
import yfinance as yf


COMPANY_NAMES = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "GOOGL": "Google",
    "TSLA": "Tesla",
    "META": "Meta",
    "NVDA": "NVIDIA",
    "NFLX": "Netflix",
    "INTC": "Intel",
    "KO": "Coca-Cola",

    "7203.T": "Toyota",
    "6758.T": "Sony",
    "9984.T": "SoftBank",
    "7974.T": "Nintendo",
    "6861.T": "Keyence",
    "9983.T": "Fast Retailing",
    "8306.T": "MUFG",
    "8035.T": "Tokyo Electron",
    "6098.T": "Recruit",
    "9432.T": "NTT",
}

def get_company_name(symbol: str):
    return COMPANY_NAMES.get(symbol, "Unknown")


def get_stock_price(symbol: str):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")
    
    if data.empty:
        return None
    return float(data["Close"].iloc[-1])


# 複数銘柄
def get_multiple_stock_prices(symbols: list[str]):
    results = {}
    
    for symbol in symbols:
        try:
            price = get_stock_price(symbol)
            if price is not None:
                results[symbol] = price
        except Exception:
            continue
    return results