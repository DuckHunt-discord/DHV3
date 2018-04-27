/* Copyright (c) 2006-2007 Mathias Bank (http://www.mathias-bank.de)
 * Dual licensed under the MIT (http://www.opensource.org/licenses/mit-license.php) 
 * and GPL (http://www.opensource.org/licenses/gpl-license.php) licenses.
 * 
 * Version 2.1
 * 
 * Thanks to 
 * Hinnerk Ruemenapf - http://hinnerk.ruemenapf.de/ for bug reporting and fixing.
 * Tom Leonard for some improvements
 * 
 */
jQuery.fn.extend({
	/**
	*
	* @param {boolean} lastValue - set to true will return only the last value found, false if you want all values. true by default.
	*
	* Returns get parameters.
	*
	* If the desired param does not exist, null will be returned
	*
	* To get the document params:
	* @example value = $(document).getUrlParam("paramName");
	* 
	* To get the params of a html-attribut (uses src attribute)
	* @example value = $('#imgLink').getUrlParam("paramName");
	*/ 
	getUrlParam: function(strParamName, lastValue = true){
		strParamName = decodeURIComponent(strParamName);
		
		var returnVal = new Array();
		var qString = null;
		
		if ($(this).attr("nodeName") == "#document") {
			//document-handler
			if (window.location.search.search(strParamName) > -1 ){
				qString = window.location.search.substr(1, window.location.search.length).split("&");
			}
		} else if ($(this).attr("src") !== undefined) {
			var strHref = $(this).attr("src");
			if ( strHref.indexOf("?") > -1 ){
				var strQueryString = strHref.substr(strHref.indexOf("?") + 1);
				qString = strQueryString.split("&");
			}
		} else if ($(this).attr("href") !== undefined) {
			var strHref = $(this).attr("href");
			if ( strHref.indexOf("?") > -1 ){
				var strQueryString = strHref.substr(strHref.indexOf("?") + 1);
				qString = strQueryString.split("&");
			}
		} else {
			return null;
		}
		
		if (qString == null) return null;
		
		for (var i = 0; i < qString.length; i++){
			var args = qString[i].split("=");
			if (decodeURIComponent(args[0]) == strParamName){
				returnVal.push(args[1] === undefined ? null : decodeURIComponent(args[1]));
			}
		}
		
		return returnVal.length == 0 ? null : returnVal.length == 1 ? returnVal[0] : lastValue ? returnVal[returnVal.length - 1] : returnVal;
	}
});
