import React,{useEffect,useState} from 'react'
import {api} from './services/api'
import {Badge,Button,Field,Icon,LoadingState,Notice} from './components/ui'
import {ErrorNotice} from './live/common'
import {StudentHome,StudentCandidates,StudentStatus,StudentBallot,StudentReview,StudentConfirmation} from './live/Student'
import {AdminHome,AdminElections,AdminElectionForm,AdminElectionSetup,AdminCandidates,AdminCandidateForm,AdminVoters,AdminVoterForm,AdminStaffAccounts,AdminMonitoring,AdminResults,AdminAudit,AdminHealth,AdminReports,AdminIntegrity,Unsupported} from './live/Admin'
import {MonitorDashboard,MonitorParticipation,MonitorElectionStatus,MonitorHealth,MonitorResults} from './live/Monitor'
import './styles.css'
const HOME={STUDENT:'/student/dashboard',ADMIN:'/admin/dashboard',MONITOR:'/monitor/dashboard'}
const NAV={
 STUDENT:[['/student/dashboard','Elections','calendar']],
 ADMIN:[['/admin/dashboard','Overview','home'],['/admin/elections','Elections','calendar'],['/admin/candidates','Candidates','users'],['/admin/voters','Voters','list'],['/admin/staff','Staff accounts','users'],['/admin/monitoring','Participation','chart'],['/admin/integrity','Integrity checks','server'],['/admin/reports','Reports','list'],['/admin/results','Results','chart'],['/admin/audit','Audit logs','list'],['/admin/system','System health','server']],
 MONITOR:[['/monitor/dashboard','Overview','home'],['/monitor/participation','Participation','chart'],['/monitor/election-status','Election status','calendar'],['/monitor/results','Closed results','chart'],['/monitor/server-health','Server health','server']],
}
const roleForPath=path=>path.startsWith('/student/')?'STUDENT':path.startsWith('/admin/')?'ADMIN':path.startsWith('/monitor/')?'MONITOR':null
function usePath(){const [path,setPath]=useState(window.location.pathname);useEffect(()=>{const cb=()=>setPath(window.location.pathname);window.addEventListener('popstate',cb);return()=>window.removeEventListener('popstate',cb)},[]);const navigate=to=>{if(to===window.location.pathname)return;window.history.pushState(null,'',to);setPath(to);window.scrollTo(0,0)};return [path,navigate]}
function Login({onLogin,loginError,busy}){const [username,setUsername]=useState(''),[password,setPassword]=useState('');return <main className="auth-page"><div className="auth-brand"><span className="logo-square"><Icon name="vote" size={24}/></span><strong>CampusVote</strong></div><form className="auth-card" onSubmit={e=>{e.preventDefault();onLogin(username,password)}}><p className="eyebrow">SCHOOL ELECTION PORTAL</p><h1>Sign in</h1><p className="muted">Enter your assigned account credentials to access the local election system.</p><div className="field"><label htmlFor="username">Student ID or username</label><input id="username" value={username} onChange={e=>setUsername(e.target.value)} autoComplete="username" required/></div><div className="field"><label htmlFor="password">Password</label><input id="password" value={password} onChange={e=>setPassword(e.target.value)} type="password" autoComplete="current-password" required/></div><ErrorNotice error={loginError}/><Button type="submit" disabled={busy}>{busy?'Signing in…':'Sign in'}</Button></form></main>}
function PasswordChange({onSubmit,onLogout,error,busy}){
 const [current,setCurrent]=useState(''),[next,setNext]=useState(''),[confirm,setConfirm]=useState(''),[localError,setLocalError]=useState('')
 const submit=e=>{e.preventDefault();setLocalError('');if(next!==confirm){setLocalError('The new passwords do not match.');return}onSubmit(current,next)}
 return <main className="auth-page"><form className="auth-card" onSubmit={submit}><p className="eyebrow">ACCOUNT SECURITY</p><h1>Change your temporary password</h1><p className="muted">Choose a new password before continuing to the election system.</p><Field id="current-password" label="Temporary password"><input id="current-password" type="password" autoComplete="current-password" value={current} onChange={e=>setCurrent(e.target.value)} required/></Field><Field id="new-password" label="New password"><input id="new-password" type="password" autoComplete="new-password" value={next} onChange={e=>setNext(e.target.value)} required/></Field><Field id="confirm-password" label="Confirm new password"><input id="confirm-password" type="password" autoComplete="new-password" value={confirm} onChange={e=>setConfirm(e.target.value)} required/></Field>{localError&&<Notice tone="danger" title="Check the form">{localError}</Notice>}<ErrorNotice error={error}/><Button type="submit" disabled={busy}>{busy?'Saving…':'Change password'}</Button><Button variant="secondary" onClick={onLogout}>Sign out</Button></form></main>
}
function MessagePage({title,message,onClick,label='Return to sign in'}){return <main className="auth-page"><div className="auth-card status-page"><span className="status-illustration"><Icon name="lock" size={32}/></span><h1>{title}</h1><p className="muted">{message}</p><Button onClick={onClick}>{label}</Button></div></main>}
function Layout({role,user,path,navigate,logout,children}){const [menu,setMenu]=useState(false);useEffect(()=>setMenu(false),[path]);return <div className={`app-shell role-${role.toLowerCase()}`}><aside className={`sidebar ${menu?'sidebar-open':''}`} aria-label={`${role} navigation`}><div className="sidebar-logo"><span className="logo-square"><Icon name="vote" size={22}/></span><div><strong>CampusVote</strong><span>School Election Portal</span></div></div><div className="sidebar-context"><Badge>{role}</Badge></div><nav className="sidebar-links" aria-label="Primary">{NAV[role].map(([url,label,icon])=><a key={url} href={url} onClick={e=>{e.preventDefault();navigate(url)}} className={path===url?'nav-active':''} aria-current={path===url?'page':undefined}><Icon name={icon}/>{label}</a>)}</nav><div className="sidebar-footer"><span>Local school network</span><span>Academic election prototype</span></div></aside>{menu&&<button className="nav-backdrop" aria-label="Close menu" onClick={()=>setMenu(false)}/>}<div className="main-column"><header className="topbar"><div className="topbar-left"><button className="icon-button mobile-menu" aria-label="Open menu" onClick={()=>setMenu(v=>!v)}><Icon name="menu"/></button><strong className="topbar-title">{role==='STUDENT'?'Student Voting Portal':role==='ADMIN'?'Election Administration':'Election Monitoring'}</strong></div><div className="topbar-right"><span className="muted small">{user.display_name}</span><button className="btn btn-ghost" onClick={logout}><Icon name="logout"/> Sign out</button></div></header><main className="content" id="main-content"><div className="content-inner">{children}</div></main><footer className="footer">School election prototype · Internal LAN · Not certified for public elections</footer></div></div>}
function StudentRoutes({path,navigate,draft,setDraft,clearDraft}){
 const match=path.match(/^\/student\/elections\/(\d+)\/(candidates|ballot|review|confirmation|status)$/)
 if(path==='/student/dashboard'||path==='/student/elections')return <StudentHome navigate={navigate}/>
 if(!match)return <MessagePage title="Page not found" message="The requested student page does not exist." onClick={()=>navigate('/student/dashboard')} label="Go to elections"/>
 const id=Number(match[1]),page=match[2]
 if(page==='candidates')return <StudentCandidates electionId={id} navigate={navigate}/>
 if(page==='ballot')return <StudentBallot electionId={id} navigate={navigate} ballotDraft={draft} setBallotDraft={setDraft}/>
 if(page==='review')return <StudentReview electionId={id} navigate={navigate} ballotDraft={draft} clearDraft={clearDraft}/>
 if(page==='confirmation')return <StudentConfirmation electionId={id} navigate={navigate}/>
 return <StudentStatus electionId={id} navigate={navigate}/>
}
function AdminRoutes({path,navigate,user}){
 if(path==='/admin/dashboard')return <AdminHome navigate={navigate}/>
 if(path==='/admin/elections')return <AdminElections navigate={navigate}/>
 if(path==='/admin/elections/new')return <AdminElectionForm navigate={navigate}/>
 let found=path.match(/^\/admin\/elections\/(\d+)\/edit$/);if(found)return <AdminElectionForm navigate={navigate} id={Number(found[1])}/>
 found=path.match(/^\/admin\/elections\/(\d+)\/setup$/);if(found)return <AdminElectionSetup navigate={navigate} id={Number(found[1])}/>
 if(path==='/admin/candidates')return <AdminCandidates navigate={navigate}/>
 if(path==='/admin/candidates/new')return <AdminCandidateForm navigate={navigate}/>
 found=path.match(/^\/admin\/candidates\/(\d+)\/edit$/);if(found)return <AdminCandidateForm navigate={navigate} id={Number(found[1])}/>
 if(path==='/admin/voters')return <AdminVoters navigate={navigate}/>
 if(path==='/admin/voters/add')return <AdminVoterForm navigate={navigate}/>
 found=path.match(/^\/admin\/voters\/(\d+)\/edit$/);if(found)return <AdminVoterForm navigate={navigate} id={Number(found[1])}/>
 if(path==='/admin/staff')return <AdminStaffAccounts canCreateAdmin={user.can_create_admin}/>
 if(path==='/admin/monitoring')return <AdminMonitoring/>
 if(path==='/admin/results')return <AdminResults/>
 found=path.match(/^\/admin\/results\/(\d+)$/);if(found)return <AdminResults id={found[1]}/>
 if(path==='/admin/audit')return <AdminAudit/>
 if(path==='/admin/system')return <AdminHealth/>
 if(path==='/admin/reports')return <AdminReports/>
 if(path==='/admin/integrity')return <AdminIntegrity/>
 if(path==='/admin/settings')return <Unsupported title="Administrator settings" description="The Phase 9 backend has no general settings endpoint."/>
 return <MessagePage title="Page not found" message="The administrator route does not exist." onClick={()=>navigate('/admin/dashboard')} label="Go to dashboard"/>
}
function MonitorRoutes({path}){
 if(path==='/monitor/dashboard')return <MonitorDashboard/>
 if(path==='/monitor/participation')return <MonitorParticipation/>
 if(path==='/monitor/election-status')return <MonitorElectionStatus/>
 if(path==='/monitor/server-health')return <MonitorHealth/>
 if(path==='/monitor/results')return <MonitorResults/>
 return <Notice tone="warning" title="Page not found">This monitor page is unavailable.</Notice>
}
export default function App(){
 const [path,navigate]=usePath();const [auth,setAuth]=useState({checking:true,user:null});const [loginError,setLoginError]=useState(null),[loginBusy,setLoginBusy]=useState(false);const [passwordError,setPasswordError]=useState(null),[passwordBusy,setPasswordBusy]=useState(false);const [draft,setDraft]=useState(null)
 useEffect(()=>{let active=true;const init=async()=>{try{await api.csrf();const user=await api.me();if(active)setAuth({checking:false,user})}catch{if(active)setAuth({checking:false,user:null})}};init();return()=>{active=false}},[])
 useEffect(()=>{const expire=()=>{setAuth({checking:false,user:null});setDraft(null);navigate('/session-expired')};window.addEventListener('campusvote-session-expired',expire);return()=>window.removeEventListener('campusvote-session-expired',expire)},[])
 useEffect(()=>{if(auth.checking||!auth.user)return;if(auth.user.must_change_password){if(path!=='/change-password')navigate('/change-password');return}if(path==='/'||path==='/login'||path==='/change-password')navigate(HOME[auth.user.role]||'/unauthorized')},[auth.user,auth.checking,path])
 const login=async (username,password)=>{if(loginBusy)return;setLoginBusy(true);setLoginError(null);try{await api.csrf();const response=await api.login(username,password);const user=response.user||await api.me();setDraft(null);setAuth({checking:false,user});navigate(user.must_change_password?'/change-password':(HOME[user.role]||'/unauthorized'))}catch(e){setLoginError(e)}finally{setLoginBusy(false)}}
 const changePassword=async(currentPassword,newPassword)=>{if(passwordBusy)return;setPasswordBusy(true);setPasswordError(null);try{const user=await api.changePassword(currentPassword,newPassword);setAuth({checking:false,user});navigate(HOME[user.role]||'/unauthorized')}catch(e){setPasswordError(e)}finally{setPasswordBusy(false)}}
 const logout=async()=>{try{await api.logout()}catch{}setAuth({checking:false,user:null});setDraft(null);navigate('/login');api.csrf().catch(()=>{})}
 if(auth.checking)return <div className="auth-page"><LoadingState label="Checking your session with the local server…"/></div>
 if(!auth.user){if(path==='/session-expired')return <MessagePage title="Session expired" message="Your login session has ended. Please sign in again. If the server is unreachable, check your LAN connection." onClick={()=>navigate('/login')} />;return <Login onLogin={login} loginError={loginError} busy={loginBusy}/>}
 if(auth.user.must_change_password)return <PasswordChange onSubmit={changePassword} onLogout={logout} error={passwordError} busy={passwordBusy}/>
 const routeRole=roleForPath(path)
 if(path==='/unauthorized')return <MessagePage title="Access denied" message="Your account does not have permission to access this page." onClick={()=>navigate(HOME[auth.user.role])} label="Go to dashboard"/>
 if(!routeRole||routeRole!==auth.user.role)return <MessagePage title="Access denied" message="You cannot access a page belonging to a different role." onClick={()=>navigate(HOME[auth.user.role])} label="Return to my dashboard"/>
 let body=routeRole==='STUDENT'?<StudentRoutes path={path} navigate={navigate} draft={draft} setDraft={setDraft} clearDraft={()=>setDraft(null)}/>:routeRole==='ADMIN'?<AdminRoutes path={path} navigate={navigate} user={auth.user}/>:<MonitorRoutes path={path}/>
 return <Layout role={routeRole} user={auth.user} path={path} navigate={navigate} logout={logout}>{body}</Layout>
}
