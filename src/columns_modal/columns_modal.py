from modal_timeline.modal_timeline import modal_timeline

_HTML = """
<div id="modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.4)"
onclick="if(event.target.id==='modal')closeModal()">
<div style="background:#fff;max-width:640px;margin:5vh auto;padding:20px;
border-radius:8px"><button onclick="closeModal()">Close</button>
<div id="modalDetails"></div><div id="modalDecision"></div>
<input id="modalReason" type="text" placeholder="why" style="display:none;width:100%">
<button id="modalRelease" style="display:none" onclick="modalRelease()">Release</button>
<button id="modalYes" style="display:none" onclick="modalDecide('yes')">Yes</button>
<button id="modalNo" style="display:none" onclick="modalNoClick()">No</button>
</div></div><script>function g(id){return document.getElementById(id);}
function closeModal(){g('modal').style.display='none';}window.currentItemId=null;
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal();});
function row(l,v){return '<div><strong>'+l+':</strong> '+(v==null?'':v)+'</div>';}
var REL='release this Intent to the Architect so it can be broken into Stories';
var VAL='validate. Yes closes it, No reopens it with your reason';
function decisionFor(k,t){
  if(k==='intent'&&t==='waiting')return {text:REL,mode:'release'};
  if((k==='intent'||k==='proposal')&&t==='checking')return {text:VAL,mode:'yesno'};
  return {text:null,mode:'none'};}function fillDetails(d){
  var html=row('id',d.id)+row('kind',d.kind)+row('title',d.title)+row('owner',d.owner);
  html+=row('state',d.state)+row('parent',d.parent);var s=d.sheet==null?'':d.sheet;
  html+='<pre style="max-height:50vh;overflow:auto;white-space:pre-wrap">'+s+'</pre>';
  g('modalDetails').innerHTML=html;var dec=decisionFor(d.kind,d.state);
  var t=dec.text==null?'No decision for the Board on this item':dec.text;
  g('modalDecision').innerHTML='<strong>Decision:</strong> '+t;
  g('modalRelease').style.display=dec.mode==='release'?'':'none';
  var yn=dec.mode==='yesno'?'':'none';
  g('modalYes').style.display=yn; g('modalNo').style.display=yn;
  g('modalReason').style.display='none'; g('modalReason').value='';
  g('modal').style.display='block';}window.openItem=function(id){
  window.currentItemId=id;
  fetch('/api/item?id='+encodeURIComponent(id)).then(r=>r.json()).then(d=>{fillDetails(d);loadTimeline(id);});};
function modalNoClick(){
var r=g('modalReason');if(r.style.display==='none'){r.style.display='';r.focus();return}
  if(r.value!==''){modalDecide('no');}}function post(url,body){
  var h={'Content-Type':'application/json'};
  fetch(url,{method:'POST',headers:h,body:JSON.stringify(body)})
    .then(()=>{closeModal(); location.reload();});}function modalDecide(decision){
  var reason=decision==='no'?g('modalReason').value:'';
  post('/api/decide',{intent:window.currentItemId,decision:decision,reason:reason});}
function modalRelease(){post('/api/release',{id:window.currentItemId});}
</script>"""


def columns_modal() -> str:
    """The board modal: item details, the decision line, Release and Yes/No."""
    return modal_timeline() + _HTML
