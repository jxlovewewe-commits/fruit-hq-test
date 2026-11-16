const fs=require('fs');const html=fs.readFileSync(__dirname+'/index.html','utf8');
const core=html.match(/<script id="core">([\s\S]*?)<\/script>/)[1];
const m={exports:{}};new Function('module',core)(m);const C=m.exports;const assert=require('assert');
const D=C.defaultItems();
assert.equal(D.length,10);
assert.deepEqual(D[0],{id:'peru-kent-sil4',name:'애플망고',country:'페루',variety:'켄트',type:'실속',kg:1.83,count:4,cost:26000,price:35500});
assert.deepEqual(D.map(i=>i.kg),[1.83,2.75,3.67,2.75,4.13,2,3,4,3,4.5]);
assert.deepEqual(D.map(i=>i.cost),[26000,39000,52000,39000,58500,23000,34500,46000,34500,51750]);
assert.deepEqual(D.map(i=>i.price),[35500,48500,61500,54000,76500,32500,44000,55500,49500,69900]);
assert.equal(C.itemLabel(D[3]),'페루 켄트 애플망고 · 선물 6과 (2.75kg)');
let S=C.sample();
assert.equal(C.stockOf(S,'peru-kent-sil6'),17);assert.equal(C.stockOf(S,'brazil-keitt-gift6'),18);
assert.equal(S.orders.map(o=>o.status).join(),'출고완료,승인,접수');
// 주문→승인→출고→정산
const o=C.placeOrder(S,'d3',{'peru-kent-sil4':2,'brazil-keitt-gift9':1},'2026-11-16');
assert.equal(C.orderTotal(o),2*35500+69900);
assert.throws(()=>C.createShipment(S,[o.id]),/승인/);
C.approveOrder(S,o.id);assert.throws(()=>C.cancelOrder(S,o.id,true),/접수/);
C.createShipment(S,[o.id],'2026-11-16');
assert.equal(o.status,'출고완료');assert.equal(C.stockOf(S,'peru-kent-sil4'),18);
let r=C.settlement(S,{dealerId:'d3'});assert.equal(r.total,140900);
C.toggleSettled(S,o.id);assert.equal(C.settlement(S,{dealerId:'d3'}).unpaid,0);
// 재고 부족 차단
const big=C.placeOrder(S,'d1',{'peru-kent-sil8':999});C.approveOrder(S,big.id);
assert.throws(()=>C.createShipment(S,[big.id]),/재고가 부족/);assert.equal(C.stockOf(S,'peru-kent-sil8'),20);
// 품목 수정/삭제 후에도 기존 주문 유지
C.upsertItem(S,Object.assign({},C.item(S,'peru-kent-sil4'),{price:40000}),false);
assert.equal(C.orderTotal(o),140900);
assert.equal(C.itemOrderCount(S,'peru-kent-sil4'),1);
C.removeItem(S,'peru-kent-sil4');assert.equal(C.orderTotal(o),140900);assert.equal(o.lines[0].label,'페루 켄트 애플망고 · 실속 4과 (1.83kg)');
assert.throws(()=>C.upsertItem(S,{id:'x',name:'골드망고',country:'태국',variety:'남독마이',type:'세트',kg:1,count:4,cost:1,price:1},true),/실속 또는 선물/);
// 품목 파일 병합
const f=C.itemsFile(S);assert.equal(f.schema,'fruit-items/1');
const r2=C.mergeItems(S,{schema:'fruit-items/1',updated:'x',items:[{id:'peru-kent-sil6',name:'애플망고',country:'페루',variety:'켄트',type:'실속',kg:2.75,count:6,cost:39000,price:49000},{id:'thai-gold-sil4',name:'골드망고',country:'태국',variety:'남독마이',type:'실속',kg:1.6,count:4,cost:20000,price:30000}]});
assert.deepEqual(r2,{added:1,updated:1});assert.equal(C.item(S,'peru-kent-sil6').price,49000);assert.equal(C.stockOf(S,'peru-kent-sil6'),17);assert.equal(C.stockOf(S,'thai-gold-sil4'),0);
assert.throws(()=>C.mergeItems(S,{items:[]}),/fruit-items\/1/);
// 저장/불러오기 + v1 마이그레이션
const mk=()=>({d:{},getItem(k){return this.d[k]??null},setItem(k,v){this.d[k]=v}});
let st=mk();C.save(st,S);assert.deepEqual(C.load(st),JSON.parse(JSON.stringify(S)));
st=mk();st.setItem('fruitHqTest.v1',JSON.stringify({v:1,items:[{id:'pe1',origin:'페루 켄트',name:'실속 4과',price:35500,stock:7}],dealers:[{id:'d1',name:'강남점'}],orders:[{id:'o1',no:1,dealerId:'d1',dealerName:'강남점',lines:[{itemId:'pe1',label:'페루 켄트 실속 4과',qty:1,price:35500}],status:'승인'}],shipments:[],seq:{order:1,ship:0,dealer:1}}));
const M=C.load(st);assert.equal(M.v,2);assert.equal(C.stockOf(M,'peru-kent-sil4'),7);assert.equal(M.orders[0].lines[0].itemId,'peru-kent-sil4');
st=mk();st.setItem(C.KEY,'{"v":7}');assert.equal(C.load(st).items.length,10);
console.log('모든 로직 테스트 통과');
