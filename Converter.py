#!/usr/bin/env python
# coding: utf-8

# In[17]:


import re
import xml.etree.ElementTree as ET
from markdownify import markdownify as md
from bs4 import BeautifulSoup
from lxml import etree
import sys
import pandas as pd


# In[2]:

#regexes:
p_fn = r'\[fn:fn(\d+)\]' #footnote in running text
p_tbl = r'\[tbl: tb(\d+)\]' #table
p_cptn = r'(?s)\*\_(.*?)\_\*' #caption for figures
p_url = r'https?:\/\/[^\s()]+'


# In[3]:


def apply_xslt(xml_string, xslt_path):
    """
    Apply XSLT transformation to an XML file and save the result to a text file.
    """
    xml_tree = etree.fromstring(xml_string)
    xslt_tree = etree.parse(xslt_path)
    transformer = etree.XSLT(xslt_tree)
    transformed_tree = transformer(xml_tree)
    
    return str(transformed_tree)


# In[4]:


def split_title_from_body(xml):
    #takes an xml file, reads it, returns an lxml.etree._ElementTree object without the 'front'
    tree = ET.parse(xml)
    tree = tree.getroot()
    tree.remove(tree.find('front'))

    string = ET.tostring(tree)
    
    return string


# In[5]:


def strip_ext_link_tags(text):
    # Define a regular expression pattern to match <ext-link> tags and their content
    pattern = r'<ext-link.*?href="(.*?)".*?>(.*?)</ext-link>|<ext-link.*?xlink:href="(.*?)".*?>(.*?)</ext-link>'
    
    # Use re.sub() to replace the matched text with the link text
    processed_text = re.sub(pattern, r'\2', text)
    
    return processed_text


# In[6]:


def capitalize_sc_tags(text):
    # Define a regular expression pattern to match <sc> tags and their content
    pattern = r'<sc>(.*?)</sc>'
    
    # Define a function to capitalize the matched text
    def capitalize(match):
        return match.group(1).upper()
    
    # Use re.sub() to replace the matched text with its capitalized form
    processed_text = re.sub(pattern, capitalize, text)
    
    # Remove the <sc> tags from the processed text
    processed_text = re.sub(r'<sc>|</sc>', '', processed_text)
    
    return processed_text


# In[7]:


def find_article_metadata_bmgn(xml):
    xml_tree = etree.parse(xml)
    
    # Find the article title and subtitle
    article_title_element = xml_tree.find('//article-title')
    article_subtitle_element = xml_tree.find('//subtitle')
    
    # Get text if elements are found, otherwise set to None
    article_title = article_title_element.text if article_title_element is not None else None
    article_subtitle = article_subtitle_element.text if article_subtitle_element is not None else None
    
    # Find the author names
    author_names = []
    for contrib in xml_tree.xpath('//contrib[@contrib-type="author"]'):
        surname = contrib.find('.//surname').text
        given_names = contrib.find('.//given-names').text
        full_name = f"{given_names} {surname}"
        author_names.append(full_name)
    
    # Find the DOI element
    doi_element = xml_tree.find('.//article-id[@pub-id-type="doi"]')
    doi = doi_element.text if doi_element is not None else None
    
    return article_title, article_subtitle, author_names, doi

def gen_title_bmgn(xml):
    title_info = find_article_metadata_bmgn(xml)
    
    # Handle potential None values in the title and subtitle
    title = f"# {title_info[0] if title_info[0] else 'No Title'}\n"
    subtitle = f"## {title_info[1]}" if title_info[1] else ""
    doi = f"[{title_info[3]}]({title_info[3]})\n\n" if title_info[3] else ""
    
    full_title = f"{title}{subtitle}\n{doi}"
    
    for author in title_info[2]:
        full_title += f"{author}\n"
    
    return full_title

def gen_title_html(xml):
    title_info = find_article_metadata_bmgn(xml)
    
    # Handle potential None values in the title and subtitle
    title = f"<h1>{title_info[0] if title_info[0] else 'No Title'}</h1>"
    subtitle = f"<h2>{title_info[1]}</h2>" if title_info[1] else ""
    doi = f'<a href="{title_info[3]}">{title_info[3]}</a><br><br>' if title_info[3] else ""
    
    full_title = f"{title}{subtitle}<br>{doi}"
    
    for author in title_info[2]:
        full_title += f"{author}<br>"

    full_title += '<br>'
    
    return full_title


# In[18]:


def table_convert(html_table):
    df = pd.read_html(html_table)
    return df[0].to_markdown()


# In[9]:


tag_dict = {
    'italic': '_',
    'bold': '**',
    'p': ''
}

closing_tag_dict = {
    'italic': '_',
    'bold': '**',
    'p': ''
}

opening_tag_dict_html = {
    'italic': '<em>',
    'bold': '<strong>',
    'p': '<p>'
}

closing_tag_dict_html = {
    'italic': '</em>',
    'bold': '</strong>',
    'p': '</p>'
}


