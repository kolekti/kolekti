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

  <xsl:import href="WWWProjectView.xsl"/>

  <xsl:output method="xml" indent="yes"/>

  <xsl:variable name="project" select="kf:get_http_data('kolekti', 'project')" />

  <xsl:template match="/">
    <html>
      <head>
        <title><xsl:call-template name="pagetitle" /></title>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <meta name="description" content="kOLEKTi" />
        <meta name="keywords" content="custom documents generator" />
        <link href="/_lib/kolekti/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
        <link href="/_lib/app/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
        <link href="/_lib/app/css/kolekti-translate.css" media="all" rel="stylesheet" type="text/css" />
      </head>
      <body>
        <xsl:call-template name="topmenu" />
        <xsl:apply-templates />
        <div id="ajax-indicator" style="display:none;">
          <span><i:text>[0103]Chargement...</i:text></span>
        </div>
        <xsl:call-template name="footer" />
      </body>
    </html>
  </xsl:template>

  <xsl:template match="kcd:data">
    <div class="" id="main">
      <div id="content">
        <div id="splitcontentleft" style="width: 50%;">
          <xsl:call-template name="mainleft" />
        </div>
        <div id="splitcontentright" style="width: 46%;">
          <xsl:call-template name="mainright" />
        </div>
      </div>
    </div>
  </xsl:template>

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
        <li>
          <a class="home" href="{$projectdir}" title="{$projectdesc}"><i:text>[0208]Accueil</i:text></a>
        </li>
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

  <xsl:template match="kcd:view">
    <div id="header">
      <h1>
         <a href="{$projectdir}/translate"><xsl:value-of select="$project/@name"/></a>
         <xsl:if test="$projectdesc">
           <span style="font-size:50%"><xsl:value-of select="$project/@name"/></span>
         </xsl:if>
      </h1>
    </div>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template name="mainleft">
     <h2><i:text>[0296]Transférer une enveloppe</i:text></h2>
     <div class="translatecontent">
      <iframe src="{$projectdir}/translate?upload=1" id="uploadframe">
        <xsl:text>&#x0D;</xsl:text>
      </iframe>
     </div>
  </xsl:template>

  <xsl:template name="mainright">
   <h2><i:text>[0242]Historique</i:text></h2>
   <div class="logs">
      <table>
        <thead>
          <th><i:text>[0243]Nom de l'enveloppe</i:text></th>
          <th><i:text>[0244]Date de l'ajout</i:text></th>
          <th><i:text>[0172]Auteur</i:text></th>
        </thead>
        <tbody>
          <xsl:apply-templates select="/kcd:view/kcd:data/kcd:namespace[@id='kolekti']/kcd:value[@key='loglistmasters']/listfiles/file">
            <xsl:sort select="@time" order="descending" />
          </xsl:apply-templates>
        </tbody>
      </table>
   </div>
  </xsl:template>

  <xsl:template match="kcd:namespace[@id='kolekti']/kcd:value[@key='loglistmasters']/listfiles/file">
   <xsl:variable name="masterfile" select="substring-after(@resid, 'masters/')" />
   <tr>
     <td><a href="{$projectdir}/masters?open={$masterfile}"><xsl:value-of select="$masterfile" /></a></td>
     <td><xsl:value-of select="kf:format_time(string(@time))" /></td>
     <td><xsl:value-of select="kf:username(string(@uid))" /></td>
   </tr>
  </xsl:template>

  <xsl:template name="footer">
    <div id="footer">
      <i:text>[0133]Propulsé par</i:text> <a href="http://www.kolekti.org/">kOLEKTi </a> <!-- <ke:version/> --> © 2007-2009 Stéphane Bonhomme - Vincent Bidaux
    </div>
  </xsl:template>
</xsl:stylesheet>
