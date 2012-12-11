(function($) {
	var map; // O mapa - Será carregado assim que o documento estiver pronto
	var municipiosArray = [];

	$(document).ready(function($) {
		$("input[type='checkbox']").change(filter);
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
		$.ajax({
			url: "/sigi/dashboard/mapdata/",
			type: 'GET',
			cache: true,
			success: function(return_data) {
			// Delete all markers
			if (municipiosArray) {
				for (i in municipiosArray) {
					municipiosArray[i].setMap(null);
				}
			}
			municipiosArray.length = 0;
			
			// Create new markers
			for (var i in return_data) {
				var municipio = return_data[i];
				var markData = {
						map: null, // Just create the mark, dont plot it
						position: new google.maps.LatLng(parseFloat(municipio.lat), parseFloat(municipio.lng)),
						title: municipio.nome,
						icon: '/sigi/media/images/' + municipio.icone + '.png'
				}
				var mark = new google.maps.Marker(markData);
				var infoWin = new google.maps.InfoWindow({content: '<strong>' + municipio.nome + '</strong><br/><br/>' + municipio.info });
				linkMarkMessage(mark, infoWin, map);
				municipio['mapmark'] = mark
				municipiosArray.push(municipio);
			}
			filter(null);
		}});
		return false;
	}

	function linkMarkMessage(mark, infoWin, map) {
		google.maps.event.addListener(mark, 'click', function() {infoWin.open(map, mark);});
	}
	
	function filter(event) {
		var data = $("#filter_form").serializeArray();
		var estados = [];
		var regioes = [];
		
		for (var i in data) {
			var name = data[i].name, value = data[i].value;
			if (name == 'estados') {
				estados.push(value);
				delete data[i];
			} else if (name == 'regioes') {
				regioes.push(value);
				delete data[i];
			}
		}
		
		for (var i in municipiosArray) {
			var municipio = municipiosArray[i];
			var aparece = false;

			if (regioes.indexOf(municipio.regiao) == -1 && estados.indexOf(municipio.estado) == -1) {
				aparece = false; 
			} else {
				for (var j in data) {
					if (data[j]) {
						var name = data[j].name, value = data[j].value;
						idx = municipio[name].indexOf(value);
						if (idx != -1) {
							aparece = true;
							break;
						}
					}
				}
			}
			if (aparece) {
				if (municipio.mapmark.map == null) {
					municipio.mapmark.setMap(map);
				}
			} else {
				if (municipio.mapmark.map != null) {
					municipio.mapmark.setMap(null);
				}
			}
		}
	}
	
})(django.jQuery);