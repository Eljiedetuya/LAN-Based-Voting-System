import React,{useEffect,useState,useRef} from 'react'
import {api} from '../services/api'
import {Badge,Button,Panel,PageHeader,Notice,LoadingState,EmptyState,Progress} from '../components/ui'
import {QueryView,ErrorNotice,useLoad,StateBadge} from './common'
import {CandidatePhoto} from '../components/CandidatePhoto'
const own = (id,path) => `/student/elections/${id}/${path}`
export function StudentHome({navigate}){
  const state=useLoad(api.activeElections,[])
  return <><PageHeader eyebrow="STUDENT PORTAL" title="Available elections" description="Only your eligible, currently open elections are shown."/><QueryView {...state} retry={state.refresh} empty={Array.isArray(state.data)&&!state.data.length} emptyMessage="No active elections are available to your account.">{Array.isArray(state.data)&&state.data.map(e=><Panel key={e.id} title={e.title} subtitle={e.description}><div className="detail-row"><span>Election</span><StateBadge status={e.status}/></div><div className="action-line"><Button onClick={()=>navigate(own(e.id,'candidates'))}>View candidates</Button><Button variant="secondary" onClick={()=>navigate(own(e.id,'status'))}>My voting status</Button></div></Panel>)}</QueryView></>
}
function useCandidateGroups(electionId){
 const state=useLoad(()=>api.candidates(electionId),[electionId])
 return state
}
export function StudentCandidates({electionId,navigate}){
 const state=useCandidateGroups(electionId)
 const groups=state.data?.positions||[], people=state.data?.candidates||[]
 return <><PageHeader eyebrow="STUDENT / CANDIDATES" title="Candidate profiles" description="Review real election candidates retrieved from the local server."/><QueryView {...state} retry={state.refresh} empty={Boolean(state.data&&!groups.length)} emptyMessage="No positions configured.">{groups.map(p=><Panel key={p.id} title={p.name}><div className="candidate-grid">{people.filter(c=>c.position_id===p.id).map(c=><article key={c.id} className="candidate-card"><CandidatePhoto src={c.photo_path} name={c.name} size="large"/><div className="candidate-info"><h3>{c.name}</h3><p>{c.platform||'No platform provided.'}</p>{c.biography&&<p>{c.biography}</p>}</div></article>)}</div></Panel>)}<div className="sticky-actions"><Button onClick={()=>navigate(own(electionId,'ballot'))}>Start ballot</Button></div></QueryView></>
}
export function StudentStatus({electionId,navigate}){
 const state=useLoad(()=>api.myStatus(electionId),[electionId])
 return <><PageHeader eyebrow="STUDENT / STATUS" title="Your election status" description="Only your own eligibility and recorded participation are shown."/><QueryView {...state} retry={state.refresh}>{state.data&&<Panel title="Server-confirmed participation"><div className="detail-row"><span>Election</span><StateBadge status={state.data.election_status}/></div><div className="detail-row"><span>Eligibility</span><Badge tone={state.data.eligible?'success':'neutral'}>{state.data.eligible?'Eligible':'Not eligible'}</Badge></div><div className="detail-row"><span>Participation</span><Badge tone={state.data.has_voted?'success':'neutral'}>{state.data.has_voted?'Recorded':'Not recorded'}</Badge></div><div className="action-line"><Button variant="secondary" onClick={state.refresh}>Check again</Button>{state.data.eligible&&!state.data.has_voted&&state.data.election_status==='OPEN'&&<Button onClick={()=>navigate(own(electionId,'ballot'))}>Go to ballot</Button>}</div></Panel>}</QueryView></>
}
export function StudentBallot({electionId,navigate,ballotDraft,setBallotDraft}){
 const state=useCandidateGroups(electionId)
 const status=useLoad(()=>api.myStatus(electionId),[electionId])
 const positions=state.data?.positions||[], candidates=state.data?.candidates||[]
 const selections=ballotDraft?.electionId===electionId?ballotDraft.choices:{}
 const selected=positions.filter(p=>Boolean(selections[p.id])).length
 const allowed=status.data?.eligible&&!status.data?.has_voted&&status.data?.election_status==='OPEN'
 const change=(p,c)=>setBallotDraft({electionId,choices:{...selections,[p]:c}})
 return <><PageHeader eyebrow="STUDENT / BALLOT" title="Select your candidates" description="Choose one candidate for every position. You must review the complete ballot before submission."/>
 <QueryView loading={state.loading||status.loading} error={state.error||status.error} retry={()=>{state.refresh();status.refresh()}}>{state.data&&status.data&&(!allowed?<Notice tone="warning" title="Ballot not available">You are not eligible, this election is closed, or a ballot has already been recorded. Check your voting status.</Notice>:<><Panel title="Ballot progress" subtitle={`${selected} of ${positions.length} positions selected`}><Progress value={selected} max={Math.max(1,positions.length)}/></Panel>{positions.map((p,i)=><section className="panel ballot-position" key={p.id}><div className="position-label">POSITION {i+1} OF {positions.length}</div><fieldset><legend>{p.name}</legend><p className="muted small">Select one candidate.</p><div className="candidate-grid">{candidates.filter(c=>c.position_id===p.id).map(c=><label key={c.id} className={`candidate-card candidate-pick ${selections[p.id]===c.id?'candidate-selected':''}`}><CandidatePhoto src={c.photo_path} name={c.name}/><div className="candidate-info"><h3>{c.name}</h3><p>{c.platform||'No platform provided.'}</p></div><span className="candidate-choice"><input type="radio" name={`ballot-position-${p.id}`} checked={selections[p.id]===c.id} onChange={()=>change(p.id,c.id)} aria-label={`Select ${c.name} for ${p.name}`}/></span></label>)}</div></fieldset></section>)}<div className="sticky-actions"><Button disabled={!positions.length||selected!==positions.length} onClick={()=>navigate(own(electionId,'review'))}>Review ballot</Button></div></>)}</QueryView></>
}
export function StudentReview({electionId,navigate,ballotDraft,clearDraft}){
 const state=useCandidateGroups(electionId)
 const status=useLoad(()=>api.myStatus(electionId),[electionId])
 const [pending,setPending]=useState(false),[error,setError]=useState(null),[uncertain,setUncertain]=useState(false)
 const inFlight=useRef(false)
 const draft=ballotDraft?.electionId===electionId?ballotDraft.choices:{}
 const positions=state.data?.positions||[], people=state.data?.candidates||[]
 const complete=positions.length>0&&positions.every(p=>people.some(c=>c.id===draft[p.id]&&c.position_id===p.id))
 const canSubmit=complete&&status.data?.eligible&&!status.data?.has_voted&&status.data?.election_status==='OPEN'&&!uncertain
 const submit=async()=>{
   if(inFlight.current||!canSubmit)return
   inFlight.current=true;setPending(true);setError(null)
   try {
     const current=await api.myStatus(electionId)
     if(!current.eligible||current.has_voted||current.election_status!=='OPEN')throw new Error('Eligibility or election state changed. Check your voting status.')
     const response=await api.submitVote(electionId,positions.map(p=>({position_id:p.id,candidate_id:draft[p.id]})))
     if(response?.status!=='recorded'||response?.has_voted!==true)throw new Error('The response did not confirm that the ballot was recorded. Check your status.')
     clearDraft();navigate(own(electionId,'confirmation'))
   }catch(e){setError(e);setUncertain(true)}finally{inFlight.current=false;setPending(false)}
 }
 return <><PageHeader eyebrow="STUDENT / FINAL REVIEW" title="Review your ballot" description="Once accepted by the server, your vote cannot be changed."/><QueryView loading={state.loading||status.loading} error={state.error||status.error} retry={()=>{state.refresh();status.refresh()}}>{state.data&&status.data&&<><Panel title="Selected candidates">{!complete?<Notice tone="warning" title="Incomplete ballot">Return to the ballot and select one candidate for every position.</Notice>:<div className="review-list">{positions.map(p=>{const candidate=people.find(c=>c.id===draft[p.id]);return <div className="review-item" key={p.id}><div className="review-candidate"><CandidatePhoto src={candidate?.photo_path} name={candidate?.name}/><div><span className="muted small">{p.name}</span><h3>{candidate?.name}</h3></div></div><Button variant="secondary" onClick={()=>navigate(own(electionId,'ballot'))}>Edit</Button></div>})}</div>}</Panel><Notice tone="warning" title="Final submission">Review every selection carefully. Once recorded, your ballot is final.</Notice>{uncertain&&<Notice tone="warning" title="Submission outcome may be unknown">Do not submit again until you have checked your recorded status. If the server shows no vote, return to the ballot and review your choices.</Notice>}<ErrorNotice error={error}/><div className="sticky-actions"><Button variant="secondary" onClick={()=>navigate(own(electionId,'ballot'))}>Edit ballot</Button><Button disabled={!canSubmit||pending} onClick={submit}>{pending?'Submitting vote…':'Submit final vote'}</Button><Button variant="secondary" onClick={()=>navigate(own(electionId,'status'))}>Check voting status</Button></div></>}</QueryView></>
}
export function StudentConfirmation({electionId,navigate}){
 const state=useLoad(()=>api.myStatus(electionId),[electionId])
 return <><PageHeader eyebrow="STUDENT / CONFIRMATION" title="Voting confirmation"/><QueryView {...state} retry={state.refresh}>{state.data&&(state.data.has_voted?<Notice tone="success" title="Your vote has been recorded">The server confirms your participation in this election. Your candidate choices are not shown or stored in this confirmation.</Notice>:<Notice tone="warning" title="No accepted vote confirmed">The server currently reports no accepted ballot for your account. Check voting status before making any further attempt.</Notice>)}<div className="action-line"><Button onClick={()=>navigate(own(electionId,'status'))}>View voting status</Button></div></QueryView></>
}
