import sys
from sec_edgar_downloader import Downloader
import datetime
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
        logging.info(f"Starting download process for {ticker} {filing_type} filing for year {year}")
        
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        dl.save_path = output_dir
        logging.debug(f"Output directory set to: {os.path.abspath(output_dir)}")

        # Fetch the filings
        logging.info(f"Fetching {filing_type} filings for {ticker} from the SEC...")
        filings = dl.get(filing_type, ticker, amount=5)  # Fetch the 5 most recent filings
        logging.debug(f"Number of filings downloaded: {filings}")

        if filings == 0:
            logging.warning(f"No {filing_type} filings found for {ticker}.")
            return

        # List all files in the output directory
        logging.info(f"Listing all files in the output directory:")
        all_files = os.listdir(output_dir)
        for file_name in all_files:
            logging.info(f"File in output directory: {file_name}")

        # Find the file for the specified year
        target_file = None
        for file_name in all_files:
            if ticker.lower() in file_name.lower() and filing_type in file_name:
                file_date = file_name.split('-')[0]
                file_year = int(file_date.split('-')[0])
                if file_year == year:
                    target_file = file_name
                    break

        if target_file:
            logging.info(f"Found {filing_type} filing for {ticker} for year {year}: {target_file}")
            print(f"Successfully found {filing_type} filing for {ticker} for year {year}.")
            print(f"File: {target_file}")
        else:
            logging.warning(f"No {filing_type} filing found for {ticker} for year {year}.")
            print(f"No {filing_type} filing found for {ticker} for year {year}.")

    except Exception as e:
        logging.error(f"Error downloading filings: {str(e)}", exc_info=True)

def get_user_input():
    """Get user input for filing details."""
    ticker = input("Enter the ticker symbol (e.g., AAPL): ").upper()
    logging.info(f"User entered ticker: {ticker}")
    
    while True:
        filing_type = input("Enter the filing type (10-K or 10-Q): ").upper()
        if filing_type in ["10-K", "10-Q"]:
            break
        logging.warning("Invalid filing type entered. Prompting user again.")
        print("Invalid filing type. Please enter either '10-K' or '10-Q'.")
    logging.info(f"User entered filing type: {filing_type}")
    
    year = int(input("Enter the year (e.g., 2023): "))
    logging.info(f"User entered year: {year}")
    
    quarter = None
    if filing_type == "10-Q":
        while True:
            quarter = int(input("Enter the quarter (1-4): "))
            if 1 <= quarter <= 4:
                break
            logging.warning("Invalid quarter entered. Prompting user again.")
            print("Invalid quarter. Please enter a number between 1 and 4.")
        logging.info(f"User entered quarter: {quarter}")
    
    return ticker, filing_type, year, quarter

def main():
    logging.info("Starting SEC filing downloader script")
    ticker, filing_type, year, quarter = get_user_input()
    output_dir = "sec_filings"
    download_specific_sec_filing(ticker, filing_type, year, quarter, output_dir)
    logging.info("Script execution completed")

if __name__ == "__main__":
    main()