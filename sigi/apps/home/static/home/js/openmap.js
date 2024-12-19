const stadia_tiles_options = {
    attribution:
        `
      &copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a>
      &copy; <a href="https://stamen.com/" target="_blank">Stamen Design</a>
      &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a>
      &copy; <a href="https://www.openstreetmap.org/about/" target="_blank">OpenStreetMap contributors</a>"
      `
};
var mymap;
var orgao_layer_group = L.layerGroup();
var map_center = [-14.235004, -51.92528];
var options = { color: 'blue', fillColor: 'red', fillOpacity: 0.4, radius: 500 };
var unfiltred_options = { color: 'red', fillColor: 'red', fillOpacity: 0, radius: 1000 };
$(document).ready(function () {
    $("input[type=checkbox]").change(filtra);
    var search_field = $("#map-search");

    if (search_field) {
        search_field.autocomplete({
            source: search_field.attr("data-source"),
            minLength: 3,
            select: function (event, ui) {
                map_fly_to(ui.item);
            }
        });
    }

    var base_layers = {
        "Toner": L.tileLayer(
            "https://tiles.stadiamaps.com/tiles/stamen_toner/{z}/{x}/{y}{r}.png",
            stadia_tiles_options,
        ),
        "Toner lite": L.tileLayer(
            "https://tiles.stadiamaps.com/tiles/stamen_toner_lite/{z}/{x}/{y}{r}.png",
            stadia_tiles_options,
        ),
        "Terrain": L.tileLayer(
            "https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png",
            stadia_tiles_options,
        ),
        "Water color": L.tileLayer(
            "https://tiles.stadiamaps.com/tiles/stamen_watercolor/{z}/{x}/{y}.jpg",
            stadia_tiles_options,
        ),
        "Open street": L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: 'Map data and imagery &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, ',
            tileSize: 512,
            zoomOffset: -1
        }),
    };

    mymap = L.map('map', {
        center: map_center,
        zoom: 4.5,
        zoomSnap: 0.01,
        layers: [base_layers.Terrain, orgao_layer_group]
    });

    mymap.zoomControl.options.zoomInTitle = "{% trans 'Aproximar' %}";
    mymap.zoomControl.options.zoomOutTitle = "{% trans 'Afastar' %}";
    mymap.zoomControl.setPosition("bottomright");

    L.control.layers(base_layers).addTo(mymap);

    mymap.on("popupopen", function (e) {
        var popup = e.popup;
        mark = popup._source;
        $.ajax({
            type: "GET",
            url: window.__openmapdetail_prefix__.replace("changeme", mark.orgao_id),
            encode: true
        }).done(function (content) {
            popup.setContent(content);
        })
    })

    filtra();

    function filtra() {
        var name = $(this).attr("name"),
            value = $(this).attr("value"),
            checked = $(this).prop("checked");

        if (name) {
            $(`input[type=checkbox][name=${name}][value=${value}]`).prop("checked", checked);
        }

        if (value == "ignore") {
            controls = $(this).attr("data-controls");
            $("input[type=checkbox][name='" + controls + "']").prop("disabled", checked);
        }

        if (value == "none") {
            $("input[type=checkbox][name='" + name + "'][value!='none']").prop("checked", !checked);
        } else {
            if (checked) {
                $("input[type=checkbox][name='" + name + "'][value='none']").prop("checked", false);
            }
        }

        if (name == 'regiao') {
            $("input[type=checkbox][name='uf'][data-regiao='" + value + "']").prop('checked', checked);
        }

        if (name == 'uf') {
            var sigla_regiao = $(this).attr('data-regiao'),
                regiao = $("input[type=checkbox][value='" + sigla_regiao + "']");
            if ($("input[type=checkbox][name='uf'][data-regiao='" + sigla_regiao + "']:checked").length == 0) {
                $(regiao).prop('checked', false).prop("indeterminate", false);
            } else if ($("input[type=checkbox][name='uf'][data-regiao='" + sigla_regiao + "']:not(:checked)").length == 0) {
                $(regiao).prop('checked', true).prop("indeterminate", false);
            } else {
                $(regiao).prop("indeterminate", true)
            }
        }

        var formData = $("#filterForm").serializeArray();
        $("#filter-spinner").toggleClass("d-none d-flex");
        $.ajax({
            type: "GET",
            url: window.__openmapdata__,
            data: formData,
            dataType: "json",
            encode: true,
        }).done(function (returnedData) {
            $("#filter-spinner").toggleClass("d-none d-flex");
            $("#totalOrgao").text(returnedData.length);
            var new_data_layer = L.layerGroup();
            returnedData.forEach(function (casa) {
                if (casa[2] === null || casa[3] === null) {
                    alert(casa[1] + " está sem coordenadas geográficas e não será plotada");
                } else {
                    var mark = L.circle([casa[2], casa[3]], options).bindTooltip(casa[1]).bindPopup('<div class="preloader-wrapper small active"><div class="spinner-layer spinner-green-only"><div class="circle-clipper left"><div class="circle"></div></div><div class="gap-patch"><div class="circle"></div></div><div class="circle-clipper right"><div class="circle"></div></div></div></div>').addTo(new_data_layer);
                    mark.orgao_id = casa[0]
                }
            });
            orgao_layer_group.clearLayers();
            orgao_layer_group.addLayer(new_data_layer);
        })
    }

    $("#clear-filters").click(function (event) {
        event.preventDefault();
        $("input[type=checkbox][name=tipo_orgao]").prop('checked', false);
        $("input[type=checkbox][name=tipo_servico]").prop('checked', false);
        $("input[type=checkbox][name=tipo_convenio]").prop('checked', false);
        $("input[type=checkbox][name=regiao]").prop('checked', false);
        $("input[type=checkbox][name=uf]").prop('checked', false);
        $("input[type=checkbox][name=gerente]").prop('checked', false);
        filtra();
    });
    $("#center-map").click(function (event) {
        event.preventDefault();
        mymap.flyTo(map_center, 4.5);
    });
});
function map_fly_to(obj) {
    mymap.flyTo([obj.lat, obj.lng], 8.5);
    var encontrado = false;
    mymap.eachLayer(function (layer) {
        if (layer instanceof L.Circle) {
            if (layer.orgao_id == obj.id) {
                layer.openPopup();
                encontrado = true;
            }
        }
    });
    if (!encontrado) {
        var mark = L.circle([obj.lat, obj.lng], unfiltred_options).bindTooltip(obj.label).bindPopup("").addTo(mymap);
        mark.orgao_id = obj.id
        mark.openPopup();
    }
}