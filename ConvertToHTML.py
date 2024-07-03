#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import xml.etree.ElementTree as ET
from lxml import etree
import sys

import Converter


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
    title = Converter.gen_title_bmgn(input_file) #create a title from the XML
    
    if reference_style == 'a':
        if Converter.contains_tag(input_file, 'xref', 'bibr'):
            reference_style = 'ref'
            print('detected ref')
            
        elif Converter.contains_tag(input_file, 'xref', 'fn'):
            reference_style = 'fn'
            print('detected fn')
        
    if reference_style == 'fn':
        markdown_file = Converter.add_footnotes_bottom(markdown_file, input_file)
        markdown_file = Converter.add_fn(markdown_file, input_file)
        
    elif reference_style == 'ref':       
        #replace tables here
        markdown_file = Converter.add_references_bottom(markdown_file, input_file)
        markdown_file = Converter.add_ref(markdown_file)
        
    final_product = title + '\n' + markdown_file #merge the generated title with the process front-free file
    
    with open('html.txt', 'w', encoding='utf-8') as final_file:
        final_file.write(final_product)


# In[3]:


if __name__ == '__main__':
    main()


# In[ ]:




