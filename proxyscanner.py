import requests
from bs4 import BeautifulSoup
import concurrent.futures

# Function to scrape proxies from a website
def scrape_proxies(url):
    proxies = []
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table')
            if table:
                for row in table.tbody.find_all('tr'):
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        protocol = 'https' if (len(cols) > 6 and cols[6].text.strip().lower() == 'yes') else 'http'
                        proxies.append((protocol, ip, port))
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
    return proxies

# Function to test proxies
def test_proxies(proxies):
    working_proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in proxies}
        for future in concurrent.futures.as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                if future.result():
                    working_proxies.append(proxy)
            except Exception as e:
                print(f"Error testing proxy {proxy}: {e}")
    return working_proxies

# Function to test a single proxy
def test_proxy(proxy):
    protocol, ip, port = proxy
    try:
        response = requests.get('https://www.example.com', proxies={protocol: f'{protocol}://{ip}:{port}'}, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

# Function to read URLs from a text file
def read_urls(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

# Aggregate proxies from multiple URLs
def aggregate_proxies(urls):
    all_proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(scrape_proxies, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                proxies = future.result()
                all_proxies.extend(proxies)
            except Exception as e:
                print(f"Error scraping {url}: {e}")
    return all_proxies

# Function to save proxies to a file sorted by port number
def save_proxies(proxies, file_path):
    sorted_proxies = sorted(proxies, key=lambda x: int(x[2]))  # Sort by port number
    with open(file_path, 'w') as file:
        for protocol, ip, port in sorted_proxies:
            file.write(f'{protocol}://{ip}:{port}\n')

# Main function
if __name__ == "__main__":
    url_file = 'urls.txt'
    output_file = 'sorted_proxies.txt'
    
    urls = read_urls(url_file)
    proxies = aggregate_proxies(urls)
    
    working_proxies = test_proxies(proxies)
    
    save_proxies(working_proxies, output_file)
    
    print(f"Working proxies saved to {output_file}")
