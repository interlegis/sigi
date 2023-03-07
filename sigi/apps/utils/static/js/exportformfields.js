$(document).ready(function () {
    if ($("#id_resource").length) {
        $("#id_resource").change(change_resource);
        change_resource();
    }
});

function change_resource() {
    var selected_resource_id = $("#id_resource").val();
    $("div[id^=id_selected_fields").parent().hide();
    $(`div#id_selected_fields_${selected_resource_id}`).parent().show();
}
