import requests
from sec_api import QueryApi
import json
from datetime import datetime
import os

# Replace 'YOUR_API_KEY' with your actual SEC API key
queryApi = QueryApi(api_key="YOUR_API_KEY")

def get_latest_10q(ticker):
    query = {
        "query": {
            "query_string": {
                "query": f"ticker:{ticker} AND formType:\"10-Q\""
            }
        },
        "from": "0",
        "size": "1",
        "sort": [{"filedAt": {"order": "desc"}}]
    }

    response = queryApi.get_filings(query)
    
    if response['total']['value'] == 0:
        print(f"No 10-Q filings found for {ticker}")
        return None
    
    filing = response['filings'][0]
    return filing

def download_10q(filing):
    url = filing['linkToFilingDetails']
    response = requests.get(url)
    
    if response.status_code == 200:
        filename = f"{filing['ticker']}_10Q_{filing['periodOfReport'].split('-')[0]}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"10-Q report downloaded: {filename}")
    else:
        print(f"Failed to download 10-Q. Status code: {response.status_code}")

def main():
    ticker = input("Enter the company ticker symbol: ").upper()
    
    latest_10q = get_latest_10q(ticker)
    if latest_10q:
        print(f"Latest 10-Q found for {ticker}:")
        print(f"Filed on: {latest_10q['filedAt']}")
        print(f"Period: {latest_10q['periodOfReport']}")
        
        download = input("Do you want to download this 10-Q? (y/n): ").lower()
        if download == 'y':
            download_10q(latest_10q)

if __name__ == "__main__":
    main()