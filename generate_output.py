import sys

head = """
<!doctype html>

<html lang="en">
<head>
  <meta charset="utf-8">

  <title>Tendrl API coverage</title>
  <script src="https://kryogenix.org/code/browser/sorttable/sorttable.js"></script>
  <style type="text/css">
  /* Sortable tables */
  table.sortable thead {
      background-color:#eee;
      color:#666666;
      font-weight: bold;
      cursor: default;
  }
  </style>
</head>

<body>
<div style="margin:10px">
<h1>API call coverage</h1>
<table class="sortable">
"""
print(head)
for line in sys.stdin:
    print("<tr><td>" + "</td><td>".join(line.split(",")) + "</td></tr>")

tail = """
</table>
</div>
</body>
</html>
"""
print(tail)