def format_citation(input_string):
    # Define a regular expression pattern to match the <ext-link> tags and extract the DOI link
    pattern = r'<ext-link\s+ext-link-type="doi"\s+{http://www\.w3\.org/1999/xlink}href=".*">(.*)</ext-link'
    
    # Use re.sub to replace the matched pattern with the DOI link itself
    formatted_string = re.sub(pattern, r'\1', input_string)
    
    return formatted_string

def format_footnote(raw_footnote, opening_tag_dict, closing_tag_dict):
    # Replace XML tags with HTML tags based on dictionaries
    for tag in opening_tag_dict:
        open_tag = '<' + tag + '>'
        close_tag = '</' + tag + '>'
        raw_footnote = raw_footnote.replace(open_tag, opening_tag_dict[tag])
        raw_footnote = raw_footnote.replace(close_tag, closing_tag_dict[tag])
    
    # Capitalize content within <sc> tags
    raw_footnote = capitalize_sc_tags(raw_footnote)
    
    # Strip <ext-link> tags from the text
    raw_footnote = strip_ext_link_tags(raw_footnote)
    
    # Format citations if needed (assuming this function exists)
    raw_footnote = format_citation(raw_footnote)
    
    # Activate URLs
    raw_footnote = activate_urls(raw_footnote)
    
    return raw_footnote



# In[11]:


def get_text_recursively(element):
    """
    Recursively extract the XML structure of an element and its children as a string.
    """
    text = ''
    if element is not None:
        # Add the opening tag of the element
        text += f"<{element.tag}"
        # Add attributes of the element, if any
        for key, value in element.attrib.items():
            text += f" {key}=\"{value}\""
        text += ">"

        # If the element has text, add it to the result
        if element.text:
            text += element.text

        # Loop through the element's children
        for child in element:
            # Recursively get text from children
            text += get_text_recursively(child)

        # Add the closing tag of the element
        text += f"</{element.tag}>"

        # If the element has tail text, add it to the result
        if element.tail:
            text += element.tail
    return text

def extract_fn_contents(xml_file):
    # Initialize an empty dictionary to store the extracted content
    fn_dict = {}

    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Find all <fn> elements within the <fn-group>
    for fn in root.findall('.//fn-group/fn'):
        fn_id = fn.get('id')  # Get the fn id
        fn_label = fn.find('label').text  # Get the fn label
        fn_content = get_text_recursively(fn.find('p'))  # Get the fn content
        
        # Store the content in the dictionary using the label as the key
        fn_dict[fn_label] = fn_content

    return fn_dict

def contains_tag(xml_file, tag, ref_type):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        # Iterate over all elements with the specified tag
        for elem in root.iter(tag):
            # Check if the element has the attribute 'ref-type' with the desired value
            if elem.get('ref-type') == ref_type:
                return True
        return False
    except ET.ParseError:
        return False

def add_footnotes_bottom(txt, basexml):
    #this function constructs the text of the footnotes at the bottom of the page and adds them, one by one
    
    footnote_list = extract_fn_contents(basexml)
    
    txt += '\n'
    txt += '### Footnotes \n'
    
    for fn in footnote_list.keys():
        fnno = fn
        fntxt = footnote_list[fn]
        fntxt = format_footnote(fntxt, tag_dict)
        fnformula = "<a href=\"#_ftnref"+ fnno +'" name="_ftn' + fnno + '">[' + fnno +'] </a>' + fntxt
        txt += '\n'
        txt += '\n'
        txt += fnformula
    return txt

def add_footnotes_bottom_html(txt, basexml):
    #this function constructs the text of the footnotes at the bottom of the page and adds them, one by one
    
    txt += '<br>'
    txt += '<h3>Footnotes</h3>'

    footnote_list = extract_fn_contents(basexml)
    for fn in footnote_list.keys():
        fnno = fn
        fntxt = footnote_list[fn]
        fntxt = format_footnote(fntxt, opening_tag_dict_html, closing_tag_dict_html)
        fnformula = "<a href=\"#_ftnref"+ fnno +'" name="_ftn' + fnno + '">[' + fnno +'] </a>' + fntxt
        txt += '<br>'
        txt += '<br>'
        txt += fnformula
    return txt

def add_fn(txt, basexml):
    #this function replaces the placeholders in the text, added by the xslt, with actual active links referring to the
    #ftnref added in previously by add_footnotes_bottom
    
    footnote_list = extract_fn_contents(basexml)
    for fn in footnote_list.keys():
        fnid = 'fn' + fn
        #print(table)
        replacement = '<a href="#_ftn' + fn + '" name="_ftnref' + fn + '">[' + fn +  ']</a>'
        #print()
        #print(replacement)
        tobereplaced = '[fn:' + fnid + ']'
        #print(tobereplaced)
        txt = txt.replace(tobereplaced, replacement)
    return txt

