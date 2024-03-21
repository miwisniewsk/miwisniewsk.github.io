import requests
from bs4 import BeautifulSoup
import html2text
from googlesearch import search
import html

def download_page(url):
    response = requests.get(url)
    response.encoding = 'utf-8'

    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to download the page. Status code: {response.status_code}")
        return None

def extract_list_items(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    ul_list = soup.find('ul') 

    if ul_list:
        list_items = ul_list.find_all('li') 
        return list_items[:12] 
    else:
        print("No <ul> list found on the page.")
        return []

def extract_name_and_followers(text):
    print(text)

    dot_position = text.find(".")
    dash_position = text.find("-")
    M_position = text.find("M")

    extracted_name = text[dot_position + 2:dash_position -1]
    extracted_followers = text[dash_position + 2:M_position]
    return extracted_name, extracted_followers

def get_google_search_wikipedia_article(query):
    try:
        query = query + " wikipedia polski"
        search_results = search(query, num=1, stop=1, pause=10)

        return next(search_results)

    except Exception as e:
        return f"Error while Google search: {str(e)}"

def get_wikipedia_img(url):
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    desired_class = "mw-file-element"
    
    img_tags = soup.find_all('img', class_=desired_class)

    if img_tags:
        for img in img_tags:
            img_src = img.get('src')
            img_src = "https:" + img_src
            
            return img_src
    else:
        return None

def get_description_link(link):

    response = requests.get(link)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')
    desired_class = "about"

    div_tag = soup.find('div', class_=desired_class)

    if div_tag:
        p_tag = div_tag.find('p')
        if p_tag:
            text = p_tag.get_text(strip=True, separator=" ")
            text = text.replace(" .", ".")
            return text
        else:
            return None
    else:
        return None

def get_description(title):

    name = title.replace(" ", "-")
    name = name.replace("’", "-")
    name = name.lower()
    link = f"https://www.famousbirthdays.com/people/{name}.html"

    res = get_description_link(link)

    if res:
        return res
    else:
        query = title + " famous birthday"
        search_results = search(query, num=1, stop=1, pause=10)
        link = next(search_results)

        return get_description_link(link)

def valid_wikipedia_image(img_src):
    if img_src == 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/OOjs_UI_icon_edit-ltr.svg/100px-OOjs_UI_icon_edit-ltr.svg.png':
        return False
    elif 'Semi-protection-shackle' in img_src:
        return False
    elif 'Wiktionary-logo' in img_src:
        return False
    else:
        return True

def extract_items(html_content):
    items = extract_list_items(html_content)

    if not items:
        print("No items found on the page.")
        return []

    extracted_data = []

    for item in items:
        element = item.find('a')

        if element:
            title = element.get_text(strip=True)
            title, followers = extract_name_and_followers(title)

            #link = get_google_search_wikipedia_article(title)
            
            name = title.replace(" ", "_")
            name = name.replace("’", "'")
            link = f"https://en.wikipedia.org/wiki/{name}"
            print(link)

            img_src = get_wikipedia_img(link)
            if valid_wikipedia_image(img_src) == False:
                link = f"https://pl.wikipedia.org/wiki/{name}"
                print(link)
                img_src = get_wikipedia_img(link)
            
            description = get_description(title)

            extracted_data.append({
                'Title': title,
                'Description': description,
                'Link': link,
                'Img': img_src,
                'Followers': followers
            })
        else:
            print("Incomplete data for an item. Skipping.")

    return extracted_data

def convert_to_markdown(item):
    markdown_content = ""
    markdown_content += f"# {item['Title']}\n\n"
    markdown_content += f"{item['Description']}\n\n"
    markdown_content += f"![]({item['Img']})\n\n"
    markdown_content += f"You can find out more information in this Wikipedia article: [Wikipedia]({item['Link']})\n\n"

    return markdown_content

def save_to_markdown(markdown_content, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(markdown_content)

def save_to_markdown_subpage(markdown_content, output_file):
    with open(output_file, 'a+') as file:
        file.seek(0, 2)
        file.write(markdown_content)

def main():
    url = 'https://www.favikon.com/blog/the-20-most-famous-tiktok-influencers-in-the-world'  
    output_file = 'output.md' 

    html_content = download_page(url)

    if html_content:
        extracted_data = extract_items(html_content)

        save_to_markdown("# TikTok Influencers\n\n", output_file)
        short_description = "Here on this page, you can find top 10 Tiktok accounts with the most followers. Click on the name to find more information about the account.\n\n"
        save_to_markdown_subpage(short_description, output_file)

        if extracted_data:
            i = 0
            for item in extracted_data:
                if (item['Description'] != None and valid_wikipedia_image(item['Img'])):
                    i = i + 1 
                    subpage = item['Title'].replace(" ", "_") + ".md"

                    markdown_content = convert_to_markdown(item)

                    save_to_markdown(markdown_content, subpage)

                    subpage_content = f"{i}. [{item['Title']}]({subpage}) "
                    subpage_content += f"with {item['Followers']} milion followers\n\n"
        
                    save_to_markdown_subpage(subpage_content, output_file)
            
            print(f"Page content saved to {output_file}")
        else:
            print("No data to convert to Markdown.")

if __name__ == "__main__":
    main()
