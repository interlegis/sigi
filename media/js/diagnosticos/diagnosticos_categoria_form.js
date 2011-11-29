// cntabiliza a quantidade de requests
// ajax para nao desabilitar o loader
// antes da hora
var nun_ajax = 0;

// variaveis globais para as requisicoes
// ajax
$.ajaxSetup({
  url: $(location).attr('href'),
  cache: false,
  type: 'POST',
  dataType: "text",
  beforeSend: function() {
    nun_ajax++
    $('#working').show()
  },
  success: function() {
    nun_ajax--
    if (nun_ajax == 0) {
      $('#working').hide()
    }
  },
  error: function(msg) {
    $('#working').hide()
    //TODO melhorar o tratamento de erro
    alert('Ops!\n' + msg);
  }
});

$(document).ready(function() {
  // remove a resposta vazia da interface
  $("div.ui-radio span.ui-btn-text:contains('---------')").parentsUntil("ul").hide()

  // para todo input do from registra um evento
  // ao modificar o campo
  $("div.ui-field-contain input").change(function () {
    $.ajax({
      data: {
        schema: this.name,
        value: this.value
      }
    })
  })
});
