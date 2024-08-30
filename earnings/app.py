from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import os
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a real secret key in production

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_api_key():
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        logging.warning("Alpha Vantage API key not set in environment variables")
    return api_key

def get_newsapi_key():
    api_key = os.environ.get('NEWSAPI_KEY')
    if not api_key:
        logging.warning("NewsAPI key not set in environment variables")
    return api_key

def format_number(number):
    try:
        num = float(number)
        return f"{num/1e6:.2f}"  # Convert to millions and format to 2 decimal places
    except (ValueError, TypeError):
        return "N/A"

def calculate_ratios(balance_sheet, income_statement):
    try:
        total_assets = float(balance_sheet.get('totalAssets', 0))
        total_liabilities = float(balance_sheet.get('totalLiabilities', 0))
        current_assets = float(balance_sheet.get('totalCurrentAssets', 0))
        current_liabilities = float(balance_sheet.get('totalCurrentLiabilities', 0))
        inventory = float(balance_sheet.get('inventory', 0))
        net_income = float(income_statement.get('netIncome', 0))
        revenue = float(income_statement.get('totalRevenue', 0))
        equity = total_assets - total_liabilities

        ratios = {
            'Current Ratio': current_assets / current_liabilities if current_liabilities else None,
            'Quick Ratio': (current_assets - inventory) / current_liabilities if current_liabilities else None,
            'Debt to Equity': total_liabilities / equity if equity else None,
            'Return on Assets (ROA)': net_income / total_assets if total_assets else None,
            'Return on Equity (ROE)': net_income / equity if equity else None,
            'Profit Margin': net_income / revenue if revenue else None
        }
        return {k: f"{v:.2f}" if v is not None else "N/A" for k, v in ratios.items()}
    except Exception as e:
        logger.error(f"Error calculating ratios: {e}")
        return {}

