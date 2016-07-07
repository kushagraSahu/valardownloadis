var playlistDownload = (function(){
	var playlist_url = "";
	function downloadAll(e){
		e.preventDefault();
		$.ajax({
			url : window.location.origin + "/playlist/download/all",
			method : 'GET',
			data : {
				'playlist_url' : playlist_url,
			},
			datatype : 'json',
		})
	}
	function init(){
		query = window.location.search
		for(i=5;i<query.length;i++){
			playlist_url = playlist_url + query[i];
		}
		button_all = document.getElementById('btn-all');
		button_all.addEventListener('click',downloadAll)
	}
	return {
		init: init
	};
})();