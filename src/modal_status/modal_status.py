def modal_status() -> str:
    """Script fragment for the board modal: defines window.loadStatus(id).

    loadStatus fetches GET /api/status?id=<id> and renders the Story's
    state, one line per job (kind, function, state, retries, claimed) and
    one line per run (time, item, gate, rule, retries, tokens, turns, usd,
    harness, model) into a box it appends after the decision line.
    """
    return """<script>
window.loadStatus=function(id){
  var box=document.getElementById('modalStatus');
  if(!box){box=document.createElement('div');box.id='modalStatus';
    box.style.cssText='max-height:30vh;overflow:auto;font-size:12px;margin-top:8px';
    document.getElementById('modalDecision').after(box);}
  box.innerHTML='';
  fetch('/api/status?id='+encodeURIComponent(id)).then(r=>r.json()).then(s=>{
    if(!s||typeof s!=='object'||!Array.isArray(s.jobs)||!Array.isArray(s.runs))return;
    var jobs=s.jobs.map(j=>'<div>'+j.kind+' '+j.function+' '+j.state
      +' retries:'+j.retries+' '+(j.claimed?'claimed':'unclaimed')+'</div>');
    var runs=s.runs.map(r=>'<div>'+String(r.ts||'').slice(0,19)+' '+r.item
      +' '+r.gate+' '+(r.rule||'')+' retries:'+r.retries+' '+r.tokens+' tok '
      +r.turns+' turns $'+r.usd+' '+r.harness+' '+r.model+'</div>');
    box.innerHTML='<strong>Status: '+s.state+'</strong>'+jobs.join('')+runs.join('');
  }).catch(()=>{box.innerHTML='';});};
</script>"""
