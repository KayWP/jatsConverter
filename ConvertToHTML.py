#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import xml.etree.ElementTree as ET
from lxml import etree
import sys

import Converter


# In[9]:


def construct_html_file(html_open, html_close, converted_article_text, xml):
    
    title = Converter.find_article_metadata_bmgn(xml)[0]
    
    file_name = title + '.html'
    
    with open(html_open, 'r', encoding='utf-8') as file:
        html_start = ''
        line = file.readline()

        while line:
            html_start += line
            line = file.readline()
            
    with open(html_close, 'r', encoding='utf-8') as file:
        html_end = ''
        line = file.readline()

        while line:
            html_end += line
            line = file.readline() 
    
    html_start.replace('[Hier moet de titel, deze tekst zou uniek moeten zijn, 030]', title)
    
    output = html_start + '\n' + converted_article_text + '\n' + html_end
    
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(output)    


# In[16]:


def convert_table_to_html(xml_string, table_id='tb001'):
    # Parse the XML
    root = ET.fromstring(xml_string)
    
    # Extract table elements
    label = root.find('label').text.strip()
    caption = root.find('.//caption').find('p').text.strip()
    thead_rows = root.find('.//thead').findall('tr')
    tbody_rows = root.find('.//tbody').findall('tr')

    # Start constructing HTML output
    html_output = f'''
    <table id="{table_id}" style="float: center;">
      <caption>{label} {caption}</caption>
      <thead>
    '''

    # Add thead rows to HTML output
    html_output += '    <tr>\n'
    for th in thead_rows[0].findall('th'):
        html_output += f'      <th>{th.text.strip()}</th>\n'
    html_output += '    </tr>\n'

    # Add tbody rows to HTML output
    html_output += '  </thead>\n  <tbody>\n'
    for tr in tbody_rows:
        html_output += '    <tr>\n'
        for td in tr.findall('td'):
            html_output += f'      <td>{td.text.strip()}</td>\n'
        html_output += '    </tr>\n'

    # Complete the HTML output
    html_output += '''
      </tbody>
    </table>
    '''

    return html_output


# In[8]:


def main():
    reference_style = 'a'
    style_file = 'ConversionHTML.xslt'

    try:
        input_file = sys.argv[1]
    except IndexError:
        print('Please input the input file as the first command line variable')
        return
    
    if len(sys.argv) > 2:
        style_file = sys.argv[2]

    if len(sys.argv) > 3:
        reference_style = sys.argv[3]
        if reference_style == 'ref' or reference_style == 'fn':
            print(f'Using specific reference style {reference_style}')
        else:
            print(f'{reference_style} is not a supported value, using automatic instead')
            reference_style = 'a'
    else:
        print('Using automatic reference style detection')

    print(f'Input file: {input_file}')
    print(f'Style file: {style_file}')
    print(f'Reference style: {reference_style}')
    
    file_without_front = Converter.split_title_from_body(input_file) #split the front, so we can add the title info in the replace_title function
    markdown_file = Converter.apply_xslt(file_without_front, style_file)
    
    markdown_file = Converter.add_tables(markdown_file, input_file)
    
    title = Converter.gen_title_html(input_file) #create a title from the XML
    
    if reference_style == 'a':
        if Converter.contains_tag(input_file, 'xref', 'bibr'):
            reference_style = 'ref'
            print('detected ref')
            
        elif Converter.contains_tag(input_file, 'xref', 'fn'):
            reference_style = 'fn'
            print('detected fn')
        
    if reference_style == 'fn':
        markdown_file = Converter.add_footnotes_bottom_html(markdown_file, input_file)
        markdown_file = Converter.add_fn(markdown_file, input_file)
        
    elif reference_style == 'ref':       
        #replace tables here
        markdown_file = Converter.add_references_bottom_html(markdown_file, input_file)
        markdown_file = Converter.add_ref(markdown_file)
        
    final_product = title + '\n' + markdown_file #merge the generated title with the process front-free file
    
    #with open('html.txt', 'w', encoding='utf-8') as final_file:
    #    final_file.write(final_product)
    
    construct_html_file('html_open.html', 'html_close.html', final_product, input_file)


# In[3]:


if __name__ == '__main__':
    main()


# In[ ]:




