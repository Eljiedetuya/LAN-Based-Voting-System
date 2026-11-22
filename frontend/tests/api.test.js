import test from 'node:test'
import assert from 'node:assert/strict'
import {api, request, ApiError} from '../src/services/api.js'

globalThis.document = {cookie:'csrftoken=localtest'}
globalThis.window = {dispatchEvent:()=>{}}
globalThis.Event = class {constructor(name){this.type=name}}
const json=(data,status=200)=>({ok:status>=200&&status<300,status, text:async()=>JSON.stringify(data)})
test('GET requests are relative, same-origin, and omit CSRF header',async()=>{
  let input,options;globalThis.fetch=async(p,o)=>{input=p;options=o;return json({status:'ok'})}
  assert.deepEqual(await api.publicHealth(),{status:'ok'});
  assert.equal(input,'/api/health/');assert.equal(options.credentials,'same-origin');assert.equal('X-CSRFToken' in options.headers,false)
})
test('ballot submission uses CSRF, sends selections and returns no choices',async()=>{
 let input,options;globalThis.fetch=async(p,o)=>{input=p;options=o;return json({status:'recorded',election_id:4,has_voted:true},201)}
 const result=await api.submitVote(4,[{position_id:5,candidate_id:7}])
 assert.equal(input,'/api/elections/4/submit-vote/');assert.equal(options.headers['X-CSRFToken'],'localtest');assert.equal(JSON.parse(options.body).selections[0].candidate_id,7);assert.equal(result.has_voted,true)
})
test('duplicate vote 409 is not mistaken for success',async()=>{
 globalThis.fetch=async()=>json({error:{code:'vote_conflict',detail:'Vote already recorded.'}},409)
 await assert.rejects(api.submitVote(1,[]),e=>e instanceof ApiError&&e.status===409&&e.code==='vote_conflict')
})
test('failed network request has unknown vote outcome',async()=>{
 globalThis.fetch=async()=>{throw new Error('offline')}
 await assert.rejects(api.submitVote(1,[]),e=>e instanceof ApiError&&e.code==='network_unavailable'&&e.message.includes('still have been recorded'))
})
test('missing CSRF token blocks write before fetch',async()=>{
 document.cookie='';let called=false;globalThis.fetch=async()=>{called=true;return json({})}
 await assert.rejects(api.submitVote(1,[]),e=>e.code==='csrf_missing');assert.equal(called,false)
 document.cookie='csrftoken=localtest'
})
