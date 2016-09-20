L.TileLayer.RecLayer = L.Class.extend( {
	
	options: {
		opacity: 1
	},
	
    initialize: function (options) {
        this._data = [];
		this._map;
		this._canvas;
        L.setOptions(this, options);
    },
	
	setOptions: function (options) {
		L.setOptions(this, options);
		// todo: may redraw
	},
	
	/**
	 * 
	 * @param {Object} point {lat: XX, lng: XX, val: XX}
	 * @return {void}
	 */
	dataAddPoint: function (point) {
		this._data.push(point);
	},
	
	dataClear: function() {
		this._data = [];
	},
	
	onAdd: function (map) {
		this._map = map;
		
		if (!this._canvas) {
			this._initCanvas();
		}
				
		map.getPanes().overlayPane.appendChild(this._canvas);

		map.on("moveend", this._plot, this);
		/* hide layer on zoom, because it doesn't animate zoom */
		map.on("zoomstart", this._hide, this);
		map.on("zoomend", this._show, this);
		
        this._plot();
	},
	
	resize: function() {
		var mapSize = this._map.getSize();
		this._canvas.width = mapSize.x;
		this._canvas.height = mapSize.y;		
	},
	
	onRemove: function (map) {
        map.getPanes().overlayPane.removeChild(this._canvas);		
	},
	
	update: function () {
		this._plot();
	},
	
	_initCanvas: function() {
		var mapSize = this._map.getSize();
		var canvas = this._canvas = document.createElement("canvas"); 
        canvas.width = mapSize.x;
        canvas.height = mapSize.y;
        canvas.style.opacity = this.options.opacity;
        canvas.style.position = 'absolute';
	},
	
	_hide: function () {
		this._canvas.style.display = 'none';
	},
	
	_show: function () {
		this._canvas.style.display = 'block';
	},
	
	_drawRectangle: function (width, height, opacity) {
		var canvas=document.createElement('canvas');
		var ctx=canvas.getContext('2d');
		ctx.fillStyle='#FF0000';
		ctx.fillRect(0, 0, width, height);
		canvas.style.opacity = opacity;
		return canvas;
	},
	
	_plot: function () {
		this.resize();

//		this._canvas.appendChild(c);

	    this._ctx = this._canvas.getContext('2d');
//		console.log(this._canvas.width + "--" + this._canvas.height);
		this._ctx.clearRect(0, 0, this._canvas.width, this._canvas.height);
		//		this._ctx.drawImage(this._drawRectangle(200,200, 0.7), 10, 10);	
		var dataEntry, pointNW, pointSE, width, height, imgage;
		for(var i = 0, len = this._data.length; i < len; i++) {
			dataEntry = this._data[i];
			pointNW = this._map.latLngToLayerPoint([dataEntry.lat - 0.5, dataEntry.lon - 0.5]);
			pointSE = this._map.latLngToLayerPoint([dataEntry.lat + 0.5, dataEntry.lon + 0.5]);
			width = pointSE.x - pointNW.x;
			height = pointNW.y - pointSE.y;
			imgage = this._drawRectangle(width, height, 0.7);
			this._ctx.drawImage(imgage, pointNW.x, pointNW.y - height);
		}
	},
		
	/**
	 * Gets a color for a the given value.
	 * 
	 * @private
	 * @param {number} v Value
	 * @return {String} Color as string
	 */
	getColor: function(v) {
		return v > this.grades[0].val ? this.grades[0].color :
           v > this.grades[1].val ? this.grades[1].color :
           v > this.grades[2].val ? this.grades[2].color :
           v > this.grades[3].val ? this.grades[3].color :
                                    this.grades[4].color;
	},
	
});

L.TileLayer.reclayer = function (options) {
	return new L.TileLayer.RecLayer(options);
};