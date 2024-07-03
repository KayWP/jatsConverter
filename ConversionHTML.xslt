<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xlink="http://www.w3.org/1999/xlink"
  exclude-result-prefixes="xlink">

  <xsl:output method="html" encoding="UTF-8"/>

  <!-- Transform the root element (usually "article") -->
  <xsl:template match="article">
    <!-- Process the <front> and <body> tags -->
    <xsl:apply-templates select="front"/>
    <xsl:apply-templates select="body"/>
  </xsl:template>

  <!-- Transform the <front> tag -->
  <xsl:template match="front">
    <!-- Process elements inside <front> -->
    <xsl:apply-templates select="journal-meta"/>
    <xsl:apply-templates select="article-meta"/>
  </xsl:template>

  <!-- Transform the <journal-meta> tag -->
  <xsl:template match="journal-meta">
    <!-- Extract and transform journal information -->
    <h1>Journal</h1>
    <p><strong>Title:</strong> <xsl:value-of select="journal-title-group/journal-title"/></p>
    <p><strong>ISSN (epub):</strong> <xsl:value-of select="issn[@pub-type='epub']"/></p>
    <p><strong>ISSN (ppub):</strong> <xsl:value-of select="issn[@pub-type='ppub']"/></p>
    <p><strong>Publisher:</strong> <xsl:value-of select="publisher/publisher-name"/></p>
    <p><strong>Publisher Location:</strong> <xsl:value-of select="publisher/publisher-loc"/></p>
  </xsl:template>

  <!-- Transform the <article-meta> tag -->
  <xsl:template match="article-meta">
    <!-- Extract and transform article information -->
    <h1>Article</h1>
    <p><strong>Article ID (Publisher):</strong> <xsl:value-of select="article-id[@pub-id-type='publisher-id']"/></p>
    <p><strong>DOI:</strong> <xsl:value-of select="article-id[@pub-id-type='doi']"/></p>
    <p><strong>Category:</strong> <xsl:value-of select="article-categories/subj-group/subject"/></p>
    <p><strong>Title:</strong> <xsl:value-of select="title-group/article-title"/></p>
    <xsl:if test="subtitle">
      <p><strong>Subtitle:</strong> <xsl:value-of select="subtitle"/></p>
    </xsl:if>
    <p><strong>Authors:</strong>
    <xsl:for-each select="contrib-group/contrib[@contrib-type='author']">
      <xsl:value-of select="normalize-space(name/surname)"/>
      <xsl:text>, </xsl:text>
      <xsl:value-of select="normalize-space(name/given-names)"/>
      <xsl:if test="position() != last()">
        <xsl:text>; </xsl:text>
      </xsl:if>
    </xsl:for-each>
    </p>
    <p><strong>Publication Date (epub):</strong> <xsl:value-of select="pub-date[@pub-type='epub']/year"/>-<xsl:value-of select="pub-date[@pub-type='epub']/month"/></p>
    <p><strong>Volume:</strong> <xsl:value-of select="volume"/></p>
    <p><strong>Issue:</strong> <xsl:value-of select="issue"/></p>
    <p><strong>Pages:</strong> <xsl:value-of select="fpage"/>-<xsl:value-of select="lpage"/></p>
  </xsl:template>

  <!-- Transform the <body> tag -->
  <xsl:template match="body">
    <xsl:apply-templates/>
  </xsl:template>

  <!-- Transform <title> elements into HTML headers with a <br> element before them -->
  <xsl:template match="title">
    <br/>
    <h3><xsl:apply-templates/></h3>
  </xsl:template>


  <!-- Transform paragraphs -->
  <xsl:template match="p">
    <p><xsl:apply-templates/></p>
  </xsl:template>

  <!-- Transform external links -->
  <xsl:template match="*[local-name()='ext-link']">
    <a href="{@xlink:href}"><xsl:apply-templates/></a>
  </xsl:template>

    <!-- Transform figures -->
  <xsl:template match="fig">
    <figure>
      <img src="{graphic/@xlink:href}" alt="Figure"/>
      <figcaption>
        <xsl:apply-templates select="caption"/>
      </figcaption>
    </figure>
  </xsl:template>

  <!-- Template to match caption elements -->
  <xsl:template match="caption">
    <em>
      <xsl:apply-templates/>
    </em>
  </xsl:template>



  <!-- Transform tables -->
  <xsl:template match="table-wrap">
    <xsl:text>[table wrap </xsl:text>
    <xsl:value-of select="@id"/>
    <xsl:text>]</xsl:text>
  </xsl:template>

  <!-- Transform the <sc> tag (capitalize its contents) -->
  <xsl:template match="sc">
    <xsl:value-of select="translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/>
  </xsl:template>

  <!-- Transform <italic> tags -->
  <xsl:template match="italic">
    <em><xsl:apply-templates/></em>
  </xsl:template>

  <!-- Transform <bold> tags -->
  <xsl:template match="bold">
    <strong><xsl:apply-templates/></strong>
  </xsl:template>

  <!-- Transform footnote references -->
  <xsl:template match="sup[xref[@ref-type='fn']]">
    <sup>[fn:<xsl:value-of select="xref/@rid"/>]</sup>
  </xsl:template>

  <xsl:template match="ext-link[@ext-link-type='doi']">
    <xsl:value-of select="."/>
  </xsl:template>

  <!-- Transform any other elements (not explicitly matched) -->
  <xsl:template match="*">
    <xsl:apply-templates/>
  </xsl:template>

</xsl:stylesheet>
