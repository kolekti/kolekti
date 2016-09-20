	var AnimatedLayer;
	
	window.requestAnimFrame = window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || window.oRequestAnimationFrame || window.msRequestAnimationFrame || function(callback) {
		return window.setTimeout(callback, 1000 / 60);
	};

	/**
	 * Animated layer
	 * 
	 * @constructor
	 * @param {Object} options {gradient: {...}}
	 * @return {void}
	 */
function AnimatedLayer(options, map) {
    this.map = map;
		this.data = [];
		this.momentIndex = 0;
		this.isPaused = false;
		this.isLooped = false;
		this.dataLayerGroup;
    this.dataLayer = new DataLayer(options, map);
		this._debugStartTime;
		this.setSpeed(10);
	}
	
	/**
	 * Sets the options.
	 * 
	 * @param {Object} options
	 * @return {void}
	 */
	AnimatedLayer.prototype.setOptions = function (options) {
		this.dataLayer.setOptions(options);
	};
	
	/**
	 * Sets the data.
	 * 
	 * @param {Object} data
	 * @return {void}
	 */
	AnimatedLayer.prototype.setData = function(data) {
		this.data = data;
	};
	
	
	/**
	 * Sets the navbar.
	 * 
	 * @param {Object} Navigation bar object 
	 * @return {void}
	 */
	AnimatedLayer.prototype.setNavigationBar = function(navbar) {
		this.navigationBar = navbar;
	};
	
	/**
	 * Sets the speed of the animation.
	 * 
	 * @param {number} speed_fps Speed in frames per seconds
	 * @return {void}
	 */
	AnimatedLayer.prototype.setSpeed = function(speed_fps) {
		this.speed_fpms = 1000 / speed_fps;
	};
	
	/**
	 * Shows a specific moment.
	 * 
	 * @param {number} index A index of the given data array.
	 * @return {void}
	 */
	AnimatedLayer.prototype.showMoment = function(index) {
		if (index) {
			this.momentIndex = index;
		}
		var dataEntry = this.data[this.momentIndex];
		this.navigationBar.update(this.momentIndex, dataEntry.date * 1000);
		this.dataLayer.plotPoints(dataEntry.points);
	};
	
	/**
	 * Animates the given data.
	 * 
	 * @return {Function}
	 */
	AnimatedLayer.prototype.animate = function() {
		var _this = this;
		var doDraw = function() {
			if (_this.isPaused) {
				return;
			}
		
			_this.showMoment();
			_this.momentIndex++;
			if (_this.momentIndex >= _this.data.length) {
				if (_this.isLooped) {
					_this.momentIndex = 0;
				} else {
					_this.animationStop();
					return;
				}
			}
			window.setTimeout(function() {
				window.requestAnimFrame(function() {
				return doDraw();
			});
			}, _this.speed_fpms);
//			return window.requestAnimFrame(function() {
//				return doDraw();
//			});
		};
		return window.requestAnimFrame(function() {
			return doDraw();
		});
	};
	
	/**
	 * Starts the animation.
	 * 
	 * @return {void}
	 */
	AnimatedLayer.prototype.animationStart = function() {
		this._debugStartTime = new Date().getTime();
		console.log("animation started at " + this._debugStartTime);
		this.isPaused = false;
		this.momentIndex = 0;
		this.animate();
	};
	
	/**
	 * Pauses the animation.
	 * 
	 * @return {void}
	 */	
	AnimatedLayer.prototype.animationPause = function() {
		this.isPaused = true;
	};
	
	/**
	 * Pauses the animation.
	 * 
	 * @return {void}
	 */	
	AnimatedLayer.prototype.animationResume = function() {
		console.log("resume");
		this.isPaused = false;
		this.animate();
	};
	
	/**
	 * Stops the animation.
	 * 
	 * @return {void}
	 */
	AnimatedLayer.prototype.animationStop = function() {
		var _debugEndTime = new Date().getTime();
		console.log("animation stoped at " + _debugEndTime + ", " + (_debugEndTime - this._debugStartTime) + "ms");
		this.animationPause();
		this.clearMap();
		this.momentIndex = 0; // TODO: dublicated with animationStart
		this.navigationBar.reset();
	};
	
	/**
	 * Set animation to a endless loop.
	 * 
	 * @param {boolean} isLooped True to activate endless loop
	 * @return {void}
	 */	
	AnimatedLayer.prototype.animationLoop = function(isLooped) {
			this.isLooped = isLooped;
	};		
	
	AnimatedLayer.prototype.clearMap = function() {
		this.dataLayer.clear();
//		if (this.dataLayerGroup) {
//			this.dataLayerGroup.clearLayers();
//			map.removeLayer(this.dataLayerGroup);			
//		}
		for(i in this.map._layers){
			if(this.map._layers[i]._path != undefined) {
				try {
					this.map.removeLayer(this.map._layers[i]);
				} catch(e) {
					console.log("problem with " + e + this.map._layers[i]);
				}
			}
		}
	};
