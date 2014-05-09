<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kcd="kolekti:ctrdata"
                xmlns:kd="kolekti:dialogs"

                extension-element-prefixes="ke"
                exclude-result-prefixes="i kf ke kcd kd">

  <xsl:output method="xml" indent="yes" />

  <xsl:template name="pagetitle">Kolekti</xsl:template>

  <xsl:template match="/">
    <html>
      <head>
        <title><xsl:call-template name="pagetitle" /></title>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <meta name="description" content="kOLEKTi" />
        <meta name="keywords" content="custom documents generator" />
        <link href="/_lib/kolekti/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
        <link href="/_lib/app/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
      </head>
      <body>
        <xsl:call-template name="guiders" />
        <xsl:call-template name="topmenu" />
        <xsl:apply-templates />
        <div id="ajax-indicator" style="display:none;">
          <span><i:text>[0103]Chargement...</i:text></span>
        </div>
        <xsl:call-template name="footer" />
      </body>
    </html>
  </xsl:template>

  <xsl:template match="kcd:view">
    <div id="header">
      <h1>kOLEKTi</h1>
      <div id="main-menu">
        <ul>
          <li><a style="display:none">&#xA0;</a></li>
        </ul>
      </div>
    </div>
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template name="guiders" />

  <xsl:template name="topmenu">
    <xsl:variable name="auth" select="number(kcd:view/kcd:data/kcd:namespace[@id='auth']/kcd:value[@key='uid']) &gt; 0" />
    <div id="top-menu">
      <div id="account">
        <ul>
     <xsl:choose>
       <xsl:when test="$auth">
         <li><a href="/user/account" class="my-account"><i:text>[0078]Mon Compte</i:text></a></li>
         <li><a href="/logout" class="logout"><i:text>[0206]Déconnexion</i:text></a></li>
       </xsl:when>
       <xsl:otherwise>
         <li><a href="/login" class="logout"><i:text>[0207]Se connecter</i:text></a></li>
       </xsl:otherwise>
     </xsl:choose>
        </ul>
      </div>

      <ul>
        <li><a href="/" class="home"><i:text>[0208]Accueil</i:text></a></li>
        <li><a href="http://www.kolekti.org/projects/kolekti/wiki/" class="help"><i:text>[0209]Aide (wiki)</i:text></a></li>
        <li><a href="http://webchat.freenode.net/?channels=kolekti-support" class="help" target="_chat"><i:text>[0210]Entraide (chat)</i:text></a></li>
        <xsl:if test="kf:admin()">
          <li><a href="/admin" class="admin"><i:text>[0104]Administration</i:text></a></li>
        </xsl:if>
      </ul>
      <xsl:if test="$auth">
   <div id="loggedas"><i:text>[0211]Connecté en tant que</i:text><xsl:text> </xsl:text><em><xsl:value-of select="kf:username()"/></em></div>
      </xsl:if>
    </div>
  </xsl:template>

  <xsl:template match="kcd:namespace[@id='auth']"></xsl:template>

  <xsl:template match="kcd:namespace[@id='user']"></xsl:template>

  <xsl:template match="kcd:namespace[@id='http']/kcd:value[@key='body']">
    <div class="" id="main">
      <div id="content">
        <xsl:choose>
          <xsl:when test="/kcd:view/kcd:http/@path = '/'">
            <div id="maincontent">
              <xsl:call-template name="maincontent" />
            </div>
          </xsl:when>
          <xsl:otherwise>
            <div id="splitcontentleft">
              <xsl:call-template name="mainleft" />
            </div>
            <div id="splitcontentright">
              <xsl:call-template name="mainright" />
            </div>
          </xsl:otherwise>
        </xsl:choose>
      </div>
    </div>
  </xsl:template>

  <xsl:template name="mainleft"> </xsl:template>

  <xsl:template name="mainright"> </xsl:template>

  <xsl:template name="maincontent">
    <div class="box">
      <h2><i:text>[0105]Projets</i:text></h2>
      <xsl:apply-templates select="projects" mode="maincontent" />
    </div>
  </xsl:template>

  <xsl:template match="projects" mode="maincontent">
    <xsl:choose>
      <xsl:when test="project">
        <ul>
          <xsl:apply-templates select="project" mode="maincontent" />
        </ul>
      </xsl:when>
      <xsl:otherwise>
        <p><i:text>[0245]Vous n'avez accès à aucun projet</i:text></p>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="project" mode="maincontent">
    <xsl:variable name="folder">
      <xsl:if test="kf:translator() = 'True'"><xsl:text>/translate</xsl:text></xsl:if>
    </xsl:variable>
    <li><a href="/projects/{@dir}{$folder}"><xsl:value-of select="@name" /></a></li>
  </xsl:template>

  <xsl:template name="footer">
    <div id="footer">
      <i:text>[0133]Propulsé par</i:text><xsl:text> </xsl:text><a href="http://www.kolekti.org/">kOLEKTi</a> <!-- <ke:version/> --> © 2007-2011 Stéphane Bonhomme - Vincent Bidaux
    </div>
  </xsl:template>

  <xsl:template name="tab">
    <xsl:param name="label" />
    <xsl:param name="link" />
    <xsl:param name="current" />
    <li>
      <a href="{$link}">
        <xsl:if test="$current">
          <xsl:attribute name="class">selected</xsl:attribute>
        </xsl:if>
        <xsl:copy-of select="$label" />
      </a>
    </li>
  </xsl:template>
</xsl:stylesheet>