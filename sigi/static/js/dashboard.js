$(document).ready(function () {
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
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
  $('.modal').modal();
  $('.dropdown-trigger').dropdown();
  $('.collapsible').collapsible();
  $("a.dashlink[data-target]").off('click').on('click', function(e) {
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
  container.closest('.card').find('.full-preloader').removeClass('hide');
  $.get(url, function(data) {
    container.html(data);
    container.closest('.card').find('.full-preloader').addClass('hide');
    setlinks();
  }).fail(function() {
    container.closest('.card').find('.full-preloader').html("Ocorreu um erro. Tente recarregar a página");
  });
}

function plot_chart(canvas, url) {
  canvas.closest('.card').find('.full-preloader').removeClass('hide');
  $.get(url, function(data) {
    var chart_name = canvas.attr("data-chart-name");
    var has_action_links = canvas.attr("data-has-action-links");

    var new_canvas = $(canvas.clone()).insertBefore(canvas);
    canvas.remove();
    canvas = new_canvas;
    canvas.removeClass("hide");

    var ctx = canvas.get(0).getContext("2d");
    var myChart = new Chart(ctx, data);

    if (has_action_links) {
      if (data.actionblock) {
        $(`#${chart_name}-action-links`).html(data.actionblock).removeClass("hide");
      } else {
        $(`#${chart_name}-previlink`).attr('href', data.prevlink);
        $(`#${chart_name}-nextlink`).attr('href', data.nextlink);
        $(`#${chart_name}-action-links`).removeClass("hide");
      }
    }
    setlinks();
    canvas.closest('.card').find('.full-preloader').addClass('hide');
  }).fail(function() {
    canvas.closest('.card').find('.full-preloader').html("Ocorreu um erro. Tente recarregar a página");
  });
}