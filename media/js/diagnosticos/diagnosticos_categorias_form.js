// cntabiliza a quantidade de requests
// ajax para nao desabilitar o loader
// antes da hora
var nun_ajax = 0;

$('#page').live('pageinit', function(event){
  // variaveis globais para as requisicoes ajax
  $.ajaxSetup({
    url: $(location).attr('href'),
    cache: false,
    type: 'POST',
    beforeSend: function() {
      nun_ajax++;
      $('#working').show();
    },
    success: function(data) {
      nun_ajax--;
      if (nun_ajax == 0)
        $('#working').hide();

      //Retirando o span existente
      $("span.errors").html("");
      if (data.mensagem == "erro") {
        for (var campo in data.erros) {
          $("#"+ campo + " span").html(data.erros[campo].join('\n'))
        }
      }
    },
    error: function(msg) {
      nun_ajax--;
      if (nun_ajax == 0)
        $('#working').hide();
      $("#open-dialog").click();
    }
  });

  // remove a resposta vazia da interface
  $("div.ui-radio span.ui-btn-text:contains('---------')").parentsUntil("ul").hide();

  // para todo input do from registra um evento
  // ao modificar o campo
  $("div.ui-field-contain textarea, div.ui-field-contain input, div.ui-field-contain select").change(function () {
    // mostra ou esconde uma pergunta dependente
    var id_to_open = []
    var id_to_close = []
    $('input[name=' + $(this).attr('name') + ']').each(function () {
        schema = $(this);
        schema_to_open = schema.attr('schema_to_open');
        if (schema_to_open) {
            if (schema.is(':checked'))
                id_to_open.push(schema_to_open)
            else
                id_to_close.push(schema_to_open)
        }
    });

    for (var i in id_to_close) {
        id = id_to_close[i]
        // Evita apagar uma pergunta caso ela possa
        // ser exibida por outra questão
        if (id_to_open.indexOf(id_to_close[i]) == -1) {
            // limpa o valor para não salva-lo
            // no submit do form
            $("#" + id + " input").val('');
            $("#" + id).slideUp();
        }
    }

    // Exibe as perguntas que devem estar disponiveis
    for (var i in id_to_open) {
        id = id_to_open[i]
        $("#" + id).slideDown();
    }

    $.ajax({
      data: $('#diagnostico').serializeArray()
    });

  });

  $('input[schema_to_open]').each(function () {
    schema = $(this);
    schema_to_open = $("#" + schema.attr('schema_to_open'));
    schema_to_open.hide();
  });

  $('input[schema_to_open]:checked').each(function () {
    schema = $(this);
    schema_to_open = $("#" + schema.attr('schema_to_open'));
    schema_to_open.show();
  });

  // se carregou o js sem erros mostra as perguntas
  $("#waiting").hide();
  $("#working").hide();
  $("#form").show();
});
