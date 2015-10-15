$(document).ready(function() {
  $("#delete").change(function() {
    if ($("#delete input[type=checkbox]:checked").length) {
      var html = "";
      if ($("#delete input[type=checkbox]:checked").length == 1) {
        html += "&nbsp&nbsp<span>" + $("#delete input:checkbox:checked").length + " box selected: </span>";
      }
      else {
        html += "&nbsp&nbsp<span>" + $("#delete input:checkbox:checked").length + " boxes selected: </span>";
      }
      html += "<input type='submit' class='btn-primary' value='Batch Delete'>";
      $('div#deletedisplay').html(html);
    }
    else {
      $('div#deletedisplay').html("");
    }
    $('#delete input[type=checkbox]').each(function () {
      var id = $(this).val();
      if (this.checked) {
        $("tr#"+id).addClass("rowchecked");
      }
      else {
        $('tr#'+id).removeClass("rowchecked");
      }
    });
  });
});
