# jatsConverter

This is a python script meant to convert Jats XML to a basic static HTML.

typical call for conversion to MD (to load into Jupyter Notebooks for further conversion)
```
python Converter.py name_of.xml JatsConversionStylesheet.xslt
```

typical call for conversion to HTML
```
python ConvertToHTML.py name_of.xml ConversionHTML.xslt jhok
```

typical call for conversion to HTML for a journal with journal-specific settings
```
python ConvertToHTML.py name_of.xml ConversionHTML.xslt jhok
```
