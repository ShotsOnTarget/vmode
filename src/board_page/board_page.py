def board_page() -> str:
    return """<!doctype html><html><head><meta charset="utf-8"><title>Board</title>
<style>body{font-family:sans-serif}table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:4px 8px}tr.row{cursor:pointer}#reason{display:none}</style>
</head><body>
<h1>Intents</h1>
<table id="intents"><thead><tr><th>id</th><th>title</th><th>state</th><th>care</th><th>stories</th></tr></thead><tbody></tbody></table>
<div id="tree"></div>
<div id="decide" style="display:none">
<button id="yes">Yes</button><button id="no">No</button>
<span id="reason"><input id="reasonInput" placeholder="reason"><button id="send">Send</button></span>
</div>
<script>
let curId=null;
function loadIntents(){fetch('/api/intents').then(r=>r.json()).then(list=>{
  document.querySelector('#intents tbody').innerHTML=list.map(it=>
    `<tr class="row" data-id="${it.id}"><td>${it.id}</td><td>${it.title}</td><td>${it.state}</td><td>${it.care}</td><td>${it.stories_done}/${it.stories_total}</td></tr>`
  ).join('');});}
function nodeHtml(node){const kids=node.children&&node.children.length?
  '<ul>'+node.children.map(nodeHtml).join('')+'</ul>':'';
  return `<li><a href="#" data-id="${node.id}">${node.id} ${node.title||''}</a>${kids}</li>`;}
function load(id){curId=id;
  document.getElementById('decide').style.display='block';
  document.getElementById('reason').style.display='none';
  fetch('/api/tree?id='+encodeURIComponent(id)).then(r=>r.json()).then(t=>{
    const back=t.back&&t.back.length?'<div>'+t.back.map(x=>x.id+':'+x.title).join(' > ')+'</div>':'';
    const fwd=t.forward?'<ul>'+nodeHtml(t.forward)+'</ul>':'';
    document.getElementById('tree').innerHTML=back+fwd;});}
function decide(decision,reason){
  fetch('/api/decide',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({intent:curId,decision:decision,reason:reason})})
    .then(()=>{document.getElementById('decide').style.display='none';loadIntents();});}
document.body.addEventListener('click',e=>{
  const el=e.target.closest('[data-id]');
  if(el){e.preventDefault();load(el.getAttribute('data-id'));}});
document.getElementById('yes').onclick=()=>decide('yes','');
document.getElementById('no').onclick=()=>{document.getElementById('reason').style.display='inline';};
document.getElementById('send').onclick=()=>decide('no',document.getElementById('reasonInput').value);
loadIntents();
</script>
</body></html>"""
