//load initial data
$(function() {
        $.get('/_data', {
          }, function(result) {
        $("#table-container").html(result);
      });
      return false;
});


//ddm items click
$(function() {
    $('#table-container').on('click', '.ddm-item', function(event) {
        event.preventDefault(); // prevent the default click action
        $.get(event.target.id, {
          }, function(result) {
        $("#table-container").html(result);
      });
      return false;
    });
});


//reset search settings btn click
$(function() {
    $('#table-container').on('click', '#reset', function(event) {
        event.preventDefault(); // prevent the default click action
        $.get('/_data?t=7&s=0', {
          }, function(result) {
        $("#table-container").html(result);
      });
      return false;
    });
});


//modal
$('#statsModal').on('shown.bs.modal', function () {
        ga('send', 'event', 'Buttons', 'click', 'Stats');
        $.get('/_stats', {
          }, function(result) {
        $('#statsModalBody').html(result);
      });
})

