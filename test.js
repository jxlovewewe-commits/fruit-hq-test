const fs=require('fs');const html=fs.readFileSync('index.html','utf8');
const core=html.match(/<script id="core">([\s\S]*?)<\/script>/)[1];
const m={exports:{}};new Function('module',core)(m);const C=m.exports;const assert=require('assert');
let S=C.sample();
assert.equal(S.items.length,10);
assert.equal(C.item(S,'pe2').stock,17);assert.equal(C.item(S,'br4').stock,18);
assert.equal(S.orders.map(o=>o.status).join(),'출고완료,승인,접수');
// 주문→승인→출고→정산
const o=C.placeOrder(S,'d3',{pe1:2,br5:1},'2026-11-16');
assert.equal(C.orderTotal(o),2*35500+69900);
assert.throws(()=>C.createShipment(S,[o.id]),/승인/);
C.approveOrder(S,o.id);assert.throws(()=>C.cancelOrder(S,o.id,true),/접수/);
C.createShipment(S,[o.id],'2026-11-16');
assert.equal(o.status,'출고완료');assert.equal(C.item(S,'pe1').stock,18);assert.equal(C.item(S,'br5').stock,19);
let r=C.settlement(S,{dealerId:'d3'});assert.equal(r.total,140900);assert.equal(r.unpaid,140900);
C.toggleSettled(S,o.id);r=C.settlement(S,{dealerId:'d3'});assert.equal(r.unpaid,0);
assert.equal(C.settlement(S,{from:'2026-11-16',to:'2026-11-16'}).rows.length,1);
// 재고 부족 차단
const big=C.placeOrder(S,'d1',{pe3:999});C.approveOrder(S,big.id);
const before=C.item(S,'pe3').stock;
assert.throws(()=>C.createShipment(S,[big.id]),/재고가 부족/);assert.equal(C.item(S,'pe3').stock,before);assert.equal(big.status,'승인');
// 대리점 취소
const c=C.placeOrder(S,'d2',{br1:1});C.cancelOrder(S,c.id,true);assert.equal(c.status,'취소');
// 저장/불러오기
const store={d:{},getItem(k){return this.d[k]??null},setItem(k,v){this.d[k]=v}};
C.save(store,S);assert.deepEqual(C.load(store),JSON.parse(JSON.stringify(S)));
console.log('모든 로직 테스트 통과');
