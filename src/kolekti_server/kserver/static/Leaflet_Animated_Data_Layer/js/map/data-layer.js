	var DataLayer;
	
function DataLayer(options, map) {
		this.setOptions(options);
		this.visualizationType = 'circle';
    this.layer = new L.LayerGroup();
    this.map = map;
		map.addLayer(this.layer);
		
		this.heatmapLayer = new L.TileLayer.WebGLHeatMap({
				size: 270 * 1000,
//				size: 180 * 1000,
				opacity: 0.8,
				gradientTexture: false,
				alphaRange: 1,
				autoresize: true
			});
		map.addLayer(this.heatmapLayer);
		this.recLayer = new L.TileLayer.RecLayer();
		map.addLayer(this.recLayer);
	}
	
	/**
	 * Sets the options.
	 * 
	 * @param {Object} options Option array
	 * @return {void}
	 */
	DataLayer.prototype.setOptions = function(options) {
		this.grades = options.grades;
		this.circleRadius_m = options.circleRadius * 1000;		// in meters
		this.rectangleHalfSize = options.gridSize / 2;
		this.fillOpacity = options.fillOpacity;
	};
	
	/**
	 * Sets the visualization type.
	 * 
	 * @param {string} type Visualization type ('circle', 'rectangle', etc.)
	 * @return {void}
	 */
	DataLayer.prototype.setVisualizationType = function(type) {
		if (this.visualizationType === 'heatmap') {
			this.heatmapLayer._clear();
		}
		this.visualizationType = type;
	};
	
	/**
	 * 
	 * @param {Array} data
	 */
	DataLayer.prototype.plotPoints = function(data) {
		var point,
			options,
			_visualizationType = this.visualizationType;

		this.layer.clearLayers();
		this.heatmapLayer.clearData();
		this.recLayer.dataClear();

		for(var i=0, len=data.length; i < len; i++) {
			point = data[i];

			if (_visualizationType === 'heatmap') {
				this.heatmapLayer.addDataPoint(point.lat, point.lon, this.getXc(point.val));
				continue;
			} else if (_visualizationType === 'rec') {
				this.recLayer.dataAddPoint(point);
				continue;
			} 

			if (point.in === 'no') {
				continue;
				// opacity = 0.3;
			}
			
			options = {
				weight: 0,
				//color: color,
				//opacity: opacity,
				fillColor: this.getColor(point.val),
				fillOpacity: this.fillOpacity
			};

			if (_visualizationType === 'circle') {
				L.circle([point.lat, point.lon], this.circleRadius_m, options).addTo(this.layer);
			} else if (_visualizationType === 'rectangle') {
				L.rectangle([[point.lat - this.rectangleHalfSize, point.lon - this.rectangleHalfSize], [point.lat + this.rectangleHalfSize, point.lon + this.rectangleHalfSize]], options).addTo(this.layer);
			} else if (_visualizationType === 'dot') {
				L.circle([point.lat, point.lon], 9000, options).addTo(this.layer);				
			}
		}
		
		if (_visualizationType === 'heatmap') {
			this.heatmapLayer.update();
		}  else if (_visualizationType === 'rec') {
			this.recLayer._plot();
		}

	};
	
	/**
	 * Gets a color for a the given value.
	 * 
	 * @private
	 * @param {number} v Value
	 * @return {String} Color as string
	 */
	DataLayer.prototype.getColor = function(v) {
		return v > this.grades[0].val ? this.grades[0].color :
           v > this.grades[1].val ? this.grades[1].color :
           v > this.grades[2].val ? this.grades[2].color :
           v > this.grades[3].val ? this.grades[3].color :
                                    this.grades[4].color;
	};

	/**
	 * 
	 * 
	 * @private
	 * @param {number} v Value
	 * @return {number} Numer in percent
	 */
	DataLayer.prototype.getXc = function(v) {
		return v > this.grades[0].val ? 100 :
           v > this.grades[1].val ? 50 :
           v > this.grades[2].val ? 30 :
           v > this.grades[3].val ? 20 :
                                    10;
	};	

	/**
	 * Clears the layer.
	 * 
	 * @return {void}
	 */
	DataLayer.prototype.clear = function() {
		if (this.visualizationType === 'heatmap') {
			this.heatmapLayer._clear();
			this.heatmapLayer.clearData();			
		} else {
			this.layer.clearLayers();
		}
	};
