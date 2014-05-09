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

  <xsl:import href="AdminForms.xsl" />
  <xsl:import href="WWWView.xsl" />

  <xsl:output method="xml" indent="yes" />

  <xsl:variable name="admin">
   <xsl:choose>
      <xsl:when test="substring-before(substring-after(/kcd:view/kcd:http/@path, '/'), '/')">
         <xsl:value-of select="substring-before(substring-after(/kcd:view/kcd:http/@path, '/'), '/')" />
      </xsl:when>
      <xsl:otherwise>
         <xsl:value-of select="substring-after(/kcd:view/kcd:http/@path, '/')" />
      </xsl:otherwise>
   </xsl:choose>
  </xsl:variable>

  <xsl:variable name="currenttab">
    <xsl:variable name="c" select="substring-after(/kcd:view/kcd:http/@path,concat('/',$admin,'/'))"/>
    <xsl:choose>
      <xsl:when test="contains($c,'/')">
   <xsl:value-of select="substring-before($c,'/')"/>
      </xsl:when>
      <xsl:when test="not($c)">projects</xsl:when>
      <xsl:otherwise>
   <xsl:value-of select="$c"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:template match="/">
    <html>
      <head>
        <title>
          <xsl:call-template name="pagetitle" />
        </title>
        <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
        <meta name="description" content="kOLEKTi" />
        <meta name="keywords" content="custom documents generator" />
        <link href="/_lib/kolekti/css/kolekti.css" media="all"
          rel="stylesheet" type="text/css" />
        <link href="/_lib/app/css/kolekti.css" media="all" rel="stylesheet"
          type="text/css" />
        <kd:kolektiadmin />
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

  <xsl:template match="kcd:view">
    <div id="header">
      <h1><i:text>[0104]Administration</i:text></h1>
      <div id="main-menu">
        <ul>
          <xsl:call-template name="tabs">
            <xsl:with-param name="current"><xsl:value-of select="$currenttab" /></xsl:with-param>
          </xsl:call-template>
        </ul>
      </div>
    </div>
    <xsl:apply-templates />
  </xsl:template>

  <xsl:template match="kcd:data">
   <div id="admincontent">   
    <xsl:call-template name="status"/>
    <xsl:choose>
     <xsl:when test="/kcd:view/kcd:http/@path='/admin/projects' or /kcd:view/kcd:http/@path='/admin'">
       <xsl:call-template name="admprojects"/>
     </xsl:when>
     <xsl:when test="starts-with(/kcd:view/kcd:http/@path,'/admin/projects/')">
       <xsl:call-template name="admproject"/>
     </xsl:when>
     <xsl:when test="/kcd:view/kcd:http/@path='/admin/users'">
       <xsl:call-template name="admusers"/>
     </xsl:when>
     <xsl:when test="starts-with(/kcd:view/kcd:http/@path,'/admin/users')">
       <xsl:call-template name="admuser"/>
     </xsl:when>
    </xsl:choose>
   </div>
  </xsl:template>

  <xsl:template name="tabs">
    <xsl:param name="current"><xsl:value-of select="$currenttab" /></xsl:param>    
    <xsl:call-template name="tab">
      <xsl:with-param name="label"><i:text>[0105]Projets</i:text></xsl:with-param>
      <xsl:with-param name="link" select="'/admin/projects'"/>
      <xsl:with-param name="current" select="$current='projects'"/>
    </xsl:call-template>

    <xsl:call-template name="tab">
      <xsl:with-param name="label"><i:text>[0106]Utilisateurs</i:text></xsl:with-param>
      <xsl:with-param name="link" select="'/admin/users'"/>
      <xsl:with-param name="current" select="$current='users'"/>
    </xsl:call-template>
  </xsl:template>

  <!-- Configuration -->
  <xsl:template name="admconfiguration">
   <div class="admincontent">
    <form class="tabular settings" method="post" action="/admin/configuration"> 
      <p>
       <label class="fieldtitle" for="lang"><i:text>[0107]Langue de travail</i:text></label>
       <input id="lang" name="lang" value="{kf:kolekticonf('lang')}" />
      </p>
      <input type="submit" i:value="[0083]Enregistrer"/>
    </form>
   </div>
  </xsl:template>

  <!-- Projects -->
  <xsl:template name="admprojects">
    <xsl:apply-templates select="kcd:namespace[@id='kolekti']/kcd:value[@key='projects']/projects"/>
  </xsl:template>

  <xsl:template match="projects">
    <form method="post" action="/{$admin}/projects"> 
      <table class="admin">
   <tbody>
     <tr>
       <th/>
       <th><i:text>[0079]Nom</i:text></th>
       <th><i:text>[0108]Répertoire</i:text></th>
       <th><i:text>[0109]Description</i:text></th>
       <th><i:text>[0107]Langue de travail</i:text></th>
     </tr>
     <xsl:for-each select="project">
       <tr>
         <td class="checkbox">
            <input type="checkbox" name="project" value="{@id}"/>
         </td>
         <td>
            <a href="/{$admin}/projects/params/{@id}"><xsl:value-of select="@name"/></a>
         </td>
         <td>
            <xsl:value-of select="@dir"/>
         </td>
         <td>
            <xsl:value-of select="description"/>
         </td>
         <td>
            <xsl:value-of select="@lang"/>
         </td>
       </tr>
     </xsl:for-each>
   </tbody>
      </table>
      <p>
   <i:text>[0110]Avec les projets sélectionnés</i:text><xsl:text> : </xsl:text>
   <select name="action">
     <option value="archive"><i:text>[0111]Créer une archive</i:text></option>
     <option value="delete"><i:text>[0095]Supprimer</i:text></option>
   </select>
   <input type="submit" i:value="[0132]ok"/>
      </p>
      <p><a href="/{$admin}/projects/params/0"><i:text>[0112]Nouveau projet</i:text></a></p>
    </form>
  </xsl:template>

  <!-- project  -->
  <xsl:template name="admproject">
    <xsl:variable name="id">
      <xsl:value-of select="substring-after(substring-after(/kcd:view/kcd:http/@path,concat('/',$admin,'/projects/')), '/')"/>
    </xsl:variable>
    <xsl:variable name="projectdata" select="/kcd:view/kcd:data/kcd:namespace[@id='kolekti']/kcd:value[@key='projects']/projects/project[@id=$id]"/>
    <h3>
      <xsl:choose>
   <xsl:when test="number($id)=0"><i:text>[0112]Nouveau projet</i:text></xsl:when>
   <xsl:otherwise><i:text>[0113]Projet</i:text><xsl:text> </xsl:text><em><xsl:value-of select="$projectdata/@name"/></em></xsl:otherwise>
      </xsl:choose>
    </h3>
    <ul id="admintabs">
      <li>
   <xsl:if test="starts-with(/kcd:view/kcd:http/@path,concat('/',$admin,'/projects/params'))">
     <xsl:attribute name="class">active</xsl:attribute>
   </xsl:if>
   <a href="/{$admin}/projects/params/{$id}"><i:text>[0114]Paramètres</i:text></a>
      </li>
      <xsl:if test="number($id)!=0">
   <li>
     <xsl:if test="starts-with(/kcd:view/kcd:http/@path,concat('/',$admin,'/projects/users'))">
       <xsl:attribute name="class">active</xsl:attribute>
     </xsl:if>
     <a href="/{$admin}/projects/users/{$id}"><i:text>[0106]Utilisateurs</i:text></a>
   </li>
   <li>
     <xsl:if test="starts-with(/kcd:view/kcd:http/@path,concat('/',$admin,'/projects/scripts'))">
       <xsl:attribute name="class">active</xsl:attribute>
     </xsl:if>
     <a href="/{$admin}/projects/scripts/{$id}"><i:text>[0115]Scripts de publication</i:text></a>
   </li>
   <li>
     <xsl:if test="starts-with(/kcd:view/kcd:http/@path,concat('/',$admin,'/projects/maintenance'))">
       <xsl:attribute name="class">active</xsl:attribute>
     </xsl:if>
     <a href="/{$admin}/projects/maintenance/{$id}"><i:text>[0116]Maintenance</i:text></a>
   </li>
      </xsl:if>
    </ul>

    <form method="post" class="tabular settings" action="{/kcd:view/kcd:http/@path}" onsubmit="return kadmin.verify()">
      <xsl:choose>
   <!-- parameters tab -->
   <xsl:when test="starts-with(/kcd:view/kcd:http/@path,concat('/',$admin,'/projects/params'))">
     <fieldset>
       <input type="hidden" id="id" name="id" value="{$id}"/>
       <p><label class="fieldtitle" for="name"><i:text>[0079]Nom</i:text></label><input type="text" id="name" name="name" value="{$projectdata/@name}"/></p>
       <p>
         <label class="fieldtitle" for="dir"><i:text>[0117]Dossier</i:text></label>
         <input type="text" id="dir" name="dir" value="{$projectdata/@dir}">
      <xsl:if test="$projectdata/@dir"><xsl:attribute name="disabled">disabled</xsl:attribute></xsl:if>
         </input>
       </p>
       <p><label class="fieldtitle" for="desc"><i:text>[0109]Description</i:text></label><textarea id="desc" name="desc" ><xsl:value-of select="$projectdata/description"/><xsl:text> </xsl:text></textarea></p>
       <p><label class="fieldtitle" for="lang"><i:text>[0107]Langue de travail</i:text></label><input id="lang" name="lang" value="{$projectdata/@lang}" /></p>
       <input type="submit" i:value="[0083]Enregistrer"/>
     </fieldset>
   </xsl:when>

   <!-- users tab -->
   <xsl:when test="starts-with(/kcd:view/kcd:http/@path,concat('/',$admin,'/projects/users'))">
     <fieldset>
     <xsl:for-each select="$projectdata/users/user">
       <p class="icon22 icon22-users">
         <input type="hidden" id="u{@uid}" value="{@uid}" name="uid"/>
         <label class="fieldtitle" for="u{@uid}">
      <xsl:value-of select="/kcd:view/kcd:data/kcd:namespace[@id='kolekti']/kcd:value[@key='users']/users/user[number(@uid)=number(current()/@uid)]/@login"/>
         </label>
         <input type="submit" id="u{@uid}" name="rem{@uid}" i:value="[0118]Retirer"/>
         <br/>
       </p>
     </xsl:for-each>
     <xsl:if test="/kcd:view/kcd:data/kcd:namespace[@id='kolekti']/kcd:value[@key='users']/users/user[not(number(@uid)=$projectdata/users/user/@uid)]">
       <p>
         <label class="fieldtitle" for="adduser"><i:text>[0119]Ajouter un utilisateur</i:text></label>
         <select name="useradd">
      <xsl:for-each select="/kcd:view/kcd:data/kcd:namespace[@id='kolekti']/kcd:value[@key='users']/users/user">
        <xsl:sort select="@login" />
        <xsl:if test="not($projectdata/users/user[number(@uid)=number(current()/@uid)])">
          <option value="{number(@uid)}"><xsl:value-of select="@login"/></option>
          <xsl:value-of select="@uid"/>
        </xsl:if>
      </xsl:for-each>
         </select>
         <input type="submit" name="add" i:value="[0120]Ajouter"/>
       </p>
     </xsl:if>
     </fieldset>
   </xsl:when>

   <!-- scripts tab -->
   <xsl:when test="starts-with(/kcd:view/kcd:http/@path,concat('/',$admin,'/projects/scripts'))">
     <fieldset>
     <xsl:for-each select="/kcd:view/kcd:data/kcd:namespace[@id='kolekti']/kcd:value[@key='scripts']/scripts/pubscript">
      <p>
         <input type="checkbox" name="script" value="{@id}">
            <xsl:if test="/kcd:view/kcd:data/kcd:namespace[@id='kolekti']/kcd:value[@key='projectscripts']/scripts/pubscript[@id=current()/@id]">
               <xsl:attribute name="checked">checked</xsl:attribute>
            </xsl:if>
         </input>
         <label class="fieldtitle" for="desc"><xsl:value-of select="@id" /></label>
      </p>
     </xsl:for-each>
     <input type="submit" i:value="[0083]Enregistrer"/>
     </fieldset>
   </xsl:when>

   <!-- maintenance tab -->
   <xsl:when test="starts-with(/kcd:view/kcd:http/@path,concat('/',$admin,'/projects/maintenance'))">
     <fieldset>
       <p>
         <span>
           <label class="fieldtitle" for="archive"><i:text>[0121]Archiver le projet</i:text></label>
           <input type="submit" name="archive" i:value="[0122]Exécuter" />
         </span>
         <xsl:if test="/kcd:view/kcd:data/kcd:namespace[@id='project']/kcd:value[@key='archive']">
           <span>
            <a href="{substring-before(/kcd:view/kcd:http/@path, $projectdata/@id)}archive/{$projectdata/@id}"><i:text>[0123]Télécharger l'archive</i:text></a>
           </span>
         </xsl:if>
       </p>
       <p>
         <label class="fieldtitle" for="usecase"><i:text>[0124]Régénérer les cas d'usage</i:text></label>
         <input type="submit" name="usecase" i:value="[0122]Exécuter" />
       </p>
     </fieldset> 
   </xsl:when>
      </xsl:choose>
    </form>
  </xsl:template>

  <!-- utilisateurs -->
  <xsl:template name="admusers">
    <xsl:apply-templates select="kcd:namespace[@id='kolekti']/kcd:value[@key='users']/users"/>
  </xsl:template>

  <xsl:template name="admuser">
    <xsl:variable name="uid">
     <xsl:value-of select="substring-after(substring-after(/kcd:view/kcd:http/@path,concat('/',$admin,'/users/')), '/')"/>
    </xsl:variable>

    <h3>
      <xsl:choose>
   <xsl:when test="number($uid)=0"><i:text>[0125]Nouvel utilisateur</i:text></xsl:when>
   <xsl:otherwise><i:text>[0126]Utilisateur</i:text><xsl:text> </xsl:text><em><xsl:value-of select="kcd:namespace[@id='kolekti']/kcd:value[@key='users']/users/user[number(@uid)=$uid]/@login"/><xsl:text> </xsl:text><xsl:value-of select="/kcd:view/kcd:data/users/user[number(@uid)=$uid]/lastname"/></em></xsl:otherwise>
      </xsl:choose>
    </h3>

    <form method="post" class="tabular settings" action="{/kcd:view/kcd:http/@path}" onsubmit="return kadmin.verify()">
      <xsl:variable name="userdata" select="kcd:namespace[@id='kolekti']/kcd:value[@key='users']/users/user[number(@uid)=$uid]"/>
      <fieldset>
         <legend><i:text>[0099]Informations générales</i:text></legend>   
         <p><label class="fieldtitle" for="lastname"><i:text>[0079]Nom</i:text></label><input type="text" id="lastname"  name="lastname" value="{$userdata/lastname}"/></p>
         <p><label class="fieldtitle" for="firstname"><i:text>[0080]Prénom</i:text></label><input type="text" id="firstname"  name="firstname" value="{$userdata/firstname}"/></p>
         <p><label class="fieldtitle" for="email"><i:text>[0081]Courriel</i:text></label><input type="text" id="email"  name="email" value="{$userdata/email}"/></p>
         <p><label class="fieldtitle" for="organization"><i:text>[0082]Organisation</i:text></label><input type="text" id="organization"  name="organization" value="{$userdata/organization}"/></p>
         <p>
            <label class="fieldtitle" for="locale"><i:text>[0107]Langue de travail</i:text></label>
            <select id="locale" name="locale">
               <xsl:for-each select="kf:getlocalelist()">
                  <option value="{@value}">
                     <xsl:if test="@value = $userdata/lang">
                        <xsl:attribute name="selected">selected</xsl:attribute>
                     </xsl:if>
                     <xsl:value-of select="." />
                  </option>
               </xsl:for-each>
            </select>
         </p>
         <p>
            <label class="fieldtitle" for="timezone"><i:text>[0323]Fuseau horaire</i:text></label>
            <select id="locale" name="timezone">
               <xsl:for-each select="kf:gettimezonelist()">
                  <option value="{@value}">
                     <xsl:if test="@value = $userdata/timezone">
                        <xsl:attribute name="selected">selected</xsl:attribute>
                     </xsl:if>
                     <xsl:text></xsl:text><xsl:value-of select="@label" />
                  </option>
               </xsl:for-each>
            </select>
         </p>
      </fieldset> 
      <fieldset>
   <legend>Identification</legend>
   <p class="required">
      <label class="fieldtitle" for="login"><i:text>[0100]Identification</i:text></label>
      <input type="text" id="login"  name="login" value="{$userdata/@login}">
         <xsl:if test="not(number($uid)=0)"><xsl:attribute name="disabled">disabled</xsl:attribute></xsl:if>
      </input>
   </p>
   <p>
      <xsl:if test="not($userdata/@login)">
         <xsl:attribute name="class"><xsl:text>required</xsl:text></xsl:attribute>
      </xsl:if>
      <label class="fieldtitle" for="pass1"><i:text>[0085]Mot de passe</i:text></label><input type="password" id="pass" name="pass"/>
   </p>   
   <p>
      <xsl:if test="not($userdata/@login)">
         <xsl:attribute name="class"><xsl:text>required</xsl:text></xsl:attribute>
      </xsl:if>
      <label class="fieldtitle" for="pass2"><i:text>[0086]Mot de passe (confirmation)</i:text></label><input type="password" id="pass2" name="pass2"/>
   </p>    
       <p>
         <span>
            <label class="fieldtitle" for="admin"><i:text>[0127]Administrateur</i:text></label>
            <input type="checkbox" id="admin" name="isadmin" value="*">
               <xsl:if test="$userdata/@isadmin"><xsl:attribute name="checked">checked</xsl:attribute></xsl:if>
            </input>
         </span>
         <span>
           <label class="fieldlisttitle" for="translator"><i:text>[0128]Traducteur</i:text></label>
           <input type="checkbox" id="translator" name="istranslator" value="*">
              <xsl:if test="$userdata/@istranslator"><xsl:attribute name="checked">checked</xsl:attribute></xsl:if>
           </input>
         </span>
       </p>
     </fieldset>
     <fieldset>
      <legend><i:text>[0129]Accès aux projets</i:text></legend>
         <xsl:for-each select="kcd:namespace[@id='kolekti']/kcd:value[@key='projects']/projects/project">
            <input type="checkbox" name="project" value="{@dir}" id="{@dir}">
               <xsl:if test="users/user[number(@uid)=$uid]"><xsl:attribute name="checked">checked</xsl:attribute></xsl:if>
            </input>
            <label for="{@dir}"><xsl:value-of select="@name" /></label>
         </xsl:for-each>
     </fieldset>
      <input type="submit" i:value="[0083]Enregistrer"/>
    </form>
  </xsl:template>
  
  <!--templates de listes -->

  <xsl:template match="users">
    <form method="post" action="/{$admin}/users" onsubmit="return kadmin.verify()">
     <table class="admin">
   <thead>
     <tr>
       <th />
       <th><i:text>[0094]Login</i:text></th>
       <th><i:text>[0079]Nom</i:text> - <i:text>[0080]Prénom</i:text></th>
       <th><i:text>[0081]Courriel</i:text></th>
       <th><i:text>[0082]Organisation</i:text></th>
       <th><i:text>[0127]Administrateur</i:text></th>
       <th><i:text>[0128]Traducteur</i:text></th>
     </tr>
   </thead>
      <tbody>
   <xsl:for-each select="user">
     <tr class="user odd active">
       <td class="checkbox"><input type="checkbox" name="deluser" value="{@uid}"/></td>
       <td><a href="/{$admin}/users/params/{number(@uid)}"><xsl:value-of select="@login"/></a></td>
       <td><xsl:value-of select="lastname"/><xsl:text> </xsl:text><xsl:value-of select="firstname"/></td>
       <td><xsl:value-of select="email"/></td>
       <td><xsl:value-of select="organization"/></td>
       <td><xsl:if test="@isadmin"><i:text>[0130]Oui</i:text></xsl:if></td>
       <td><xsl:if test="@istranslator"><i:text>[0130]Oui</i:text></xsl:if></td>
     </tr>
   </xsl:for-each>
      </tbody>
     </table>
     <p><i:text>[0131]Avec les utilisateurs sélectionnés</i:text> : <select name="action"><option value="delete"><i:text>[0095]Supprimer</i:text></option></select><input type="submit" i:value="[0132]ok" onclick="javascript:kadmin.deletedata('/admin/groups')"/></p>
     <p><a href="/{$admin}/users/params/0"><i:text>[0125]Nouvel utilisateur</i:text></a></p>
    </form>
  </xsl:template>
</xsl:stylesheet>
