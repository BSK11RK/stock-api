# 株価取得
import yfinance as yf


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