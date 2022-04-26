$(document).ready(function () {
    $(".search-text").on("input change", function () {
        var $resultbox = $(".search-result");
        var $this = $(this);
        var term = $this.val();
        var url = $this.attr("data-source");
        var param_name = $this.attr("data-param");
        var item_click = $resultbox.attr("data-item-click");
        var callback = window[item_click];
        var query_param = {};

        query_param[param_name] = term;

        if (term.length < 3) {
            $resultbox.html("");
            $resultbox.addClass("hide");
            return;
        }

        $.get(url, query_param, function (data) {
            $resultbox.html("");
            for (i in data) {
                var plain = JSON.stringify(data[i]);
                var $item = $(`<a href="#" class="search-result-item" data-retrieved='${plain}'></a>`);
                $item.html(data[i].label);
                $resultbox.append($item);
            }
            $resultbox.removeClass("hide");

            $(".search-result-item").on("click", function () {
                var plain = $(this).attr("data-retrieved");
                var obj = JSON.parse(plain);
                $this.val(obj.label);
                $resultbox.html("").addClass("hide");
                callback(obj);
            });
        });
    });
});