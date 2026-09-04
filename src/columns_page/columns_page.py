def columns_page() -> str:
    return (
        """<!doctype html><html><head><meta charset="utf-8"><title>Columns</title>
<style>body{font-family:sans-serif}table{border-collapse:collapse}"""
        """td,th{border:1px solid #ccc;padding:4px 8px}</style>
</head><body>
<div id="columns"></div>
<script>
function itemsHtml(items){
  return '<table><thead><tr><th>id</th><th>kind</th>"""
        """<th>title</th><th>state</th></tr></thead><tbody>'+items.map(it=>
    `<tr><td><a href="/?id=${it.id}">${it.id}</a></td><td>${it.kind}</td>"""
        """<td>${it.title}</td><td>${it.state}</td></tr>`
  ).join('')+'</tbody></table>';}
function columnHtml(col){
  return `<h2>${col.name} (${col.role}) """
        """${col.in_progress}/${col.wip}</h2>${itemsHtml(col.items)}`;}
fetch('/api/columns').then(r=>r.json()).then(cols=>{
  document.getElementById('columns').innerHTML=cols.map(columnHtml).join('');});
</script>
</body></html>"""
    )
