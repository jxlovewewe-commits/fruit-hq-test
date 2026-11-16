# 브라우저 흐름 테스트: python3 uitest.py → /tmp/uitest.html 생성 후 headless chrome으로 실행
import subprocess,re,sys
s=open('index.html').read()
t=r'''<script>
window.confirm=function(){window._c=(window._c||0)+1;return true};window.prompt=function(){};var log=[];function ok(c,m){log.push((c?'OK ':'FAIL ')+m);}
function done(){document.body.setAttribute('data-log',log.join(' | '));}
function click(sel){var e=document.querySelector(sel);if(!e)throw new Error('없음: '+sel);e.click();}
function go(h){location.hash=h;render();}
try{
if(view==='dealer'){
  localStorage.removeItem(KEY);S=load(localStorage);render();
  ok($('me').value==='d3'&&$('brandsub').textContent==='수원점','?d=d3 대리점 미리 선택');
  var bad=HQ_ACTIONS.filter(function(a){return document.querySelector('[data-a="'+a+'"]');});
  ok(!bad.length,'대리점 DOM에 본부 기능 버튼 없음 '+bad.join(','));
  ok(!document.querySelector('#file,#itemsfile,.nav,#newdealer,[id^="q-"],[id^="it-"],[id^="f-"]'),'본부 입력·탭바 없음');
  var links=[].filter.call(document.querySelectorAll('a[href]'),function(a){return a.getAttribute('href').charAt(0)!=='#';});ok(!links.length,'외부·본부 링크 없음');
  ['mine','settle','order'].forEach(function(p){go(p);var tx=document.body.innerText;ok(!/본부 관리|재고 조정|품목 관리|데이터 초기화|출고 지시|정산완료로 표시|예시 데이터/.test(tx)&&!HQ_ACTIONS.some(function(a){return document.querySelector('[data-a="'+a+'"]');}),'#'+p+' 본부 문구·기능 없음');});
  ok(document.querySelector('[data-ic="peru-kent-sil4"]').innerText.replace(/\s+/g,' ').indexOf('페루 켄트 애플망고 실속 4과 (1.83kg) 35,500원')>=0,'품목 카드 표시');
  ok($('orderbtn').disabled,'수량 0이면 주문 버튼 비활성');
  click('[data-step="1"][data-id="peru-kent-sil4"]');click('[data-step="1"][data-id="peru-kent-sil4"]');click('[data-step="1"][data-id="brazil-keitt-gift9"]');click('[data-step="-1"][data-id="brazil-keitt-gift9"]');
  ok($('ototal').textContent==='71,000원'&&$('ocount').textContent==='선택 2개','스테퍼·합계 '+$('ototal').textContent);
  click('#orderbtn');var o=S.orders[S.orders.length-1];ok(o.status==='접수'&&o.dealerName==='수원점'&&orderTotal(o)===71000,'주문 접수 #'+o.no);
  ok(JSON.parse(localStorage.getItem(KEY)).orders.length===4&&$('ototal').textContent==='0원','localStorage 저장·장바구니 비움');
  go('mine');click('[data-a="dcancel"][data-id="'+o.id+'"]');ok(o.status==='취소','접수 주문 취소');
  ok([].every.call(document.querySelectorAll('[data-a="dcancel"]'),function(b){return order(S,b.dataset.id).status==='접수';})&&!document.querySelector('[data-a="dcancel"][data-id="'+o.id+'"]'),'접수 주문에만 취소 버튼');
  // 대리점 화면에서 본부 기능 강제 호출 무시
  var fake=document.createElement('button');fake.dataset.a='reset';document.body.appendChild(fake);var n=S.orders.length;fake.click();fake.remove();ok(S.orders.length===n,'본부 동작 강제 호출 무시');
  done();
}else{
  localStorage.removeItem(KEY);S=load(localStorage);render();
  ok(!document.querySelector('.seg a[href*="view"],a[href*="view=dealer"]')&&!document.querySelector('.oq,[data-step],#orderbtn'),'본부에 대리점 화면·전환 탭 없음');
  ok(document.querySelectorAll('.nav a').length===6&&document.body.innerText.indexOf('예시 데이터')>=0,'하단 탭 6개·예시 데이터 표시');
  var kp=[].map.call(document.querySelectorAll('.kpi .v'),function(e){return e.textContent;}).join('/');ok(kp==='1건/1건/0개/244,500원','요약 카드 '+kp);
  var o=placeOrder(S,'d3',{'peru-kent-sil4':2},today());save(localStorage,S);
  go('orders');click('[data-a="approve"][data-id="'+o.id+'"]');ok(o.status==='승인','승인');
  go('ship');document.querySelector('.shp[value="'+o.id+'"]').checked=true;click('[data-a=ship]');
  ok(o.status==='출고완료'&&stockOf(S,'peru-kent-sil4')===18,'출고·재고 차감');
  var big=placeOrder(S,'d1',{'peru-kent-sil8':999});approveOrder(S,big.id);render();document.querySelector('.shp[value="'+big.id+'"]').checked=true;click('[data-a=ship]');
  ok(big.status==='승인'&&/재고가 부족/.test($('toast').textContent),'재고 부족 차단: '+$('toast').textContent.slice(0,30));
  go('settle');click('[data-a="settle"][data-id="'+o.id+'"]');ok(o.settled,'정산완료 토글');
  go('items');$('it-name').value='골드망고';$('it-country').value='태국';$('it-variety').value='<img src=x onerror=alert(1)>';$('it-type').value='선물';$('it-count').value=4;$('it-kg').value=1.6;$('it-cost').value=20000;$('it-price').value=30000;$('it-id').value='thai-gold-gift4';
  click('[data-a=saveitem]');ok(item(S,'thai-gold-gift4')&&!document.querySelector('#app img'),'품목 추가·이스케이프');
  click('[data-a=edititem][data-id="thai-gold-gift4"]');$('it-price').value=31000;click('[data-a=saveitem]');ok(item(S,'thai-gold-gift4').price===31000,'품목 수정');
  window._c=0;click('[data-a=delitem][data-id="peru-kent-sil4"]');ok(window._c===1&&!item(S,'peru-kent-sil4')&&orderTotal(o)===71000,'주문 있는 품목 삭제 확인창·기존 주문 유지');
  go('settings');$('newdealer').value='<b>일산점</b>';click('[data-a=adddealer]');ok(!document.querySelector('#app .li b b')&&document.querySelectorAll('[data-a=copylink][data-id]').length===4,'대리점 추가·이스케이프·링크 복사 버튼');
  ok(dealerLink('d2').slice(-17)==='?view=dealer&d=d2','대리점 링크 '+dealerLink('d2'));
  go('items');S.items.forEach(function(it){if(it.id==='peru-kent-sil6')it.price=1;});click('[data-a=calcitems]');
  setTimeout(function(){ok(/불러왔/.test($('toast').textContent)&&item(S,'peru-kent-sil4')&&item(S,'peru-kent-sil6').price===48500,'계산기 품목 불러오기: '+$('toast').textContent);done();},3000);
}
}catch(e){log.push('ERROR '+e.message);done();}
</script></body>'''
i=s.rindex('</body>');open('/tmp/uitest.html','w').write(s[:i]+t+s[i+7:])
fail=0
for q in ['', '?view=dealer&d=d3']:
    out=subprocess.run(['google-chrome','--headless','--no-sandbox','--disable-gpu','--virtual-time-budget=8000','--dump-dom','file:///tmp/uitest.html'+q],capture_output=True,text=True,timeout=60).stdout
    m=re.search(r'data-log="([^"]*)"',out);r=m.group(1) if m else 'NO RESULT'
    print('== '+('대리점' if q else '본부'));print(r.replace(' | ','\n'))
    if 'FAIL' in r or 'ERROR' in r or not m: fail=1
sys.exit(fail)
