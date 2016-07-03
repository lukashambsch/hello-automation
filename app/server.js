var express = require('express');
var app = express();

var port = process.env.PORT || 8081;

app.get('/', function(req, res) {
  res.send('Automation for the People');
});

var listener = app.listen(port, function() {
   console.log('App listening on port ' + listener.address().port);
});
