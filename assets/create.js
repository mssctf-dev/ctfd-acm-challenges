// Markdown Preview

$('#desc-edit').on('shown.bs.tab', function (event) {
    if (event.target.hash === '#desc-preview'){
        $(event.target.hash).html(
            window.challenge.render($('#desc-editor').val())
        )
    }
});

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip();
});
