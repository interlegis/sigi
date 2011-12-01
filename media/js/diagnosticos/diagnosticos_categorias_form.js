$('#page').live('pageinit', function(event){
  // variaveis globais para as requisicoes ajax
  $.ajaxSetup({
    url: $(location).attr('href'),
    cache: false,
    type: 'POST',
    success: function(data) {
        //Retirando o span existente
        $("span.errors").html("");
        if (data.mensagem == "erro") {
          for (var campo in data.erros) {
            $("#"+ campo + " span").html(data.erros[campo].join('\n'))
          }
        }
    },
    error: function(msg) {
      $("#open-dialog").click()
    },
  });

  // remove a resposta vazia da interface
  $("div.ui-radio span.ui-btn-text:contains('---------')").parentsUntil("ul").hide()

  // para todo input do from registra um evento
  // ao modificar o campo
  $("div.ui-field-contain input, div.ui-field-contain select").change(function () {
    $.ajax({
      data: $('#diagnostico').serializeArray()
    })
  })

  // se carregou o js sem erros mostra as perguntas
  $("#waiting").hide();
  $("#form").show();
});
