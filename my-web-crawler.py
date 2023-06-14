from argparse import ArgumentParser as ap
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser as rbp
import matplotlib.pyplot as plt

#lists of links
visited_links = set()
file_counts = {}
files = {}
pie_value=[]
pie_label=[]

def extract_last_word(url):
#for getting url of sitemap from robots.txt
    # Retrieve the HTML content of the page
    response = requests.get(url)
    html_content = response.text

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the text content from the HTML
    text = soup.get_text()

    # Split the text into words
    words = text.split()

    # Retrieve the last word
    last_word = words[-1] if words else None

    return last_word
    
def extract_locs_from_sitemap(url):
#for getting urls from sitemap
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'xml')
    locs = soup.find_all('loc')
    loc_urls = [loc.text for loc in locs]
    return loc_urls

def check_robots(domain):
    robots_txt_url = "http://" + domain + "/robots.txt"
    response = requests.get(robots_txt_url)
    rp = rbp()
    rp.parse(response.text.splitlines())
    return rp

def crawl(url, threshold, output_file, robots):
#main crawler
    #get domain of url
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    robots_txt = check_robots(domain) if robots else None
    
    def extract_file_type(link):
        # Extract the file extension from the link
        parsed_url = urlparse(link)
        path = parsed_url.path
        file_type = path.split("/")[-1].split(".")[-1].lower() if "." in path else None
        return file_type

    def process_link(link, depth):
        #dont check visited links or go too deep
        if link in visited_links or depth > threshold:
            return

        visited_links.add(link)
        response = requests.get(link, allow_redirects=True)
        #deadends
        if response.status_code != 200:
            return
        #find all links
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all(["a", "link", "script", "img"])
        #get href and src links
        for link in links:
            href = link.get("href")
            src = link.get("src")

            if href:
                href = urljoin(url, href)
                parsed_href = urlparse(href)
                newdom = parsed_href.netloc
                #increment the corresponding filetype
                file_type = extract_file_type(href)
                if file_type:
                    file_counts[file_type] = file_counts.get(file_type, 0) + 1
                    files.setdefault(file_type, []).append(href)
                    #if robots flag is on check if it is in the rules
                if newdom == domain and (not robots_txt or robots_txt.can_fetch("*", href)):
                    #go deeper
                    process_link(href, depth + 1)

            if src:
                #similar to href but src
                src = urljoin(url, src)
                parsed_src = urlparse(src)
                newdom = parsed_src.netloc
                
                file_type = extract_file_type(src)
                if file_type:
                    file_counts[file_type] = file_counts.get(file_type, 0) + 1
                    files.setdefault(file_type, []).append(src)
                if newdom == domain and (not robots_txt or robots_txt.can_fetch("*", src)):
                    process_link(src, depth + 1)

    process_link(url, 1)
    if not output_file:
        #for printing on terminal
        if robots:
            print("Checking robots.txt")
            response = requests.get("https://"+domain+"/robots.txt")    
            if response.status_code == 200:
                print("robots.txt file found on", url)
                print("Checking sitemap")
                smap = extract_last_word("https://"+domain+"/robots.txt")
                response = requests.get(smap)
                if response.status_code == 200:
                    maplist = extract_locs_from_sitemap(smap)
                    print("Sitemap :")
                    for word in maplist:
                        print(word)
                else:
                    print("No sitemap found\n")
            else:
                print("No robots.txt file found on", url)
        else:
            print("Not checking for robots.txt")
        print(f"At recursion level {threshold}")
        print("Total files found:", sum(file_counts.values()))
        for file_type, links in files.items():
            pie_label.append(file_type)
            pie_value.append(len(links))
            print(file_type.capitalize() + ":" + str(len(links)))
            for link in links:
                print(link)
        print("Summary :")
        for i in range(len(pie_label)):
            print(pie_label[i]," : ",pie_value[i])
    else:
        #for printing in the output file
        with open(output_file,"w") as f:
            if robots:
                f.write("Checking robots.txt \n")
                response = requests.get("https://"+domain+"/robots.txt")    
                if response.status_code == 200:
                    f.write("robots.txt file found on "+ url+"\n")
                    f.write("Checking sitemap\n")
                    smap = extract_last_word("https://"+domain+"/robots.txt")
                    response = requests.get(smap)
                    if response.status_code == 200:
                         maplist = extract_locs_from_sitemap(smap)
                         f.write("Sitemap : "+str(len(maplist))+"\n")
                         for word in maplist:
                                f.write(word + "\n")
                         else:
                            f.write("No sitemap found\n")
                else:
                    f.write("No robots.txt file found on "+ url + "\n")
            else:
               f.write("Not checking for robots.txt \n")
            f.write(f"At recursion level {threshold}\n")
            f.write("Total files found:"+ str(sum(file_counts.values()))+"\n")
            for file_type, links in files.items():
                pie_label.append(file_type)
                pie_value.append(len(links))
                f.write(file_type.capitalize() + ":" + str(len(links))+"\n")
                for link in links:
                    f.write(link+"\n")
            f.write("Summary :\n")
            for i in range(len(pie_label)):
                f.write(pie_label[i]+" : "+str(pie_value[i])+"\n")
    plt.pie(pie_value,labels=pie_label)
    plt.savefig('pie.png')
    plt.close()

if __name__ == "__main__":
    #get arguments from cli
    parser = ap()
    parser.add_argument("-u", "--url", type=str, required=True)
    parser.add_argument("-t", "--threshold", type=int, default=float('inf'))
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument("-r", "--robot", action="store_true")
    
    args = parser.parse_args()
    
    url = args.url
    threshold = args.threshold
    output = args.output
    robots = args.robot
    
    if not output:
        print(r'''
        
                              ____      ____      __      
     \_______/               |_  _|    |_  _|    [  |         
 `.,-'\_____/`-.,'             \ \  /\  / /.---.  | |.--.   
  /`..'\ _ /`.,'\               \ \/  \/ // /__\\ | '/'`\ \ 
 /  /`.,' `.,'\  \               \  /\  / | \__., |  \__/ | 
/__/__/     \__\__\__      ______ \/  \/   '.__.'[__;.__.'  __                  
\  \  \     /  /  /      .' ___  |                         [  |                 
 \  \,'`._,'`./  /      / .'   \_| _ .--.  ,--.  _   _   __ | | .---.  _ .--.   
  \,'`./___\,'`./       | |       [ `/'`\]`'_\ :[ \ [ \ [  ]| |/ /__\\[ `/'`\]  
 ,'`-./_____\,-'`.      \ `.___.'\ | |    // | |,\ \/\ \/ / | || \__., | |      
     /       \           `.____ .'[___]   \'-;__/ \__/\__/ [___]'.__.'[___]     
                   ''')
        crawl(url,threshold,None,robots)
    else:
        crawl(url,threshold,output,robots)
