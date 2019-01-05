function switchCategory(catname) {
  $('.categorydiv').hide();
  $('.category').removeClass('active');
  $('#button_' + catname).addClass('active');
  $('#category_' + catname).show();
}

function doPopup() {
  var width = maxWidth();
  width = width + (width * 0.1);
  var options = 'menubar=no,location=no,status=no,titlebar=no,toolbar=no,scrollbars=no,height=' + $('#wrapper').height() + ',width=' + width;
  console.log(options);
  window.open(window.location.href, 'aw-watcher-manual-flaskweb', options);
}

function maxWidth() {
  var widths = [$('#categories').width(), $('#links').width()];
  $('.categorydiv').each(function() {
    console.log(this);
    console.log($(this).width());
    widths.push($(this).width());
  });
  return Math.max(...widths);
}
