<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:html="http://www.w3.org/1999/xhtml"
                xmlns="http://www.w3.org/1999/xhtml"
                
                exclude-result-prefixes="html"
                version="1.0">

<!--###################
    # Index templates #
    ################### -->

  <!-- Nombre de topics par section sur l'index, 0 = tous -->
  <xsl:variable name="max-section-topics" select="number(0)" />
  <!-- Vidéos en mode fenêtre (valeur '1') ou en externe (valeur '0') -->
  <xsl:variable name="videos-modal" select="'0'" />

  <!-- Mise en forme de la page d'index -->
  <xsl:template name="index-body">
    <div class="container" id="page">
      <section>
        <div class="row">
          <div class="span9">
            <div class="sommaire">
              <div class="well">
                <div class="row">
                  <div class="span6">
                    <!-- inclus la liste des topics par section
                        parametres: 
                            - class: valeur de l'attribut class de chaque section, par défaut 'section'
                     -->
                    <xsl:call-template name="section-topics-list">
                      <xsl:with-param name="class" select="'well'"/>
                    </xsl:call-template>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </xsl:template>

  <!-- Mise en forme du titre des sections
    parametres: 
        - title: valeur du titre de la section -->
  <xsl:template name="section-title">
    <xsl:param name="title" />
    <h2><xsl:value-of select="$title" /></h2>
  </xsl:template>

  <!-- Mise en forme des topics listés
    parametres: 
        - link: lien vers le topic -->
  <xsl:template name="topic-item">
    <xsl:param name="link" />
    <a href="{$link}">
      <i class="icon-chevron-right"></i>
      <!-- inclus le titre du topic -->
      <xsl:call-template name="modtitle" />
    </a>
  </xsl:template>

<!--###################
    # Summary templates #
    ################### -->

  <!-- Mise en forme des pages sommaire de chaque section -->
  <xsl:template name="summary-section">
    <div class="container" id="page">
        <section>
            <div class="row">
                <!-- colonne contenu -->
                <div class="span9">
                    <div class="well">
                        <!-- inclus le contenu du sommaire -->
                        <xsl:call-template name="summary-content" />
                    </div>
                </div>
            </div>
        </section>
    </div>
  </xsl:template>

<!--###################
    # Topic templates #
    ################### -->

  <!-- Mise en forme du contenu des topics -->
  <xsl:template name="topic-body">
    <div class="container" id="page">
        <section>
            <div class="row">
                <!-- colonne contenu -->
                <div class="span9">
                    <!-- inclus le contenu du topic -->
                    <xsl:call-template name="topic-content" />
                </div>
            </div>
        </section>
     </div>
  </xsl:template>
</xsl:stylesheet>