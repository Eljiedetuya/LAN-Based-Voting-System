// Synthetic demonstration data: never presented as real election records.
export const election = { id: 1, title: 'Student Council Election 2026', status: 'OPEN', closesAt: '2026-12-10T16:00:00+08:00', description: 'Demo election for user interface review only.' }
export const positions = [
 {id:10,name:'President',description:'Student leadership and campus representation',candidates:[
  {id:101,name:'Alex Rivera',platform:'Improve student support, strengthen communication, and expand campus activities.',bio:'A student advocate focused on accessible campus services.'},
  {id:102,name:'Jordan Santos',platform:'Build stronger student clubs and more transparent student-led initiatives.',bio:'Committed to student participation and practical school improvements.'}]},
 {id:11,name:'Vice President',description:'Support the student council and its initiatives',candidates:[
  {id:103,name:'Taylor Cruz',platform:'Create inclusive events and responsive student feedback programs.',bio:'Interested in collaboration across student organizations.'},
  {id:104,name:'Morgan Reyes',platform:'Improve coordination between classes and school activities.',bio:'An organizer focused on reliable school programs.'}]},
 {id:12,name:'Secretary',description:'Maintain records and communications',candidates:[
  {id:105,name:'Sam Lee',platform:'Make announcements clear, accessible, and timely.',bio:'Focused on clear communication and accountability.'},
  {id:106,name:'Casey Lim',platform:'Bring consistency and organization to student council records.',bio:'Values documentation and transparent processes.'}]},
]
export const voters = Array.from({length:12},(_,i)=>({id:i+1,studentId:`STU-${String(i+1).padStart(3,'0')}`,name:['Avery Santos','Jamie Cruz','Riley Mendoza','Harper Lee','Quinn Garcia','Drew Reyes','Parker Diaz','Emery Tan','Rowan Ramos','Skyler Lim','Charlie Torres','Alexis Flores'][i],status:i===10?'Disabled':'Active',eligible:i!==10,hasVoted:i<7}))
export const audit = [{id:1,action:'Election opened',actor:'Election Administrator',target:'Student Council Election 2026',at:'2026-11-18 09:00'},{id:2,action:'Candidate updated',actor:'Election Administrator',target:'Candidate profile',at:'2026-11-17 14:20'},{id:3,action:'Voter account created',actor:'Election Administrator',target:'STU-012',at:'2026-11-17 13:11'}]
export const stats = {eligible:100,recorded:63,remaining:37,turnout:63,lastUpdated:'Illustrative snapshot — not live'}
export const demoElectionStatus = 'OPEN'
