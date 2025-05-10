jQuery(document).ready(function($) {
	var App = {
		init: {
			oneGooMenu: function() {
				var menuBtnID = '#NR-onegoo-service-switch',
					menuTargetID = '#NR-onegoo-service',
					menuCloseClass = '.nr-onegoo-service-close',
					menuBgClass = '.nr-onegoo-bg',
					openClass = 'is-open';
				$(menuCloseClass).on('click', function () {
					$(menuTargetID).toggleClass(openClass);
					$(menuBtnID).toggleClass(openClass);
					$(menuBgClass).toggleClass(openClass);
				});
				$(document).on('click touchstart', function(e) {
					if (!$(e.target).closest(menuTargetID).length && !$(e.target).closest(menuBtnID).length) {
						$(menuTargetID).removeClass(openClass);
						$(menuBtnID).removeClass(openClass);
						$(menuBgClass).removeClass(openClass);
					}
				});
			},
		} // init
	}; // App
	App.init.oneGooMenu();
});