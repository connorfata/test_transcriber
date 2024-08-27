from sec_edgar_downloader import Downloader
import os
import datetime

# Initialize the downloader with your company name and email address
company_name = "scribe_"
email_address = "fataconnor13@gmail.com"
dl = Downloader(company_name=company_name, email_address=email_address)

# Function to download a specific SEC filing
def download_specific_sec_filing(ticker, filing_type="10-K", year=None, quarter=None, output_dir="sec_filings"):
    """
    Download a specific SEC filing for a company based on the filing type, year, and quarter.

    :param ticker: The ticker symbol of the company (e.g., "AAPL" for Apple Inc.)
    :param filing_type: The type of filing to download (e.g., "10-K", "10-Q")
    :param year: The year of the filing (e.g., 2023)
    :param quarter: The quarter of the filing (for "10-Q", e.g., 1 for Q1, 2 for Q2, etc.)
    :param output_dir: The directory where the filings will be saved
    """
    try:
        # Set the save path for the downloader
        dl.save_path = output_dir

        # Download all filings of the specified type
        dl.get(filing_type, ticker)

        # List the downloaded filings
        downloaded_files = os.listdir(output_dir)

        # Filter by the specified year and quarter
        for file_name in downloaded_files:
            file_path = os.path.join(output_dir, file_name)

            # Parse the date from the file name (assuming it's in the format YYYY-MM-DD in the file name)
            if filing_type == "10-K":
                if str(year) in file_name:
                    print(f"Found {year} {filing_type} filing: {file_name}")
                    return
            elif filing_type == "10-Q":
                # Extract the date from the file name or its metadata
                file_date_str = file_name.split('-')[0]  # Assumes the date is at the start of the file name
                filing_date = datetime.datetime.strptime(file_date_str, '%Y-%m-%d').date()

                # Check if the date matches the specified year and quarter
                if filing_date.year == year and ((quarter - 1) * 3 + 1) <= filing_date.month <= (quarter * 3):
                    print(f"Found Q{quarter} {year} {filing_type} filing: {file_name}")
                    return

        print(f"No {filing_type} filings found for {ticker} matching the specified year and quarter.")
    except Exception as e:
        print(f"Error downloading filings: {str(e)}")

# Example usage
ticker = "AAPL"  # Apple's ticker symbol
filing_type = "10-Q"  # Type of filing to download, "10-K" or "10-Q"
year = 2023  # Year of the filing
quarter = 2  # Quarter for "10-Q", can be 1, 2, 3, or 4
output_dir = "sec_filings"  # Directory to save the filings

download_specific_sec_filing(ticker, filing_type, year, quarter, output_dir)



