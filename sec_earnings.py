import sys
from sec_edgar_downloader import Downloader
import datetime
import os

# Initialize the downloader with your company name and email address
company_name = "scribe_"
email_address = "fataconnor13@gmail.com"
dl = Downloader(company_name=company_name, email_address=email_address)

def get_quarter(month):
    """Return the quarter number based on the month."""
    return (month - 1) // 3 + 1

def download_specific_sec_filing(ticker, filing_type="10-Q", year=None, quarter=None, output_dir="sec_filings"):
    """
    Download a specific SEC filing for a company based on the filing type, year, and quarter.

    :param ticker: The ticker symbol of the company (e.g., "AAPL" for Apple Inc.)
    :param filing_type: The type of filing to download (e.g., "10-K", "10-Q")
    :param year: The year of the filing (e.g., 2023)
    :param quarter: The quarter of the filing (for "10-Q", e.g., 1 for Q1, 2 for Q2, etc.)
    :param output_dir: The directory where the filings will be saved
    """
    try:
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        dl.save_path = output_dir

        # Fetch the filings
        print(f"Fetching {filing_type} filings for {ticker} from the SEC...")
        filings = dl.get(filing_type, ticker)

        if filings == 0:
            print(f"No {filing_type} filings found for {ticker}.")
            return

        # List all downloaded files
        print(f"\nAll downloaded {filing_type} filings for {ticker}:")
        for file_name in os.listdir(output_dir):
            if ticker.lower() in file_name.lower() and filing_type in file_name:
                print(file_name)

        # Iterate through the filings to find the one that matches the desired quarter and year
        found = False
        closest_year = None
        closest_file = None

        for file_name in os.listdir(output_dir):
            if ticker.lower() not in file_name.lower() or filing_type not in file_name:
                continue
            
            filing_date_str = file_name.split('-')[0]  # Assumes the date is at the start of the file name
            try:
                filing_date = datetime.datetime.strptime(filing_date_str, '%Y-%m-%d').date()
                filing_quarter = get_quarter(filing_date.month)
                
                if filing_type == "10-Q" and filing_date.year == year and filing_quarter == quarter:
                    print(f"\nFound exact match - Q{quarter} {year} 10-Q filing for {ticker}: {file_name}")
                    found = True
                    break
                elif filing_type == "10-K" and filing_date.year == year:
                    print(f"\nFound exact match - {year} 10-K filing for {ticker}: {file_name}")
                    found = True
                    break
                
                # Track the closest year if no exact match is found
                if closest_year is None or abs(filing_date.year - year) < abs(closest_year - year):
                    closest_year = filing_date.year
                    closest_file = file_name

            except ValueError:
                print(f"Could not parse date from file name: {file_name}")

        if found:
            print(f"Successfully found the {filing_type} filing for {ticker}.")
        elif closest_file:
            print(f"\nNo exact match found. Closest {filing_type} filing for {ticker}: {closest_file}")
        else:
            print(f"\nNo matching or close {filing_type} filing found for {ticker} for {'Q' + str(quarter) if quarter else ''} {year}.")

    except Exception as e:
        print(f"Error downloading filings: {str(e)}")

def get_user_input():
    """Get user input for filing details."""
    ticker = input("Enter the ticker symbol (e.g., AAPL): ").upper()
    
    while True:
        filing_type = input("Enter the filing type (10-K or 10-Q): ").upper()
        if filing_type in ["10-K", "10-Q"]:
            break
        print("Invalid filing type. Please enter either '10-K' or '10-Q'.")
    
    year = int(input("Enter the year (e.g., 2023): "))
    
    quarter = None
    if filing_type == "10-Q":
        while True:
            quarter = int(input("Enter the quarter (1-4): "))
            if 1 <= quarter <= 4:
                break
            print("Invalid quarter. Please enter a number between 1 and 4.")
    
    return ticker, filing_type, year, quarter

def main():
    ticker, filing_type, year, quarter = get_user_input()
    output_dir = "sec_filings"
    download_specific_sec_filing(ticker, filing_type, year, quarter, output_dir)

if __name__ == "__main__":
    main()