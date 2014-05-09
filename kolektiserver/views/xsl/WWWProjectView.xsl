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

  <xsl:import href="WWWView.xsl"/>

  <xsl:output method="xml" indent="yes"/>

  <xsl:variable name="currenttab">None</xsl:variable>
  <xsl:variable name="project" select="kf:get_http_data('kolekti', 'project')" />
  <xsl:variable name="projectdesc"><xsl:value-of select="$project/@description" /></xsl:variable>
  <xsl:variable name="projectdir">/projects/<xsl:value-of select="$project/@directory" /></xsl:variable>

  <xsl:key match="file|publication" use="@resid|@master" name="keyfiles"/>

  <xsl:template name="pagetitle"><xsl:value-of select="$project/@name" /><xsl:call-template name="tabtitle"/></xsl:template>
  <xsl:template name="tabtitle"/>

  <xsl:template name="metadata">
    <meta name="kolekti.project" content="{$project}"/>
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
      <kd:flags/>
      <h1>
        <a href="{$projectdir}">
          <xsl:value-of select="$project/@name"/>
        </a>
        <xsl:if test="$projectdesc">
          <span style="font-size:50%">
            <xsl:value-of select="$project/@name"/>
          </span>
        </xsl:if>
      </h1>
      <div id="main-menu">
        <ul>
          <xsl:call-template name="tabs">
            <xsl:with-param name="current"><xsl:value-of select="$currenttab"/></xsl:with-param>
          </xsl:call-template>
        </ul>
        <kd:svnrevision />
        <!-- Add panel control -->
        <xsl:call-template name="panelcontrol" />
      </div>
    </div>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="kcd:data">
    <div class="" id="main">
      <xsl:if test="/kcd:view/kcd:http/@path = $projectdir">
        <xsl:attribute name="class">projecthome</xsl:attribute>
      </xsl:if>
      <div id="content">
        <xsl:if test="/kcd:view/kcd:http/@path = $projectdir">
          <xsl:variable name="userprojects" select="kf:userprojects()" />
          <xsl:if test="count($userprojects) &gt; 1">
	          <div class="projectlist">
	            <label><i:text>[0212]Accéder au projet</i:text></label>
	            <select name="projectlist" onchange="kolekti.project_change(this.options[this.selectedIndex].value);">
	              <xsl:for-each select="$userprojects">
	                <option value="{@dir}">
	                  <xsl:if test="@dir = $project/@directory">
	                    <xsl:attribute name="selected">selected</xsl:attribute>
	                  </xsl:if>
	                  <xsl:value-of select="@name" />
	                </option>
	              </xsl:for-each>
	            </select>
	          </div>
          </xsl:if>
        </xsl:if>
        <div id="splitcontentleft">
          <xsl:call-template name="mainleft"/>
        </div>
        <div id="splitcontentright">
          <xsl:call-template name="mainright"/>
        </div>
        <xsl:if test="main">
          <div id="news">
            <xsl:call-template name="news" />
          </div>
        </xsl:if>
      </div>
    </div>
  </xsl:template>

  <xsl:template name="mainleft">
    <xsl:variable name="histo" select="/kcd:view/kcd:data/kcd:namespace[@id='kolekti']/kcd:value[@key='loglistorders']/listfiles/ordershistory" />
    <h2><i:text>[0328]Liste des lancements</i:text></h2>
    <div class="box">
      <xsl:call-template name="neworder" />
      <ul class="orders">
        <xsl:apply-templates select="kcd:namespace[@id='kolekti']/kcd:value[@key='orders']/orders/order">
         <xsl:sort select="$histo[@resid = concat(current()/@path, '/', current()/@src)]/@time" order="descending"/>
         <xsl:with-param name="histo" select="$histo" />
        </xsl:apply-templates>
      </ul>
    </div>
  </xsl:template>

  <xsl:template name="neworder">
    <xsl:variable name="src">configuration/orders/_</xsl:variable>
    <xsl:variable name="url" select="concat(/kcd:view/kcd:http/@path, '/', $src, '?viewer=orderseditor&amp;mode=detached')" />
    <xsl:variable name="config">
      <xsl:text>config='height=400, width=800, toolbar=no, menubar=no, scrollbars=no, resizable=no, location=no, directories=no, status=no'</xsl:text>
    </xsl:variable>
    <p class="itemsactions">
      <a href="#" onclick="window.open('{$url}', '_', {$config});"><i:text>[0213]Créer un lancement</i:text></a>
    </p>
  </xsl:template>

  <xsl:template match="orders/order">
    <xsl:param name="histo" />
    <xsl:variable name="curhisto" select="$histo[@resid = concat(current()/@path, '/', current()/@src)]" />
    <xsl:variable name="url" select="concat(@path, '/', @src, '?viewer=orderseditor&amp;mode=detached')" />
    <xsl:variable name="config">
      <xsl:text>config='height=400, width=800, toolbar=no, menubar=no, scrollbars=no, resizable=no, location=no, directories=no, status=no'</xsl:text>
    </xsl:variable>
    <li>
      <span class="itemsactions">
        <span class="itemaction" onclick="window.open('{$url}&amp;publish=1', '{@src}', {$config});">
          <img src="/_lib/app/icons/publish.png" i:alt="[0214]Publier" i:title="[0215]Publier le lancement" />
        </span>
      </span>
      <a href="#" onclick="window.open('{$url}', '{@src}', {$config});"><xsl:value-of select="@src" /></a>
      <xsl:if test="$curhisto">
        <span class="histo">
          <span class="date"><i:text>[0338]publié le</i:text><xsl:text> </xsl:text><xsl:value-of select="kf:format_time(string($curhisto/@time))"/></span>
          <xsl:if test="not(kf:userid() = $curhisto/@uid)">
            <span class="user"><xsl:text> </xsl:text><i:text>[0223]par</i:text><xsl:text> </xsl:text><xsl:value-of select="kf:username(string($curhisto/@uid))" /></span>
          </xsl:if>
        </span>
      </xsl:if>
    </li>
  </xsl:template>

  <xsl:template name="mainright">
   <h2><i:text>[0216]Actions récentes</i:text></h2>
   <div class="box">
      <xsl:choose>
        <xsl:when test="kcd:namespace[@id='kolekti']/kcd:value/listfiles/file">
           <xsl:if test="kcd:namespace[@id='kolekti']/kcd:value[@key='loglistmodules']/listfiles/file">
             <h3><i:text>[0022]Modules</i:text></h3>
             <ul class="listfiles">
               <xsl:comment>list of recents modules</xsl:comment>
               <xsl:apply-templates select="kcd:namespace[@id='kolekti']/kcd:value[@key='loglistmodules']/listfiles/file[generate-id()=generate-id(key('keyfiles',@resid)[last()])]">
                 <xsl:sort select="@time" order="descending"/>
                 <xsl:with-param name="showuser" select="true()"/>
               </xsl:apply-templates>
             </ul>
           </xsl:if>
           <xsl:if test="kcd:namespace[@id='kolekti']/kcd:value[@key='loglisttrames']/listfiles/file">
             <h3><i:text>[0029]Trames</i:text></h3>
             <ul class="listfiles">
               <xsl:comment>list of recents trames</xsl:comment>
               <xsl:apply-templates select="kcd:namespace[@id='kolekti']/kcd:value[@key='loglisttrames']/listfiles/file[generate-id()=generate-id(key('keyfiles',@resid)[last()])]">
                 <xsl:sort select="@time" order="descending"/>
                 <xsl:with-param name="showuser" select="true()"/>
               </xsl:apply-templates>
             </ul>
           </xsl:if>
           <xsl:if test="kcd:namespace[@id='kolekti']/kcd:value[@key='loglistlaunchers']/listfiles/file">
             <h3><i:text>[0217]Lancements</i:text></h3>
             <ul class="listfiles">
               <xsl:comment>list of recents orders</xsl:comment>
               <xsl:apply-templates select="kcd:namespace[@id='kolekti']/kcd:value[@key='loglistlaunchers']/listfiles/file[generate-id()=generate-id(key('keyfiles',@resid)[last()])]">
                 <xsl:sort select="@time" order="descending"/>
                 <xsl:with-param name="showuser" select="true()"/>
               </xsl:apply-templates>
             </ul>
           </xsl:if>
           <xsl:if test="kcd:namespace[@id='kolekti']/kcd:value[@key='loglistpublications']/listfiles/file">
             <h3><i:text>[0020]Enveloppes</i:text></h3>
             <ul class="listfiles">
               <xsl:comment>list of recents masters</xsl:comment>
               <xsl:apply-templates select="kcd:namespace[@id='kolekti']/kcd:value[@key='loglistpublications']/listfiles/publication[generate-id()=generate-id(key('keyfiles',@master)[last()])]">
                 <xsl:sort select="@time" order="descending"/>
                 <xsl:with-param name="showuser" select="true()"/>
               </xsl:apply-templates>
             </ul>
           </xsl:if>
         </xsl:when>
         <xsl:otherwise>
           <p class="info"><i:text>[0218]Aucune activité</i:text></p>
         </xsl:otherwise>
       </xsl:choose>
     </div>
   </xsl:template>

   <xsl:template match="kcd:value/listfiles/file"/>

   <xsl:template match="kcd:value[@key='loglistmodules']/listfiles/file">
     <xsl:param name="showuser"/>
     <xsl:if test="position() &lt;= 10">
       <xsl:call-template name="listfiles">
         <xsl:with-param name="ref" select="concat($projectdir, '/modules')" />
         <xsl:with-param name="label" select="substring-after(@resid, '/modules/')" />
         <xsl:with-param name="showuser" select="$showuser"/>
       </xsl:call-template>
     </xsl:if>
   </xsl:template>

   <xsl:template match="kcd:value[@key='loglisttrames']/listfiles/file">
     <xsl:param name="showuser"/>
     <xsl:if test="position() &lt;= 10">
       <xsl:call-template name="listfiles">
         <xsl:with-param name="ref" select="concat($projectdir, '/trames')" />
         <xsl:with-param name="label" select="substring-after(@resid, '/trames/')" />
         <xsl:with-param name="showuser" select="$showuser"/>
       </xsl:call-template>
     </xsl:if>
   </xsl:template>

   <xsl:template match="kcd:value[@key='loglistpubprofiles']/listfiles/file">
     <xsl:param name="showuser"/>
     <xsl:if test="position() &lt;= 10">
       <xsl:call-template name="listfiles">
         <xsl:with-param name="ref" select="concat($projectdir, '/configuration/publication_profiles')" />
         <xsl:with-param name="label" select="substring-after(@resid, '/configuration/publication_profiles/')" />
         <xsl:with-param name="showuser" select="$showuser"/>
       </xsl:call-template>
     </xsl:if>
   </xsl:template>

   <xsl:template match="kcd:value[@key='loglistlaunchers']/listfiles/file">
     <xsl:param name="showuser"/>
     <xsl:if test="position() &lt;= 10">
       <xsl:call-template name="listfiles">
         <xsl:with-param name="ref" select="concat($projectdir, '/configuration/orders')" />
         <xsl:with-param name="label" select="substring-after(@resid, '/configuration/orders/')" />
         <xsl:with-param name="showuser" select="$showuser"/>
       </xsl:call-template>
     </xsl:if>
   </xsl:template>

   <xsl:template match="kcd:value[@key='loglistpublications']/listfiles/publication[@master]">
     <xsl:param name="showuser"/>
     <xsl:if test="position() &lt;= 10">
       <xsl:call-template name="listfiles">
         <xsl:with-param name="ref" select="concat($projectdir, '/masters')" />
         <xsl:with-param name="label" select="@master" />
         <xsl:with-param name="showuser" select="$showuser"/>
       </xsl:call-template>
     </xsl:if>
   </xsl:template>

   <xsl:template name="listfiles">
     <xsl:param name="ref" />
     <xsl:param name="label" />
     <xsl:param name="showuser"/>
     <xsl:variable name="mylog" select="kf:userid() = @uid or (@uid='-1' and kf:userid()=kf:userid(string(@author)))"/>
     <li>
       <xsl:if test="$showuser and not($mylog)">
         <xsl:attribute name="class"><xsl:text>other_author</xsl:text></xsl:attribute>
       </xsl:if>
       <xsl:attribute name="title">
         <xsl:value-of select="concat('rev. ',@revnum,' : ',@msg)"/>
       </xsl:attribute>
       <!-- debug
       [    uid = <xsl:value-of select='@uid'/>,
         author = <xsl:value-of select='@author'/>]
       [  my  uid = <xsl:value-of select='kf:userid()'/>,
          ath uid = <xsl:value-of select='kf:userid(@author)'/>]
            -->
       <span class="owner">
         <xsl:choose>
           <xsl:when test="$mylog">
             <img src="/_lib/app/icons/user.png" i:alt="[0219]perso" i:title="[0220]Mon activité" />
           </xsl:when>
           <xsl:otherwise>
             <img src="/_lib/app/icons/owner.png" i:alt="[0221]autre" i:title="[0222]Activité du projet" />
           </xsl:otherwise>
         </xsl:choose>
       </span>
       <span class="link">
         <a href="{kf:id2url(string($ref))}?open={kf:id2url($label)}">
           <!-- <xsl:variable name="fname" select="kf:format_time(substring($label, 1, string-length($label)-4))" />
                <xsl:variable name="ext" select="substring($label, string-length($label)-2)" />
                <xsl:value-of select="concat($fname,'.', $ext)" />-->
                <xsl:value-of select="$label"/>
         </a>
       </span>
       <xsl:if test="$showuser and not($mylog)">
         <xsl:text> </xsl:text><i:text>[0223]par</i:text><xsl:text> </xsl:text><xsl:value-of select="kf:username(string(@uid), string(@author))" />
       </xsl:if>
       <xsl:text> (</xsl:text>
       <span class="date"><xsl:value-of select="kf:format_time(string(@time))"/></span>
       <xsl:text>)</xsl:text>
     </li>
   </xsl:template>

   <xsl:template name="news">
     <h3>kolekti News...</h3>
     <p> voir comment on peut repiquer les annonces du redmine .... (atom !)</p>
   </xsl:template>

   <xsl:template name="tabs">
     <xsl:param name="current"><xsl:value-of select="$currenttab"/></xsl:param>
     <xsl:call-template name="tab">
       <xsl:with-param name="label"><i:text>[0022]Modules</i:text></xsl:with-param>
       <xsl:with-param name="link"><xsl:value-of select="$projectdir"/>/modules</xsl:with-param>
       <xsl:with-param name="current" select="$current='modules'"/>
     </xsl:call-template>
     <xsl:call-template name="tab">
       <xsl:with-param name="label"><i:text>[0021]Medias</i:text></xsl:with-param>
       <xsl:with-param name="link"><xsl:value-of select="$projectdir"/>/medias</xsl:with-param>
       <xsl:with-param name="current" select="$current='medias'"/>
     </xsl:call-template>
     <xsl:call-template name="tab">
       <xsl:with-param name="label"><i:text>[0028]Tableurs</i:text></xsl:with-param>
       <xsl:with-param name="link"><xsl:value-of select="$projectdir"/>/sheets</xsl:with-param>
       <xsl:with-param name="current" select="$current='sheets'"/>
     </xsl:call-template>
     <xsl:call-template name="tab">
       <xsl:with-param name="label"><i:text>[0018]Styles</i:text></xsl:with-param>
       <xsl:with-param name="link"><xsl:value-of select="$projectdir"/>/design</xsl:with-param>
       <xsl:with-param name="current" select="$current='design'"/>
     </xsl:call-template>
     <xsl:call-template name="tab">
       <xsl:with-param name="label"><i:text>[0029]Trames</i:text></xsl:with-param>
       <xsl:with-param name="link"><xsl:value-of select="$projectdir"/>/trames</xsl:with-param>
       <xsl:with-param name="current" select="$current='trames'"/>
     </xsl:call-template>
     <xsl:call-template name="tab">
       <xsl:with-param name="label"><i:text>[0020]Enveloppes</i:text></xsl:with-param>
       <xsl:with-param name="link"><xsl:value-of select="$projectdir"/>/masters</xsl:with-param>
       <xsl:with-param name="current" select="$current='masters'"/>
     </xsl:call-template>
     <!--<xsl:call-template name="tab">
          <xsl:with-param name="label"><i:text>[0224]Pivot</i:text></xsl:with-param>
          <xsl:with-param name="link"><xsl:value-of select="$projectdir"/>/pivots</xsl:with-param>
          <xsl:with-param name="current" select="$current='pivots'"/>
        </xsl:call-template>-->
     <xsl:call-template name="tab">
       <xsl:with-param name="label"><i:text>[0025]Publications</i:text></xsl:with-param>
       <xsl:with-param name="link"><xsl:value-of select="$projectdir"/>/publications</xsl:with-param>
       <xsl:with-param name="current" select="$current='publications'"/>
     </xsl:call-template>
     <xsl:call-template name="tab">
       <xsl:with-param name="label"><i:text>[0225]Configuration</i:text></xsl:with-param>
       <xsl:with-param name="link"><xsl:value-of select="$projectdir"/>/configuration</xsl:with-param>
       <xsl:with-param name="current" select="$current='configuration'"/>
     </xsl:call-template>
   </xsl:template>

   <xsl:template name="panelcontrol">
     <kd:panelcontrol class="projectpanelcontrol">
        <kd:panel id="leftpanel" target="splitcontentleft">
           <kd:icons>
              <kd:icon-on i:title="[0226]Cacher le panneau gauche">/_lib/kolekti/icons/hide_browser.png</kd:icon-on>
              <kd:icon-off i:title="[0227]Afficher le panneau gauche">/_lib/kolekti/icons/show_browser.png</kd:icon-off>
           </kd:icons>
        </kd:panel>
        <kd:panel id="rightpanel" target="splitcontentright">
           <kd:icons>
              <kd:icon-on i:title="[0228]Cacher le panneau droite">/_lib/kolekti/icons/hide_view.png</kd:icon-on>
              <kd:icon-off i:title="[0229]Afficher le panneau droite">/_lib/kolekti/icons/show_view.png</kd:icon-off>
           </kd:icons>
        </kd:panel>
     </kd:panelcontrol>
   </xsl:template>
</xsl:stylesheet>
