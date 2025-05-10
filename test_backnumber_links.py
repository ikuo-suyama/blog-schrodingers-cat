import requests
from bs4 import BeautifulSoup
import time

SERVER_URL = "http://localhost:8080"
TEST_URL = f"{SERVER_URL}/ikuoikuo_2005/e/4846a3e02780eec9e21428510723d478.html"  # Use a sample article

def get_backnumber_links(url):
    """Extract backnumber links from the given URL"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: Could not access {url}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Dump the HTML content to a file for debugging
        with open('debug_html.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Print all h4 elements for debugging
        print("All h4 elements found:")
        for idx, h4 in enumerate(soup.find_all('h4')):
            print(f"  {idx}: {h4.text}")
        
        # Find the backnumber section using a more flexible approach
        backnumber_module = None
        
        # Try to find it by the module ID
        backnumber_module = soup.find('div', id='mod-back-numbers-scroll')
        
        if not backnumber_module:
            # If not found by ID, try to find it by heading text
            for h4 in soup.find_all('h4'):
                if 'バックナンバー' in h4.text:
                    backnumber_module = h4.find_parent('div', class_='module')
                    break
        
        if not backnumber_module:
            print(f"Error: Could not find backnumber module in {url}")
            return []
        
        # Find all links in the backnumber module
        links = []
        for a_tag in backnumber_module.find_all('a', href=True):
            href = a_tag['href']
            if '/m/' in href or href.startswith('/ikuoikuo_2005/m/'):
                links.append((a_tag.text, href))
        
        return links
    
    except Exception as e:
        print(f"Error accessing {url}: {str(e)}")
        return []

def test_backnumber_link(url):
    """Test if a backnumber link works correctly"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            print(f"Error: {url} returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error accessing {url}: {str(e)}")
        return False

def main():
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Get backnumber links from the test URL
    print(f"Getting backnumber links from {TEST_URL}...")
    links = get_backnumber_links(TEST_URL)
    
    if not links:
        print("No backnumber links found.")
        return
    
    print(f"Found {len(links)} backnumber links.")
    
    # Test a sample of the links (to avoid testing all of them)
    sample_links = links[:5]  # First 5 links
    print(f"Testing {len(sample_links)} sample links...")
    
    success_count = 0
    for text, href in sample_links:
        # Convert relative URL to absolute URL
        if href.startswith('/'):
            url = SERVER_URL + href
        else:
            url = href
        
        print(f"Testing: {text} -> {url}")
        if test_backnumber_link(url):
            print(f"✅ {text} -> {url} - OK")
            success_count += 1
        else:
            print(f"❌ {text} -> {url} - Failed")
    
    print(f"\nResults: {success_count}/{len(sample_links)} backnumber links work correctly")

if __name__ == "__main__":
    main() 