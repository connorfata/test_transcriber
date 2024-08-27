import requests
import os
from datetime import datetime

def get_api_key():
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        api_key = input("Please enter your Alpha Vantage API key: ")
    return api_key

def get_latest_10q(ticker, api_key):
    base_url = "https://www.alphavantage.co/query"
    function = "INCOME_STATEMENT"
    
    params = {
        "function": function,
        "symbol": ticker,
        "apikey": api_key
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "quarterlyReports" in data:
            latest_report = data["quarterlyReports"][0]
            return latest_report
        else:
            print(f"No quarterly reports found for {ticker}")
            return None
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

def display_10q_data(report, ticker):
    if report:
        fiscal_date_ending = report.get("fiscalDateEnding", "N/A")
        total_revenue = report.get("totalRevenue", "N/A")
        gross_profit = report.get("grossProfit", "N/A")
        net_income = report.get("netIncome", "N/A")

        print(f"\nLatest 10-Q data for {ticker}:")
        print(f"Fiscal Date Ending: {fiscal_date_ending}")
        print(f"Total Revenue: ${total_revenue}")
        print(f"Gross Profit: ${gross_profit}")
        print(f"Net Income: ${net_income}")
    else:
        print("No report data available.")

def main():
    api_key = get_api_key()
    ticker = input("Enter the company ticker symbol: ").upper()
    
    latest_10q = get_latest_10q(ticker, api_key)
    if latest_10q:
        display_10q_data(latest_10q, ticker)
    
    save_option = input("\nDo you want to save this data to a file? (y/n): ").lower()
    if save_option == 'y':
        filename = f"{ticker}_10Q_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(filename, 'w') as f:
            for key, value in latest_10q.items():
                f.write(f"{key}: {value}\n")
        print(f"Data saved to {filename}")

if __name__ == "__main__":
    main()