$(document).ready(function () {
  setlinks();
  $("div[data-source]").each(function(index, container) {
    var container = $(container);
    var url = container.attr('data-source');
    get_content(container, url);
  });
  $("canvas[data-source]").each(function(index, canvas) {
    var canvas = $(canvas)
    var url = canvas.attr("data-source");
    plot_chart(canvas, url);
  });
});
      
function setlinks() {
  $("a[data-target]").off('click').on('click', function(e) {
    e.preventDefault();
    var $this = $(this);
    var target = $("#"+$this.attr('data-target'));
    var url = $this.attr('href');
    if (target.is("canvas")) {
      plot_chart(target, url);
    } else if (target.is("div")) {
      get_content(target, url);
    }
  });
}
      
function get_content(container, url) {
  $.get(url, function(data) {
    container.html(data);
    setlinks();
  });
}
      
function plot_chart(canvas, url) {
  $.get(url, function(data) {
    var new_canvas = $(canvas.clone()).insertBefore(canvas);
    canvas.remove();
    canvas = new_canvas;
    var ctx = canvas.get(0).getContext("2d");
    if (data.type == 'pie') {
      var myChart = new Chart(ctx).Pie(data.data, data.options);
    } else if (data.type == 'line') {
      var myChart = new Chart(ctx).Line(data.data, data.options);
    } else if (data.type == 'bar') {
      var myChart = new Chart(ctx).Bar(data.data, data.options);
    }
        
    if (canvas.is("[data-legend-id]")) {
      var legend_container = $("#"+canvas.attr("data-legend-id"));
      legend_container.html(myChart.generateLegend());
    }
    if (canvas.is("[data-prevlink-id]")) {
      var prevlink = $("#"+canvas.attr("data-prevlink-id"));
      prevlink.attr('href', data.prevlink);
    }
    if (canvas.is("[data-nextlink-id]")) {
      var nextlink = $("#"+canvas.attr("data-nextlink-id"));
      nextlink.attr('href', data.nextlink);
    }
  });
}