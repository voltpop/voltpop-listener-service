<html>
<head>
  <title>Form Output</title>
  <link rel="stylesheet" href="css/main.scss">
  <link rel="stylesheet" href="css/toolbar.scss">
  <ul>
    <li style="float:right"><a class="active" href="add_channel">New Channel</a></li> 
    <li style="float:right"><a class="active" href="query_channel">Queue Logs</a></li> 
    <li style="float:right"><a class="active" href="#home">Home</a></li> 
  </ul> 
</head>
<body>
<div>Adding Channel: <b><?php echo $_GET["key"]; ?></b> </div>
<div>Secured: <b><?php echo $_GET["secured"]; ?></b> </div>
<div>Enabled: <b><?php echo $_GET["enabled"]; ?></b> </div>
<div>Queryable: <b><?php echo $_GET["queryable"]; ?></b> </div>
</body>
</html>

