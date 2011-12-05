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
  $("div.ui-radio span.ui-btn-text:contains('---------')").parentsUntil("ul").hide()

  // para todo input do from registra um evento
  // ao modificar o campo
  $("div.ui-field-contain textarea, div.ui-field-contain input, div.ui-field-contain select").change(function () {
    $.ajax({
      data: $('#diagnostico').serializeArray()
    })
  })

  // se carregou o js sem erros mostra as perguntas
  $("#waiting").hide();
  $("#working").hide();
  $("#form").show();
});