def get_financial_data(ticker, api_key):
    base_url = "https://www.alphavantage.co/query"
    
    balance_sheet_params = {"function": "BALANCE_SHEET", "symbol": ticker, "apikey": api_key}
    income_statement_params = {"function": "INCOME_STATEMENT", "symbol": ticker, "apikey": api_key}
    
    balance_sheet_response = requests.get(base_url, params=balance_sheet_params)
    income_statement_response = requests.get(base_url, params=income_statement_params)
    
    if balance_sheet_response.status_code == 200 and income_statement_response.status_code == 200:
        balance_sheet_data = balance_sheet_response.json()
        income_statement_data = income_statement_response.json()
        
        if "quarterlyReports" in balance_sheet_data and "quarterlyReports" in income_statement_data:
            latest_balance_sheet = balance_sheet_data["quarterlyReports"][0]
            latest_income_statement = income_statement_data["quarterlyReports"][0]
            
            # Calculate financial ratios
            ratios = calculate_ratios(latest_balance_sheet, latest_income_statement)
            
            # Organize and format the balance sheet data
            balance_sheet = {
                'Assets': {
                    'Current Assets': {
                        'Cash and Cash Equivalents': format_number(latest_balance_sheet.get('cashAndCashEquivalentsAtCarryingValue')),
                        'Short-term Investments': format_number(latest_balance_sheet.get('shortTermInvestments')),
                        'Cash and Short-term Investments': format_number(latest_balance_sheet.get('cashAndShortTermInvestments')),
                        'Current Net Receivables': format_number(latest_balance_sheet.get('currentNetReceivables')),
                        'Inventory': format_number(latest_balance_sheet.get('inventory')),
                        'Other Current Assets': format_number(latest_balance_sheet.get('otherCurrentAssets')),
                        'Total Current Assets': format_number(latest_balance_sheet.get('totalCurrentAssets'))
                    },
                    'Non-Current Assets': {
                        'Property, Plant, and Equipment': format_number(latest_balance_sheet.get('propertyPlantEquipment')),
                        'Goodwill': format_number(latest_balance_sheet.get('goodwill')),
                        'Intangible Assets': format_number(latest_balance_sheet.get('intangibleAssets')),
                        'Intangible Assets Excluding Goodwill': format_number(latest_balance_sheet.get('intangibleAssetsExcludingGoodwill')),
                        'Long-term Investments': format_number(latest_balance_sheet.get('longTermInvestments')),
                        'Other Non-Current Assets': format_number(latest_balance_sheet.get('otherNonCurrrentAssets')),
                        'Total Non-Current Assets': format_number(latest_balance_sheet.get('totalNonCurrentAssets'))
                    },
                    'Total Assets': format_number(latest_balance_sheet.get('totalAssets')),
                    'Other Asset Details': {
                        'Investments': format_number(latest_balance_sheet.get('investments')),
                        'Accumulated Depreciation Amortization PPE': format_number(latest_balance_sheet.get('accumulatedDepreciationAmortizationPPE'))
                    }
                },
                'Liabilities': {
                    'Current Liabilities': {
                        'Accounts Payable': format_number(latest_balance_sheet.get('currentAccountsPayable')),
                        'Short-term Debt': format_number(latest_balance_sheet.get('shortTermDebt')),
                        'Current Long-term Debt': format_number(latest_balance_sheet.get('currentLongTermDebt')),
                        'Current Debt': format_number(latest_balance_sheet.get('currentDebt')),
                        'Other Current Liabilities': format_number(latest_balance_sheet.get('otherCurrentLiabilities')),
                        'Total Current Liabilities': format_number(latest_balance_sheet.get('totalCurrentLiabilities'))
                    },
                    'Non-Current Liabilities': {
                        'Long-term Debt': format_number(latest_balance_sheet.get('longTermDebt')),
                        'Long-term Debt Noncurrent': format_number(latest_balance_sheet.get('longTermDebtNoncurrent')),
                        'Capital Lease Obligations': format_number(latest_balance_sheet.get('capitalLeaseObligations')),
                        'Deferred Revenue': format_number(latest_balance_sheet.get('deferredRevenue')),
                        'Other Non-Current Liabilities': format_number(latest_balance_sheet.get('otherNonCurrentLiabilities')),
                        'Total Non-Current Liabilities': format_number(latest_balance_sheet.get('totalNonCurrentLiabilities'))
                    },
                    'Total Liabilities': format_number(latest_balance_sheet.get('totalLiabilities')),
                    'Other Liability Details': {
                        'Debt Long-term and Short-term Combined': format_number(latest_balance_sheet.get('debtLongtermAndShorttermCombinedAmount'))
                    }
                },
                'Shareholders Equity': {
                    'Common Stock': format_number(latest_balance_sheet.get('commonStock')),
                    'Retained Earnings': format_number(latest_balance_sheet.get('retainedEarnings')),
                    'Treasury Stock': format_number(latest_balance_sheet.get('treasuryStock')),
                    'Other Total Stockholders Equity': format_number(latest_balance_sheet.get('otherTotalStockholdersEquity')),
                    'Total Shareholders Equity': format_number(latest_balance_sheet.get('totalShareholderEquity'))
                },
                'Other Details': {
                    'Common Stock Shares Outstanding': format_number(latest_balance_sheet.get('commonStockSharesOutstanding'))
                }
            }

            income_statement = {
                'Revenue': {
                    'Total Revenue': format_number(latest_income_statement.get('totalRevenue')),
                },
                'Cost and Expenses': {
                    'Cost of Revenue': format_number(latest_income_statement.get('costOfRevenue')),
                    'Cost of Goods and Services Sold': format_number(latest_income_statement.get('costofGoodsAndServicesSold')),
                    'Gross Profit': format_number(latest_income_statement.get('grossProfit')),
                    'Operating Expenses': format_number(latest_income_statement.get('operatingExpenses')),
                    'Selling, General, and Administrative': format_number(latest_income_statement.get('sellingGeneralAndAdministrative')),
                    'Research and Development': format_number(latest_income_statement.get('researchAndDevelopment')),
                    'Depreciation and Amortization': format_number(latest_income_statement.get('decpreciationAndAmortization')),
                    'Depreciation': format_number(latest_income_statement.get('depreciation')),
                },
                'Operating Income': {
                    'Operating Income': format_number(latest_income_statement.get('operatingIncome')),
                },
                'Non-Operating Income': {
                    'Interest Income': format_number(latest_income_statement.get('interestIncome')),
                    'Interest Expense': format_number(latest_income_statement.get('interestExpense')),
                    'Interest and Debt Expense': format_number(latest_income_statement.get('interestAndDebtExpense')),
                    'Net Interest Income': format_number(latest_income_statement.get('netInterestIncome')),
                    'Investment Income Net': format_number(latest_income_statement.get('investmentIncomeNet')),
                    'Non-Interest Income': format_number(latest_income_statement.get('nonInterestIncome')),
                    'Other Non-Operating Income': format_number(latest_income_statement.get('otherNonOperatingIncome')),
                },
                'Income Before Tax': {
                    'Income Before Tax': format_number(latest_income_statement.get('incomeBeforeTax')),
                    'Income Tax Expense': format_number(latest_income_statement.get('incomeTaxExpense')),
                },
                'Net Income': {
                    'Net Income': format_number(latest_income_statement.get('netIncome')),
                    'Net Income From Continuing Operations': format_number(latest_income_statement.get('netIncomeFromContinuingOperations')),
                },
                'Comprehensive Income': {
                    'Comprehensive Income Net of Tax': format_number(latest_income_statement.get('comprehensiveIncomeNetOfTax')),
                },
                'EBIT and EBITDA': {
                    'EBIT (Earnings Before Interest and Taxes)': format_number(latest_income_statement.get('ebit')),
                    'EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization)': format_number(latest_income_statement.get('ebitda')),
                }
            }
            
            return {
                "balance_sheet": balance_sheet,
                "income_statement": income_statement,
                "ratios": ratios,
                "fiscal_date_ending": latest_balance_sheet.get('fiscalDateEnding')
            }
    
    # If we reach this point, either the API call failed or the data was not in the expected format
    logger.error(f"API Response (Balance Sheet): {balance_sheet_response.text}")
    logger.error(f"API Response (Income Statement): {income_statement_response.text}")
    return None

