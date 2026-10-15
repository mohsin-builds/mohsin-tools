// Dependency-free simulation tests for validation, encoder selection, bounds,
// and the target-byte search. These DO NOT replace real browser integration tests.
import assert from 'node:assert/strict';
import {loadBitmap,compressToBytes,convert,safeFileName,formatBytes} from '../assets/toolkit.js';
let closed=0;
globalThis.createImageBitmap=async file=>{if(file.broken)throw Error('decode');return {width:file.width||1000,height:file.height||800,close(){closed++}}};
globalThis.document={createElement(tag){assert.equal(tag,'canvas');return {
 width:0,height:0,getContext(){return {fillStyle:'#fff',fillRect(){},drawImage(){},set imageSmoothingEnabled(v){},set imageSmoothingQuality(v){}}},
 toBlob(callback,mime,quality){const area=this.width*this.height;const factor=mime==='image/png'?.7:(quality??.92)*.6+.04;callback({size:Math.round(area*factor),type:mime})}
}}};
const file={name:'my photo.HEIC.png',type:'image/png',size:900000,width:1000,height:800};
assert.equal(safeFileName(file.name),'my-photo.HEIC');
assert.equal(formatBytes(1536),'1.5 KB');
assert.equal((await convert(file,{mime:'image/png',width:200,height:230})).blob.type,'image/png');
const compressed=await compressToBytes(file,{targetBytes:50000,mime:'image/jpeg',allowShrink:true});
assert.ok(compressed.metTarget);assert.ok(compressed.blob.size<=50000);assert.ok(compressed.width<1000);
const failed=await compressToBytes(file,{targetBytes:2048,mime:'image/jpeg',width:200,height:230,allowShrink:false});
assert.equal(failed.metTarget,false);
await assert.rejects(loadBitmap({...file,type:'image/heic'}),/HEIC/);
await assert.rejects(loadBitmap({...file,size:26*1024*1024}),/25 MB/);
await assert.rejects(compressToBytes(file,{targetBytes:1,mime:'image/jpeg'}),/at least/);
assert.ok(closed>=3);
console.log('PASS: simulated Canvas encoder, compression ceilings, dimension choice, failure warnings, unsupported types, validation');