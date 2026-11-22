import React, {useEffect,useState} from 'react'
import {ApiError} from '../services/api'
import {Notice, LoadingState, EmptyState, Button, Badge} from '../components/ui'
export function ErrorNotice({error, onRetry}) {
  if (!error) return null
  return <Notice tone="danger" title={error.status === 403 ? 'Access restricted or session expired' : 'Request unavailable'}>{error.message}{onRetry && <div className="action-line"><Button variant="secondary" onClick={onRetry}>Try again</Button></div>}</Notice>
}
export function useLoad(loader, deps=[], {pollMs=0}={}) {
  const [state,setState] = useState({data:null,loading:true,error:null,updated:null})
  const [revision,setRevision] = useState(0)
  const refresh = () => setRevision(n=>n+1)
  useEffect(()=>{
    let active = true
    const load=async()=>{
      try { const data=await loader(); if(active)setState({data,loading:false,error:null,updated:new Date()}) }
      catch(error) {if(active)setState(s=>({...s,error,loading:false}))}
    }
    load()
    const timer = pollMs ? setInterval(()=>{if(document.visibilityState==='visible')load()},pollMs) : null
    return ()=>{active=false;if(timer)clearInterval(timer)}
  // Loader is intentionally supplied as a stable property-based function by the calling page.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps,revision,pollMs])
  return {...state,refresh}
}
export function QueryView({loading,error,children,retry,empty=false,emptyMessage='No records found.'}) {
  if (loading) return <LoadingState label="Loading from local server…"/>
  if (error && !children) return <ErrorNotice error={error} onRetry={retry}/>
  if (empty) return <><ErrorNotice error={error} onRetry={retry}/><EmptyState title={emptyMessage}/></>
  return <><ErrorNotice error={error} onRetry={retry}/>{children}</>
}
export function StateBadge({status}){const value=String(status||'UNKNOWN').toUpperCase();return <Badge tone={value==='OPEN'||value==='HEALTHY'||value==='RECORDED'?'success':value==='UNAVAILABLE'?'danger':value==='DRAFT'?'warning':'neutral'}>{value}</Badge>}
export function RecordedCount({count}){return <strong className="numeric-value">{typeof count==='number'?count:'—'}</strong>}
export function useAction(){const [busy,setBusy]=useState(false),[error,setError]=useState(null),[success,setSuccess]=useState('');const run=async (fn)=>{if(busy)return;setBusy(true);setError(null);setSuccess('');try{return await fn()}catch(e){setError(e);return null}finally{setBusy(false)}};return {busy,error,success,setSuccess,run,setError}}
export function writeError(error){if(error instanceof ApiError)return error.message;return 'The operation could not be completed.'}
