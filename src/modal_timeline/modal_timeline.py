def modal_timeline() -> str:
    """Script fragment for the board modal: defines window.loadTimeline(id).

    loadTimeline fetches GET /api/timeline?id=<id> and renders one line per
    event (time, actor, gate, item, rule, tokens) into a box it appends after
    the decision line. Work item: 0005-1 modal_timeline code.
    """
    return """<script>
window.loadTimeline=function(id){
  var box=document.getElementById('modalTimeline');
  if(!box){box=document.createElement('div');box.id='modalTimeline';
    box.style.cssText='max-height:30vh;overflow:auto;font-size:12px;margin-top:8px';
    document.getElementById('modalDecision').after(box);}
  box.innerHTML='';
  fetch('/api/timeline?id='+encodeURIComponent(id)).then(r=>r.json()).then(ev=>{
    if(!Array.isArray(ev))return;
    var tok=e=>e.tokens>0?' ('+e.tokens+' tok)':'';
    var rows=ev.map(e=>'<div>'+String(e.ts||'').slice(0,19)+' <b>'+e.actor+'</b> '
      +e.gate+' '+e.item+' '+(e.rule||'')+tok(e)+'</div>');
    box.innerHTML='<strong>Timeline ('+ev.length+')</strong>'+rows.join('');
  }).catch(()=>{box.innerHTML='';});};
</script>"""
