(function($) {
	var map; // O mapa - Será carregado assim que o documento estiver pronto
	var markersArray = [];

	$(document).ready(function($) {
		$("#filter_form").bind('submit', ajax_submit);
		var latlng = new google.maps.LatLng(-14.2350040, -51.925280);
		var myOptions = {
				zoom: 5,
				center: latlng,
				mapTypeId: google.maps.MapTypeId.ROADMAP
		};

		map = new google.maps.Map(document.getElementById("map"), myOptions);
	    ajax_submit();
    })
    
	function ajax_submit(event) {
		var data = $("#filter_form").serialize();
		$.post("/sigi/dashboard/map_data/", data, function(return_data) {
			// Delete all markers
			if (markersArray) {
				for (i in markersArray) {
					markersArray[i].setMap(null);
				}
			}
			markersArray.length = 0;
			
			// Plot new markers
			for (var i in return_data) {
				var municipio = return_data[i];
				var markData = {
						map: map,
						position: new google.maps.LatLng(parseFloat(municipio.lat), parseFloat(municipio.lng)),
						title: municipio.nome,
						icon: '/sigi/media/images/' + municipio.icone + '.png'
				}
				var mark = new google.maps.Marker(markData);
				markersArray.push(mark);
				var infoWin = new google.maps.InfoWindow({content: '<strong>' + municipio.nome + '</strong><br/><br/>' + municipio.info });
				linkMarkMessage(mark, infoWin, map);
			}
		});
		return false;
	}

	function linkMarkMessage(mark, infoWin, map) {
		google.maps.event.addListener(mark, 'click', function() {infoWin.open(map, mark);});
	}
	
})(django.jQuery);