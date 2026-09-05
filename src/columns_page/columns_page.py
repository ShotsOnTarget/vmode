def columns_page() -> str:
    return (
        """<!doctype html><html><head><meta charset="utf-8"><title>Columns</title>
<style>body{font-family:sans-serif}#columns{display:flex;flex-direction:row;"""
        """overflow-x:auto;white-space:nowrap}.col{display:inline-block;"""
        """vertical-align:top;width:220px;flex:0 0 220px;margin-right:8px}"""
        """.col.paused{background:#ddd;color:#888}.card{border:1px solid #ccc;"""
        """border-radius:4px;padding:6px;margin-bottom:6px}</style>
</head><body>
<div id="columns"></div>
<script>
function cardHtml(it){
  return `<div class="card"><a href="/?id=${it.id}">${it.id}</a> """
        """${it.kind}<br>${it.title}<br>${it.state}</div>`;}
function columnHtml(col){
  const cls=col.wip===0?'col paused':'col';
  return `<div class="${cls}"><h2>${col.name} (${col.role}) """
        """${col.in_progress}/${col.wip}</h2>${col.items.map(cardHtml)"""
        """.join('')}</div>`;}
fetch('/api/columns').then(r=>r.json()).then(cols=>{
  document.getElementById('columns').innerHTML=cols.map(columnHtml).join('');});
</script>
</body></html>"""
    )
