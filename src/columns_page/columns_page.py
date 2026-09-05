from columns_modal.columns_modal import columns_modal


def columns_page() -> str:
    """Return the columns board HTML page as a string."""
    return (
        """<!doctype html><html><head><meta charset="utf-8"><title>Columns</title>
<style>body{font-family:system-ui,sans-serif;font-size:14px;padding:16px;margin:0}"""
        """#columns{display:flex;gap:12px;overflow-x:auto;align-items:flex-start}"""
        """.col{width:144px;flex:0 0 144px;background:#f4f5f7;border-radius:8px;"""
        """padding:10px;box-sizing:border-box}.col.paused{opacity:0.5}"""
        """.hd{display:flex;justify-content:space-between;align-items:baseline;"""
        """font-size:13px;font-weight:bold;white-space:nowrap;overflow:hidden;"""
        """margin-bottom:8px}.hd .nm{overflow:hidden;text-overflow:ellipsis;"""
        """white-space:nowrap}.hd .rl{font-weight:normal;color:#888;margin-left:4px}"""
        """.hd .ct{flex:0 0 auto;margin-left:6px}"""
        """.card{background:#fff;border:1px solid #d0d4da;border-radius:6px;"""
        """padding:8px;margin-bottom:8px;word-break:break-word;cursor:pointer}"""
        """.card.reopened{background:#fff6bf}.card.in_progress{background:#bfe9e6}"""
        """.card .l1{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}"""
        """.card .l1 .k{color:#888;font-size:12px;margin-left:4px}"""
        """.pill{display:inline-block;padding:1px 6px;border-radius:10px;"""
        """background:#e6e8eb;font-size:12px}.empty{color:#888}</style>
</head><body>
<div id="columns"></div>
<script>
function esc(s){const d=document.createElement('div');d.textContent=s;"""
        """return d.innerHTML;}
function cardHtml(it){
  return `<div class="card ${esc(it.state)}" onclick="openItem('${esc(it.id)}')">"""
        """<div class="l1"><a href="/?id=${esc(it.id)}" """
        """onclick="event.stopPropagation()">${esc(it.id)}</a>"""
        """<span class="k">${esc(it.kind)}</span></div>"""
        """<div>${esc(it.title)}</div><div><span class="pill">${esc(it.state)}"""
        """</span></div></div>`;}
function columnHtml(col){
  const cls=col.wip===0?'col paused':'col';
  const body=col.items.length?col.items.map(cardHtml).join('')"""
        """:'<div class="empty">nothing here</div>';
  return `<div class="${cls}"><div class="hd"><span class="nm">${esc(col.name)}"""
        """<span class="rl">${esc(col.role)}</span></span><span class="ct">"""
        """${col.in_progress}/${col.wip}</span></div>${body}</div>`;}
fetch('/api/columns').then(r=>r.json()).then(cols=>{
  document.getElementById('columns').innerHTML=cols.map(columnHtml).join('');});
</script>"""
        + columns_modal()
        + """
</body></html>"""
    )
