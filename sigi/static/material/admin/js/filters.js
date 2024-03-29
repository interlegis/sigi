$("#apply-filters").on("click", function () {
    var query = [];
    var retorno = decodeURIComponent(window.location.search).replace("?", "").split("&");
    var remove = [];
    var filters = $(".admin_filter");
    var dal_filters = $("[id$=dal-filter]")
    for (i = 0; i < filters.length; i++) {
        var element = $(filters[i]);
        var filter;
        if (element.attr("type") == "text") {
            var cleaner = decodeURIComponent(element.attr("data-clear")).replace("?", "").split("&");
            if (element.val() == "") {
                filter = []
            } else {
                filter = [element.attr("name") + '=' + decodeURIComponent(element.val())];
            }
            filter = filter.concat(cleaner);
        } else {
            filter = decodeURIComponent(element.val()).replace("?", "").split("&");
        }
        remove = remove.concat(retorno.filter(x => !filter.includes(x)));
        query = query.concat(filter.filter(x => !retorno.includes(x)));
    }

    for (i = 0; i < dal_filters.length; i++) {
        var element = $(dal_filters[i]);
        var filter = [];
        if (element.val() != "") {
            filter = [element.serialize()];
        }
        remove = remove.concat(retorno.filter(x => x.includes(element.attr("name"))));
        query = query.concat(filter);
    }

    query = query.concat(retorno.filter(x => !remove.includes(x)));
    query = query.filter(x => x != "");
    window.location.href = "?" + (query.join("&"));
});
