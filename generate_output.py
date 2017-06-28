import sys

head = """
<!doctype html>

<html lang="en">
<head>
  <meta charset="utf-8">

  <title>Tendrl API coverage</title>
  <script type='text/javascript' src="https://kryogenix.org/code/browser/sorttable/sorttable.js"></script>
  <style type="text/css">
  /* Sortable tables */
  table.sortable thead {
      background-color:#eee;
      color:#666666;
      font-weight: bold;
      cursor: default;
  }
  .red {
      background-color:#FF6347;
  }
  </style>
</head>

<body>
<div style="margin:10px">
<h1>API call coverage</h1>
<table class="sortable">
"""
print(head)
first = True
for line in sys.stdin:
    if first:
        print("<thead>")
        print("<tr><td>" + "</td><td>".join(line.split(",")) + "</td></tr>")
        print("</thead>")
        first = False
        print("<tbody>")
    else:
        row = "".join(["</td><td>" + x if x != "No" 
              else "</td><td class='red'>" + x 
              for x in line.split(",")]) + "</td></tr>"
        row = "<tr>" + row[5:]
        print(row)
print("</tbody>")
tail = """
</table>
</div>
</body>
</html>
"""
print(tail)
