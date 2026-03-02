import os
import time
import random
import pandas as pd
from ddgs import DDGS 
from email_validator import validate_email, EmailNotValidError
import requests
from bs4 import BeautifulSoup

def verify_email(email):
    """Checks if the email format is valid using email-validator."""
    if pd.isna(email) or str(email).strip() == "": return False
    try:
        validate_email(str(email).strip(), check_deliverability=False)
        return True
    except: return False

def get_linkedin_url(biz_name, website):
    """Finds LinkedIn URL via Website Scraping or DuckDuckGo Search (Privacy Safe)."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
    
    # Method 1: Website Scraping
    if not pd.isna(website) and str(website).lower() != "n/a":
        try:
            url = website if str(website).startswith('http') else 'https://' + str(website)
            res = requests.get(url, timeout=7, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href'].lower()
                if 'linkedin.com/company/' in href or 'linkedin.com/in/' in href:
                    return a['href']
        except: pass

    # Method 2: DuckDuckGo Search (Updated Syntax)
    try:
        query = f"{biz_name} USA linkedin profile"
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)
            for r in results:
                link = r.get('href', '')
                if 'linkedin.com/company/' in link or 'linkedin.com/in/' in link:
                    return link
    except: pass
    return "Not Found"

def main():
    # Automatically finds the desktop path without revealing PC username
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    
    print("==============================================")
    print("   Lead Verification & LinkedIn Finder Tool   ")
    print("==============================================")
    
    file_name = input("Enter your excel file name (e.g., input.xlsx): ")
    input_file = os.path.join(desktop_path, file_name)
    output_file = os.path.join(desktop_path, "verified_results.csv")

    if os.path.exists(input_file):
        print(f"Reading file: {file_name}...")
        df = pd.read_excel(input_file)
        final_data = []

        try:
            for index, row in df.iterrows():
                # Flexible Column Selection (A, B, E, F, H, I)
                name = row.iloc[0]
                web  = row.iloc[4]
                email = row.iloc[5]
                
                if verify_email(email):
                    print(f"[{index+1}] Verifying: {name}")
                    linkedin = get_linkedin_url(name, web)
                    
                    final_data.append({
                        "Business Name": name,
                        "Categories": row.iloc[1],
                        "Website": web,
                        "Email": email,
                        "LinkedIn": linkedin,
                        "Street Address": row.iloc[7],
                        "Locality": row.iloc[8]
                    })
                    time.sleep(random.uniform(1, 2)) # Anti-block delay
                
        except KeyboardInterrupt:
            print("\nStopped by user. Saving progress...")

        if final_data:
            pd.DataFrame(final_data).to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\nSuccess! Result saved to Desktop: verified_results.csv")
        else:
            print("\nNo valid data found.")
    else:
        print(f"Error: '{file_name}' not found on Desktop.")

if __name__ == "__main__":
    main()
