(function($) {
	var map; // O mapa - Será carregado assim que o documento estiver pronto
	var municipiosArray = {};

	$(document).ready(function($) {
		$("input[type='checkbox']").change( filter );
		$("#changelist-search").submit( search );
		$("#closeiwlink").click( closeAllInfowindows );
		$("#summary_report").click( open_report );
		$("#list_report").click( open_report );
		$("#list_csv").click( open_report );
		var latlng = new google.maps.LatLng(-14.2350040, -51.925280);
		var myOptions = {
				scrollwheel: false,
				zoom: 5,
				center: latlng,
				mapTypeId: google.maps.MapTypeId.ROADMAP
		};

		map = new google.maps.Map(document.getElementById("map"), myOptions);
	    ajax_submit();
    })

	function ajax_submit(event) {
		$.ajax({
			url: "/dashboard/mapdata/",
			type: 'GET',
			cache: true,
			success: function(return_data) {
			// Delete all markers
			for (i in municipiosArray) {
				municipiosArray[i].setMap(null);
			}
			municipiosArray = {}

			// Create new markers
			for (var i in return_data) {
				var municipio = return_data[i];
				var markData = {
						map: null, // Just create the mark, dont plot it
						position: new google.maps.LatLng(parseFloat(municipio.lat), parseFloat(municipio.lng)),
						title: municipio.nome,
						icon: '/static/img/mapmarker.png'
				}
				var mark = new google.maps.Marker(markData);
				var iwcontent = '<strong>' + municipio.nome + '</strong><br/><br/>' +
				                municipio.info;

				if (municipio.thumb != '') {
					iwcontent = iwcontent + '<br/><br/>' +
                                '<a href="' + municipio.foto + '" target="_blank">' +
				                '<img src="' + municipio.thumb + '"></a>';
				}

				var infoWin = new google.maps.InfoWindow({content: iwcontent });
				linkMarkMessage(mark, infoWin, map);
				municipio['mapmark'] = mark;
				municipio['infowindow'] = infoWin;
				municipiosArray[i] = municipio;
			}
			filter(null);
		}});
		return false;
	}

	function linkMarkMessage(mark, infoWin, map) {
		google.maps.event.addListener(mark, 'click', function() {infoWin.open(map, mark);});
	}

	function closeAllInfowindows() {
		for (var i in municipiosArray) {
			municipiosArray[i]['infowindow'].close();
		}
	}

	function filter(event) {
		var data = $("#filter_form").serializeArray();
		var estados = [];
		var regioes = [];
		var gerentes = [];
		var mostra_sem_nada = true;

		for (var i in data) {
			var name = data[i].name, value = data[i].value;
			if (name == 'estados') {
				estados.push(value);
				delete data[i];
			} else if (name == 'regioes') {
				regioes.push(value);
				delete data[i];
			} else if (name == 'gerente') {
				gerentes.push(value);
				delete data[i];
			} else {
				mostra_sem_nada = false;
			}
		}

		var totalizadores = {}; // id => count
		$(".totalizador").each(function(){ totalizadores[this.id] = 0; });

		for (var i in municipiosArray) {
			var municipio = municipiosArray[i];
			municipio['infowindow'].close();
			var aparece = false;
			var sem_nada = municipio.seit.length == 0 && municipio.convenios.length == 0 && municipio.equipadas.length == 0 && municipio.diagnosticos.length == 0;

			if (regioes.indexOf(municipio.regiao) == -1 && estados.indexOf(municipio.estado) == -1) {
				aparece = false;
				sem_nada = false;
			} else {
				if (gerentes.length > 0 && gerentes.indexOf(municipio.gerente) == -1) {
					aparece = false;
					sem_nada = false;
				} else {
					for (var j in data) {
						if (data[j]) {
							var name = data[j].name, value = data[j].value;
							if (municipio[name].indexOf(value) != -1) {
								aparece = true;
								break;
							}
						}
					}
				}
			}
			if (aparece || (sem_nada && mostra_sem_nada)) {
				if (municipio.mapmark.map == null) {
					municipio.mapmark.setMap(map);
				}
				totalizadores[municipio.regiao]++;
				totalizadores[municipio.estado]++;
				totalizadores["gerente_" + municipio.gerente]++;

				// TODO os prefixos dos ids dependem do codigo de
				// sigi/apps/metas/views.py:65 ... def mapa(...)
				// => tentar tirar essa dependencia ou sinmplificar

				for (var j in municipio.seit) {
					totalizadores[municipio.seit[j]]++
				}
				for (var j in municipio.convenios) {
					totalizadores["convenio_" + municipio.convenios[j]]++
				}
				for (var j in municipio.equipadas) {
					totalizadores["equip_" + municipio.equipadas[j]]++
				}
				for (var j in municipio.diagnosticos) {
					totalizadores["diagnostico_" + municipio.diagnosticos[j]]++
				}
			} else {
				if (municipio.mapmark.map != null) {
					municipio.mapmark.setMap(null);
				}
			}
		}
		for (var id in totalizadores){
			$("#" + id).text(totalizadores[id]);
		}
	}

	function search(event) {
		$.ajax({
			url: "/dashboard/mapsearch/",
			type: 'GET',
			data: $("#changelist-search").serializeArray(),
			cache: true,
			success: function(return_data) {
				if (return_data.result == 'NOT_FOUND') {
					$("#search-panel").html('Nenhum município encontrado.');
					return;
				}
				if (return_data.ids.length == 1) {
					$("#search-panel").html('um município encontrado.');
				} else {
					$("#search-panel").html(return_data.ids.length + ' municípios encontrados.');
				}
				var total = 0;
				for (var i in return_data.ids) {
					var municipio = municipiosArray[return_data.ids[i]];
					if (typeof(municipio) != 'undefined') {
						if (municipio.mapmark.map == null) {
							municipio.mapmark.setMap(map);
						}
						google.maps.event.trigger(municipio.mapmark, 'click');
						total = total + 1;
					}
				}

				if (total == 0) {
					$("#search-panel").html('Nenhum município encontrado.');
					return;
				}
				if (total == 1) {
					$("#search-panel").html('um município encontrado.');
				} else {
					$("#search-panel").html(total + ' municípios encontrados.');
				}
			}});
		return false;
	}

	function open_report(event) {
		event.preventDefault();

		var href = $(this).attr('href');
		var data = $("#filter_form").serialize();
		
		if (href.indexOf("?") < 0) {
			href = href + "?" + data
		} else {
			href = href + "&" + data
		}
		
		var win = window.open(href, '', '');
		win.focus();
		return false;
	}

})(django.jQuery);
