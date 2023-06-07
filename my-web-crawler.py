from argparse import ArgumentParser as ap
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

visited_links = set()
file_counts = {}
files = {}

def crawl(url, threshold, output_file):
    
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    def extract_file_type(link):
        # Extract the file extension from the link
        parsed_url = urlparse(link)
        path = parsed_url.path
        file_type = path.split("/")[-1].split(".")[-1].lower() if "." in path else None
        return file_type

    def process_link(link, depth):
        if link in visited_links or depth > threshold:
            return

        visited_links.add(link)
        response = requests.get(link, allow_redirects=True)

        if response.status_code != 200:
            return

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all(["a", "link", "script", "img"])

        for link in links:
            href = link.get("href")
            src = link.get("src")

            if href:
                href = urljoin(url, href)
                parsed_href = urlparse(href)
                newdom = parsed_href.netloc

                file_type = extract_file_type(href)
                if file_type:
                    file_counts[file_type] = file_counts.get(file_type, 0) + 1
                    files.setdefault(file_type, []).append(href)
                    #if output_file:
                    #    output_file.write(f"{href}\n")
                if newdom == domain:
                    process_link(href, depth + 1)

            if src:
                src = urljoin(url, src)
                parsed_src = urlparse(src)
                newdom = parsed_src.netloc
                
                file_type = extract_file_type(src)
                if file_type:
                    file_counts[file_type] = file_counts.get(file_type, 0) + 1
                    files.setdefault(file_type, []).append(src)
                    #if output_file:
                    #    output_file.write(f"{src}\n")
                if newdom == domain:
                    process_link(src, depth + 1)

    process_link(url, 1)
    if not output_file:
        print(f"At recursion level {threshold}")
        print("Total files found:", sum(file_counts.values()))
        for file_type, links in files.items():
            print(file_type.capitalize() + ":" + str(len(links)))
            for link in links:
                print(link)
    else:
        with open(output_file,"w") as f:
            f.write(f"At recursion level {threshold}\n")
            f.write("Total files found:"+ str(sum(file_counts.values()))+"\n")
            for file_type, links in files.items():
                f.write(file_type.capitalize() + ":" + str(len(links))+"\n")
                for link in links:
                    f.write(link+"\n")  
            

if __name__ == "__main__":
    parser = ap()
    parser.add_argument("-u", "--url", type=str, required=True)
    parser.add_argument("-t", "--threshold", type=int, default=float('inf'))
    parser.add_argument("-o", "--output", type=str)
    
    args = parser.parse_args()
    
    url = args.url
    threshold = args.threshold
    output = args.output
    
    if not output:
        crawl(url,threshold,None)
    else:
        crawl(url,threshold,output)