def get_stock_news(ticker, api_key):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ticker,
        "apikey": api_key,
        "limit": 10
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "feed" in data:
            return data["feed"]
    return None

def get_macro_news(api_key):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "topics": "economy_macro",
        "apikey": api_key,
        "limit": 10
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "feed" in data:
            return data["feed"]
    return None

def get_newsapi_articles():
    newsapi_key = get_newsapi_key()
    base_url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": newsapi_key,
        "country": "us",
        "category": "business",
        "pageSize": 10
    }
    logging.debug(f"Making request to NewsAPI: {base_url}")
    response = requests.get(base_url, params=params)
    logging.debug(f"NewsAPI response status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if "articles" in data:
            return data["articles"]
    logging.error(f"Failed to fetch news from NewsAPI. Status code: {response.status_code}")
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form['ticker'].upper()
        api_key = get_api_key()
        financial_data = get_financial_data(ticker, api_key)
        stock_news = get_stock_news(ticker, api_key)
        macro_news = get_macro_news(api_key)
        newsapi_articles = get_newsapi_articles()
        
        if financial_data:
            return render_template('result.html', 
                                   ticker=ticker, 
                                   financial_data=financial_data, 
                                   stock_news=stock_news,
                                   macro_news=macro_news,
                                   newsapi_articles=newsapi_articles)
        else:
            error_message = f"No financial data found for {ticker}. Please check the ticker symbol and try again."
            return render_template('index.html', error=error_message)
        
    return render_template('index.html')

@app.route('/news')
def news_page():
    api_key = get_api_key()
    macro_news = get_macro_news(api_key)
    newsapi_articles = get_newsapi_articles()
    return render_template('news.html', macro_news=macro_news, newsapi_articles=newsapi_articles)

def get_macro_news(api_key):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "topics": "economy_macro",
        "apikey": api_key,
        "limit": 10
    }
    response = requests.get(base_url, params=params)
    logger.debug("API Response Status: %s", response.status_code)
    logger.debug("API Response Content: %s", response.text[:500])  # Print first 500 characters
    
    if response.status_code == 200:
        data = response.json()
        if "feed" in data:
            return data["feed"]
    return None

# Add this new function to get news based on selected categories
def get_custom_news(api_key, categories):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "topics": ",".join(categories),
        "apikey": api_key,
        "limit": 50  # Increased limit to get more news items
    }
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if "feed" in data:
            return data["feed"]
    return None

@app.route('/customize', methods=['GET', 'POST'])
def customize_news():
    categories = [
        'economy_macro', 'economy_monetary', 'economy_fiscal', 'economy_forex',
        'finance', 'life_sciences', 'manufacturing', 'real_estate',
        'retail_wholesale', 'technology'
    ]
    
    if request.method == 'POST':
        selected_categories = request.form.getlist('categories')
        print(f"Selected categories: {selected_categories}")  # Debug print
        session['selected_categories'] = selected_categories
        return redirect(url_for('custom_news_feed'))
    
    return render_template('customize_news.html', categories=categories)

@app.route('/custom_news_feed')
def custom_news_feed():
    selected_categories = session.get('selected_categories', [])
    print(f"Retrieved categories from session: {selected_categories}")  # Debug print
    api_key = get_api_key()
    custom_news = get_custom_news(api_key, selected_categories)
    print(f"Custom news retrieved: {'Yes' if custom_news else 'No'}")  # Debug print
    return render_template('custom_news_feed.html', custom_news=custom_news, selected_categories=selected_categories)

def get_custom_news(api_key, categories):
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": "NEWS_SENTIMENT",
        "topics": ",".join(categories),
        "apikey": api_key,
        "limit": 50
    }
    print(f"API request parameters: {params}")  # Debug print
    response = requests.get(base_url, params=params)
    print(f"API response status code: {response.status_code}")  # Debug print
    
    if response.status_code == 200:
        data = response.json()
        if "feed" in data:
            return data["feed"]
        else:
            print(f"No 'feed' in API response. Response content: {data}")  # Debug print
    else:
        print(f"API request failed. Response content: {response.text}")  # Debug print
    return None

if __name__ == '__main__':
    app.run(debug=True)