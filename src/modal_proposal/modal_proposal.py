def modal_proposal() -> str:
    """Script fragment for the board modal: window.showProposal(d, box).

    For a proposal item it fetches the pattern the sheet's page line names
    and puts the pattern and fix paragraphs first, then the target and care
    line, and folds the diff into a details element, so the Board reads why
    before what. Other kinds are left to the default details.
    """
    return """<script>
window.showProposal=function(d,box){
  var parts=(d.sheet||'').split('\\n---\\n');var head=parts[0];var diff=parts[1]||'';
  var f={};head.split('\\n').forEach(function(l){var i=l.indexOf(': ');
    if(i>0)f[l.slice(0,i)]=l.slice(i+2);});
  var esc=function(s){return String(s==null?'':s).replace(/[&<>]/g,function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});};
  var html='<div><strong>Proposal:</strong> '+esc(d.title)+'</div>'
    +'<div><strong>Target:</strong> '+esc(f.target)
    +' &middot; <strong>care:</strong> '+esc(f.care)+'</div>'
    +'<div id="modalWhy"><em>loading the pattern&hellip;</em></div>'
    +'<details><summary>the exact change (diff)</summary>'
    +'<pre style="white-space:pre-wrap">'+esc(diff)+'</pre></details>';
  box.innerHTML=html;var why=g('modalWhy');
  if(!/^vm-/.test(f.page||'')){why.innerHTML='<em>no pattern cited</em>';return;}
  fetch('/api/item?id='+encodeURIComponent(f.page)).then(function(r){return r.json();})
  .then(function(p){var t=(p.sheet||'').replace(/^cost:.*$/m,'');
    why.innerHTML='<div style="white-space:pre-wrap">'+esc(t.trim())+'</div>';})
  .catch(function(){why.innerHTML='<em>pattern not readable</em>';});};
</script>"""
