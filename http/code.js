String.prototype.endsWith = function(suffix) {
    return this.indexOf(suffix, this.length - suffix.length) !== -1
}

var saveUrl = function(){
  var dfd = $.Deferred()
  $.ajax({
    url: '../cgi-bin/dataset_url',
    data: {
      url: scraperwiki.readSettings().target.url
    }
  }).done(function(currentUrl){
    dfd.resolve(currentUrl)
  }).fail(function(jqXHR){
    dfd.reject('Source dataset URL could not be saved.', jqXHR.status + ' ' + jqXHR.statusText)
  })
  return dfd.promise()
}

var readUrl = function(){
  var dfd = $.Deferred()
  $.ajax({
    url: '../cgi-bin/dataset_url'
  }).done(function(currentUrl){
    dfd.resolve(currentUrl)
  }).fail(function(){
    dfd.resolve('')
  })
  return dfd.promise()
}

var pipInstall = function(){
  var dfd = $.Deferred()
  scraperwiki.exec('pip install --user --upgrade -r ~/tool/requirements.txt; echo "Exit Code: $?"').done(function(stdout){
    if($.trim(stdout).endsWith('Exit Code: 0')){
      dfd.resolve()
    } else {
      // Something went wrong with pip install!
      // There will be a traceback in stdout.
      dfd.reject('Python dependencies could not be installed.', $.trim(stdout))
    }
  }).fail(function(jqXHR){
    dfd.reject('Exec endpoint returned ' + jqXHR.status + ' ' + jqXHR.statusText, jqXHR.status + ' ' + jqXHR.statusText)
  })
  return dfd.promise()
}

var showConfig = function(){
  $('#settings').show()
  $('#loading').hide()
  $('#url').val(scraperwiki.readSettings().source.url + '/cgi-bin/rss/feed.rss')
}

$(function(){
  readUrl().done(function(currentUrl){
    if($.trim(currentUrl) == ''){
      $('#loading p').html('Installing RSS endpoint&hellip;')
      $.when(saveUrl(), pipInstall()).then(function(){
        showConfig()
      }, function(errorMessage, errorDetails){
        console.log(errorDetails)
        $('#error').show().children('p').text('RSS installation failed:<br/>' + errorMessage)
        $('#loading').hide()
      })
    } else {
      showConfig()
    }
  })
  $(document).on('focus', '#url', function(e){
    e.preventDefault()
    this.select()
  }).on('mouseup', '#url', function(e){
    e.preventDefault()
  })
  $('.nav li').on('click', function(e){
    e.preventDefault()
    $(this).parent().addClass('active').siblings('.active').removeClass('active')
    var target = $(this).attr('href')
    $(target).show().siblings('.tab').hide()
  })
})
