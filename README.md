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

