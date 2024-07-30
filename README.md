# jatsConverter

This is a python script meant to convert [Jats XML](https://jats.nlm.nih.gov/) to a basic static HTML.

typical call for conversion to MD (to load into Jupyter Notebooks for further conversion)
```
python Converter.py name_of.xml JatsConversionStylesheet.xslt
```

typical call for conversion to HTML
```
python ConvertToHTML.py name_of.xml ConversionHTML.xslt
```

typical call for conversion to HTML for a journal with journal-specific settings
```
python ConvertToHTML.py name_of.xml ConversionHTML.xslt jhok
```

## Supported JATS XML elements
This converter does not support all possible JATS XML elements. The aim is to support these elements:

| **Element**              | **Description**                                                                                  |
|--------------------------|--------------------------------------------------------------------------------------------------|
| `article`                | Processes the `<front>` and `<body>` tags within the root element.                              |
| `front`                  | Processes the `<journal-meta>` and `<article-meta>` elements inside `<front>`.                   |
| `journal-meta`           | Extracts and transforms journal information (title, ISSNs, publisher, and location).            |
| `article-meta`           | Extracts and transforms article information (ID, DOI, category, title, authors, date, volume, issue, pages). |
| `body`                   | Processes all elements within `<body>`.                                                         |
| `title`                  | Transforms `<title>` elements into HTML headers with a preceding `<br>` element.                |
| `p`                      | Transforms paragraphs.                                                                          |
| `ext-link`               | Transforms external links.                                                                      |
| `fig`                    | Transforms figures, including images and captions.                                              |
| `caption`                | Transforms captions by wrapping the content in `<em>` tags.                                     |
| `table-wrap`             | Transforms table wraps, including the ID attribute in text form.                                |
| `sc`                     | Transforms small caps elements by converting the text to uppercase.                             |
| `italic`                 | Transforms italic text.                                                                         |
| `bold`                   | Transforms bold text.                                                                           |
| `xref[@ref-type='bibr']` | Transforms bibliographic references.                                                            |
| `sup[xref[@ref-type='fn']]` | Transforms footnote references within superscript tags.                                         |
| `xref[@ref-type='fn']`   | Transforms footnote references.                                                                 |
| `ext-link[@ext-link-type='doi']` | Transforms DOI external links.                                                             |
| `*`                      | Applies templates to any other elements not explicitly matched.                                 |
