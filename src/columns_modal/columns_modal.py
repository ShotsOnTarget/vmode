def columns_modal() -> str:
    return """
<div id="modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);"
onclick="if(event.target.id==='modal')closeModal()">
<div style="background:#fff;max-width:640px;margin:5vh auto;padding:20px;
border-radius:8px;">
<button onclick="closeModal()">Close</button>
<div id="modalDetails"></div>
<input id="modalReason" type="text" placeholder="reason"
style="display:none;width:100%;">
<button id="modalYes" style="display:none;" onclick="modalDecide('yes')">Yes</button>
<button id="modalNo" style="display:none;" onclick="modalNoClick()">No</button>
</div>
</div>
<script>
window.currentItemId = null;
function g(id){return document.getElementById(id);}
function closeModal(){g('modal').style.display = 'none';}
document.addEventListener('keydown', function(e){if(e.key==='Escape')closeModal();});
function row(l, v){return '<div><strong>'+l+':</strong> '+(v==null?'':v)+'</div>';}
function fillDetails(d){
  var html = row('id', d.id)+row('kind', d.kind)+row('title', d.title);
  html += row('owner', d.owner)+row('state', d.state)+row('parent', d.parent);
  var s = d.sheet == null ? '' : d.sheet;
  html += '<pre style="max-height:50vh;overflow:auto;white-space:pre-wrap">'+s+'</pre>';
  g('modalDetails').innerHTML = html;
  var k=d.kind,t=d.state,disp=(k==='intent'||k==='proposal')&&t==='checking'?'':'none';
  g('modalYes').style.display = disp; g('modalNo').style.display = disp;
  g('modalReason').style.display = 'none'; g('modalReason').value = '';
  g('modal').style.display = 'block';
}
window.openItem = function(id){
  window.currentItemId = id;
  fetch('/api/item?id='+encodeURIComponent(id))
    .then(function(r){return r.json();}).then(fillDetails);
};
function modalNoClick(){
  var r = g('modalReason');
  if(r.style.display === 'none'){r.style.display=''; r.focus(); return;}
  if(r.value !== ''){modalDecide('no');}
}
function modalDecide(decision){
  var reason = decision === 'no' ? g('modalReason').value : '';
  var p = {intent:window.currentItemId, decision:decision, reason:reason};
  var h = {'Content-Type':'application/json'};
  fetch('/api/decide', {method:'POST', headers:h, body:JSON.stringify(p)})
    .then(function(){closeModal(); location.reload();});
}
</script>
"""