def compose_ref_dict(text):
    # Define the regex pattern
    pattern = re.compile(r'\[(r\d+):([^\]]+)\]')
    
    # Find all matches in the text
    matches = pattern.findall(text)
    
    # Create the resulting dictionary
    result = {}
    for match in matches:
        entire_match = f'[{match[0]}:{match[1]}]'
        group1 = match[0]
        group2 = match[1]
        formatted_string = f'<a href="#_ftn{group1}" name="_ftnref{group1}">[{group2}]</a>'
        result[entire_match] = formatted_string
    
    return result

def add_ref(txt):
    ref_dict = compose_ref_dict(txt)
    
    for ref in ref_dict.keys():
        txt = txt.replace(ref, ref_dict[ref])
        
    return txt

def extract_ref_contents(xml_file):
    # Initialize an empty dictionary to store the extracted content
    ref_dict = {}

    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Find all <ref> elements within the <ref-list>
    for ref in root.findall('.//ref-list/ref'):
        ref_id = ref.get('id')  # Get the ref id
        ref_content = get_text_recursively(ref.find('mixed-citation'))  # Get the ref content
        
        # Store the content in the dictionary using the ref id as the key
        ref_dict[ref_id] = ref_content

    return ref_dict

def add_references_bottom(txt, basexml):
    reference_list = extract_ref_contents(basexml)
    
    txt += '\n'
    txt += '### References \n'

    for ref in reference_list.keys():
        ref_no = ref
        ref_text = reference_list[ref]
        ref_text = ref_text.strip('<mixed-citation>').strip('</mixed-citation>')
        ref_text = format_footnote(ref_text, opening_tag_dict_html, closing_tag_dict_html)
        ref_formula = "<a href=\"#_ftnref"+ ref_no +'" name="_ftn' + ref_no + '">[' + ref_no +'] </a>' + ref_text
        
        txt += '\n'
        txt += '\n'
        txt += ref_formula
        
    return txt

def add_references_bottom_html(txt, basexml):
    reference_list = extract_ref_contents(basexml)
    
    txt += '<br>'
    txt += '<h3>Footnotes</h3>'

    for ref in reference_list.keys():
        ref_no = ref
        ref_text = reference_list[ref]
        ref_text = ref_text.strip('<mixed-citation>').strip('</mixed-citation>')
        ref_text = format_footnote(ref_text, tag_dict)
        ref_formula = "<a href=\"#_ftnref"+ ref_no +'" name="_ftn' + ref_no + '">[' + ref_no +'] </a>' + ref_text
        
        txt += '<br>'
        txt += '<br>'
        txt += ref_formula
        
    return txt

# In[12]:


def activate_urls(text):
    urls = re.findall(p_url, text)
    formatted_text = text
    for url in urls:
        url = url.strip('.')
        markdown_link = f'<a href={url} target="blank">{url}</a>'
        formatted_text = formatted_text.replace(url, markdown_link)
    return formatted_text

def activate_ext_links(text):
    # Regular expression pattern to match <ext-link> tags with href attribute
    
    p_ext_link = r'<ext-link.*?href="(.*?)".*?>(.*?)<\/ext-link>'
    
    # Find all <ext-link> tags with href attribute and extract URLs and link text
    urls = re.findall(p_ext_link, text)
    
    # Process each URL and replace it with HTML link markup
    formatted_text = text
    for url, link_text in urls:
        markdown_link = f'<a href="{url}" target="blank">{link_text}</a>'
        formatted_text = formatted_text.replace(f'<ext-link.*?href="{url}">{link_text}</ext-link>', markdown_link)
    
    return formatted_text



# In[13]:


def main():
    tijdschrift = None
    try:
        input_file = sys.argv[1]
        style_file = sys.argv[2]
            
    except IndexError:
        print('Please input all the necessary command line variables')
    
    try:
        tijdschrift = sys.argv[3]
        print(f'using specific parameters for journal {tijdschrift}')

    except IndexError:
        pass


    if tijdschrift == 'BMGN':
        file_without_front = split_title_from_body(input_file) #split the front, so we can add the title info in the replace_title function
        markdown_file = apply_xslt(file_without_front, style_file)
        
        #replace tables here
        markdown_file = add_footnotes_bottom(markdown_file, input_file)
        markdown_file = add_fn(markdown_file, input_file)
        title = gen_title_bmgn(input_file) #create a title from the XML
        final_product = title + '\n' + markdown_file #merge the generated title with the process front-free file
    
    else:
        tree = ET.parse(input_file)
        tree = tree.getroot()
        
        input_string = ET.tostring(tree)

        markdown_file = apply_xslt(input_string, style_file)
        
        #replace tables here
        markdown_file = add_references_bottom(markdown_file, input_file)
        markdown_file = add_ref(markdown_file)
        final_product = markdown_file #merge the generated title with the process front-free file
    
    with open('markdown.txt', 'w', encoding='utf-8') as final_file:
        final_file.write(final_product)


# In[15]:


if __name__ == '__main__':
    main()

