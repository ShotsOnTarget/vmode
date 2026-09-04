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
  const tb=document.querySelector('#intents tbody');tb.innerHTML='';
  list.forEach(it=>{const tr=document.createElement('tr');tr.className='row';
    tr.innerHTML=`<td>${it.id}</td><td>${it.title}</td><td>${it.state}</td><td>${it.care}</td><td>${it.stories_done}/${it.stories_total}</td>`;
    tr.onclick=()=>selectIntent(it.id);tb.appendChild(tr);});});}
function renderList(items){const ul=document.createElement('ul');
  items.forEach(it=>{const li=document.createElement('li');const a=document.createElement('a');
    a.href='#';a.textContent=it.id+' '+(it.title||'');
    a.onclick=(e)=>{e.preventDefault();selectIntent(it.id);};li.appendChild(a);
    if(it.children&&it.children.length)li.appendChild(renderList(it.children));ul.appendChild(li);});
  return ul;}
function selectIntent(id){curId=id;
  document.getElementById('decide').style.display='block';
  document.getElementById('reason').style.display='none';
  fetch('/api/tree?id='+encodeURIComponent(id)).then(r=>r.json()).then(t=>{
    const div=document.getElementById('tree');div.innerHTML='';
    if(t.back&&t.back.length){const b=document.createElement('div');
      b.textContent=t.back.map(x=>x.id+':'+x.title).join(' > ');div.appendChild(b);}
    div.appendChild(renderList(t.forward||[]));});}
function decide(decision,reason){
  fetch('/api/decide',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({intent:curId,decision:decision,reason:reason})})
    .then(()=>{document.getElementById('decide').style.display='none';loadIntents();});}
document.getElementById('yes').onclick=()=>decide('yes','');
document.getElementById('no').onclick=()=>{document.getElementById('reason').style.display='inline';};
document.getElementById('send').onclick=()=>decide('no',document.getElementById('reasonInput').value);
loadIntents();
</script>
</body></html>"""
