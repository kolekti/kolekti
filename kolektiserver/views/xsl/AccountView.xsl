<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml"
                xmlns:i="kolekti:i18n"
                xmlns:kf="kolekti:extensions:functions"
                xmlns:ke="kolekti:extensions:elements"
                xmlns:kd="kolekti:dialogs"
                xmlns:kcd="kolekti:ctrdata"
                xmlns:kes="kolekti:extsrc"
                xmlns:kui="kolekti:userinfo"
                xmlns:kua="kolekti:userauth"

                extension-element-prefixes="ke"
                exclude-result-prefixes="i kf ke kd kcd kes kui kua">

  <xsl:import href="WWWView.xsl"/>
  <xsl:import href="AdminForms.xsl"/>
  <xsl:output method="xml" indent="yes"/>

  <xsl:variable name="currenttab">
    <xsl:variable name="c" select="substring-after(/kcd:view/kcd:http/@path,'/user/')"/>
    <xsl:choose>
      <xsl:when test="contains($c,'/')">
        <xsl:value-of select="substring-before($c,'/')"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$c"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:template match="kcd:view">
    <div id="header">
      <h1><i:text>[0078]Mon Compte</i:text></h1>
      <div id="main-menu">
        <ul>
          <xsl:call-template name="tabs">
            <xsl:with-param name="current"><xsl:value-of select="$currenttab"/></xsl:with-param>
          </xsl:call-template>
        </ul>
      </div>
    </div>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="kcd:data">
    <kd:kolektiadmin />
    <kd:sidebar />
    <div>
      <div id="admincontent">
        <xsl:call-template name="accountuser"/>
      </div>
    </div>
  </xsl:template>

  <xsl:template name="accountuser">  
    <xsl:variable name="userdata" select="kcd:namespace[@id='kolekti']/kcd:value[@key='user']/user"/>
    <xsl:choose>
      <xsl:when test="$currenttab='account'">
        <xsl:call-template name="status"/>
        <form method="post" class="tabular settings" action="{/kcd:view/kcd:http/@path}" onsubmit="return kadmin.verify()">
          <fieldset>
            <p><label class="fieldtitle" for="lastname"><i:text>[0079]Nom</i:text></label><input type="text" id="lastname" name="lastname" value="{$userdata/lastname}"/></p>
            <p><label class="fieldtitle" for="firstname"><i:text>[0080]Prénom</i:text></label><input type="text" id="firstname" name="firstname" value="{$userdata/firstname}"/></p>
            <p><label class="fieldtitle" for="email"><i:text>[0081]Courriel</i:text></label><input type="text" id="email" name="email" value="{$userdata/email}"/></p>
            <p><label class="fieldtitle" for="organization"><i:text>[0082]Organisation</i:text></label><input type="text" id="organization" name="organization" value="{$userdata/organization}"/></p>
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
          <input type="submit" i:value="[0083]Enregistrer" />
        </form>
      </xsl:when>

      <xsl:when test="$currenttab='ident'">
        <xsl:call-template name="status"/>
        <form method="post" class="tabular settings" action="{/kcd:view/kcd:http/@path}" onsubmit="return kadmin.verify()">
          <fieldset>
            <p><label class="fieldtitle"  for="login"><i:text>[0084]Identifiant</i:text></label><input type="text" id="showlogin"  name="showlogin" value="{$userdata/@login}" disabled="disabled"/></p>
            <p class="required"><label class="fieldtitle"  for="pass1"><i:text>[0085]Mot de passe</i:text></label><input type="password" id="pass" name="pass"/></p>
            <p class="required"><label class="fieldtitle"  for="pass2"><i:text>[0086]Mot de passe (confirmation)</i:text></label><input type="password" id="pass2" name="pass2"/></p>
          </fieldset>
          <input type="submit" i:value="[0083]Enregistrer" />
        </form>
      </xsl:when>

       <xsl:when test="$currenttab='extsrc'">
        <xsl:call-template name="status"/>
        <xsl:choose>
          <xsl:when test="/kcd:view/kcd:http/@path='/user/extsrc'">
            <xsl:if test="/kcd:view/kcd:data/kes:sources">
              <fieldset>
                <legend><i:text>[0087]Mes wikis</i:text></legend>
                <xsl:apply-templates select="/kcd:view/kcd:data/kes:sources"/>
              </fieldset>
            </xsl:if>
            <p><a href="/user/extsrc/0"><i:text>[0088]Ajouter une source...</i:text></a></p>
          </xsl:when>

          <xsl:otherwise>
            <xsl:call-template name="editextsrc">
              <xsl:with-param name="srcid" select="substring-after(/kcd:view/kcd:http/@path,'/user/extsrc/')"/>
            </xsl:call-template>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="editextsrc">
    <xsl:param name="srcid"/>
    <form method="post" class="tabular settings" action="/user/extsrc" onsubmit="return kadmin.verify()">
      <fieldset>
        <legend>
          <xsl:choose>
            <xsl:when test="$srcid='0'"><i:text>[0089]Nouvelle source wiki</i:text></xsl:when>
            <xsl:otherwise><i:text>[0090]Wiki source</i:text> : <em><xsl:value-of select="$srcid"/></em></xsl:otherwise>
          </xsl:choose>
        </legend>
        <input type="hidden" name="extsrcid" value="{$srcid}"/>
        <xsl:if test="$srcid='0'">
          <p>
            <label class="fieldtitle"  for="extsrcnewid"><i:text>[0091]Nom de la source</i:text> : </label>
            <input type="text" name="extsrcnewid"/>
          </p>
        </xsl:if>
        <p>
          <label class="fieldtitle"  for="extsrccon"><i:text>[0092]Connecteur</i:text> : </label>
          <select name="extsrccon">
            <xsl:apply-templates select="/kcd:view/kcd:data/kes:connectors">
              <xsl:with-param name="selected" select="/kcd:view/kcd:data/kes:sources/kes:source[@id=$srcid]/@connector"/>
            </xsl:apply-templates>
          </select>
        </p>
        <p>
          <label class="fieldtitle"  for="extsrcurl"><i:text>[0093]Adresse du serveur</i:text> : </label>
          <input type="text" name="extsrcurl" value="{/kcd:view/kcd:data/kes:sources/kes:source[@id=$srcid]/@url}"/>
        </p>
        <p>
          <label class="fieldtitle"  for="extsrcurl"><i:text>[0094]Login</i:text> : </label>
          <input type="text" name="extsrclog" value="{/kcd:view/kcd:data/kes:sources/kes:source[@id=$srcid]/@user}"/>
        </p>
        <p>
          <label class="fieldtitle"  for="extsrcurl"><i:text>[0085]Mot de passe</i:text> : </label>
          <input type="text" name="extsrcpass" value="{/kcd:view/kcd:data/kes:sources/kes:source[@id=$srcid]/@passwd}"/>

        </p>
        <xsl:if test="not($srcid='0')">
          <p><input type="checkbox" name="extsrcdelete" value="yes"/><label for="extsrcdelete"><i:text>[0095]Supprimer</i:text></label></p>
        </xsl:if>
      </fieldset>
      <input type="submit" i:value="[0083]Enregistrer" />
    </form>
  </xsl:template>

  <xsl:template match="kes:connector">
    <xsl:param name="selected"/>
    <option value="{@id}">
      <xsl:if test="@id=$selected">
        <xsl:attribute name="selected">selected</xsl:attribute>
      </xsl:if>
      <xsl:value-of select="@id"/>
    </option>
  </xsl:template>

  <xsl:template match="kes:source">
    <div class="extsrc">
      <h4><xsl:value-of select="@id"/></h4>
      <p><i:text>[0092]Connecteur</i:text> :  <xsl:value-of select="@connector"/></p>
      <p><i:text>[0096]Url</i:text> : <xsl:value-of select="@url"/></p>
      <p><i:text>[0097]User</i:text> : <xsl:value-of select="@user"/></p>
      <p class="actions">
        --> <a href="/user/extsrc/{@id}"><i:text>[0098]Modifier</i:text></a>
      </p>
    </div>
  </xsl:template>

  <xsl:template name="tabs">
    <xsl:param name="current"><xsl:value-of select="$currenttab"/></xsl:param>
    <xsl:call-template name="tab">
      <xsl:with-param name="label"><i:text>[0099]Informations générales</i:text></xsl:with-param>
      <xsl:with-param name="link" select="'/user/account'"/>
      <xsl:with-param name="current" select="$current='account'"/>
    </xsl:call-template>
    <xsl:call-template name="tab">
      <xsl:with-param name="label"><i:text>[0100]Identification</i:text></xsl:with-param>
      <xsl:with-param name="link" select="'/user/ident'"/>
      <xsl:with-param name="current" select="$current='ident'"/>
    </xsl:call-template>
<!--     <xsl:call-template name="tab">
      <xsl:with-param name="link" select="'/user/extsrc'"/>
      <xsl:with-param name="label"><i:text>[0101]Wikis</i:text></xsl:with-param>
      <xsl:with-param name="current" select="$current='extsrc'"/>
    </xsl:call-template> -->
  </xsl:template>
</xsl:stylesheet>
