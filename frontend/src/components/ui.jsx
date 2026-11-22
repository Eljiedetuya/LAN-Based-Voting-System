import React from 'react'
export function Icon({name,size=18}) {
 const paths={
  vote:<><path d="M4 10h16v11H4z"/><path d="m9 3 6 3-3 5-6-3z"/><path d="M8 15h8"/></>,
  home:<><path d="m3 10 9-7 9 7"/><path d="M5 9v12h14V9"/><path d="M9 21v-7h6v7"/></>,
  users:<><circle cx="9" cy="8" r="3"/><path d="M3 20v-2a6 6 0 0 1 12 0v2"/><path d="M17 5a3 3 0 0 1 0 6"/><path d="M19 14a5 5 0 0 1 2 4v2"/></>,
  calendar:<><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/></>,
  check:<><path d="m4 12 5 5L20 6"/></>,
  chevron:<><path d="m9 18 6-6-6-6"/></>,
  back:<><path d="m15 18-6-6 6-6"/></>,
  chart:<><path d="M4 20V4M4 20h17M8 16v-4M13 16V8M18 16V5"/></>,
  list:<><path d="M9 6h12M9 12h12M9 18h12"/><path d="M4 6h.01M4 12h.01M4 18h.01"/></>,
  shield:<><path d="m12 2 9 4v6c0 6-4 9-9 10-5-1-9-4-9-10V6z"/><path d="m8 12 3 3 5-6"/></>,
  network:<><rect x="9" y="2" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="16" y="16" width="6" height="6" rx="1"/><path d="M12 8v4M5 16v-4h14v4"/></>,
  file:<><path d="M6 2h9l4 4v16H6z"/><path d="M15 2v5h4M9 12h7M9 16h7"/></>,
  alert:<><path d="m12 3 10 18H2z"/><path d="M12 9v5M12 18h.01"/></>,
  info:<><circle cx="12" cy="12" r="10"/><path d="M12 11v6M12 7h.01"/></>,
  logout:<><path d="M10 4H4v16h6M14 8l4 4-4 4M8 12h10"/></>,
  settings:<><circle cx="12" cy="12" r="3"/><path d="M4 12h3M17 12h3M12 4v3M12 17v3M6.4 6.4l2.2 2.2m6.8 6.8 2.2 2.2m0-11.2-2.2 2.2m-6.8 6.8-2.2 2.2"/></>,
  lock:<><rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></>,
  search:<><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></>,
  clock:<><circle cx="12" cy="12" r="9"/><path d="M12 7v6l4 2"/></>,
  server:<><rect x="3" y="3" width="18" height="8" rx="1"/><rect x="3" y="13" width="18" height="8" rx="1"/><path d="M7 7h.01M7 17h.01"/></>,
  menu:<><path d="M4 6h16M4 12h16M4 18h16"/></>,
  x:<><path d="M5 5l14 14M19 5 5 19"/></>,
  plus:<><path d="M12 5v14M5 12h14"/></>,
  arrow:<><path d="M4 12h16m-6-6 6 6-6 6"/></>
 }
 return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">{paths[name]||paths.info}</svg>
}
export function Badge({children,tone='neutral'}) {return <span className={`badge badge-${tone}`}>{children}</span>}
export function Notice({tone='info',title,children}) {return <div className={`notice notice-${tone}`} role={tone==='danger'?'alert':'status'}><Icon name={tone==='danger'||tone==='warning'?'alert':tone==='success'?'check':'info'}/><div><strong>{title}</strong>{children&&<div className="notice-body">{children}</div>}</div></div>}
export function Button({children,variant='primary',type='button',disabled=false,onClick,icon, ...props}) {return <button className={`btn btn-${variant}`} type={type} disabled={disabled} onClick={onClick} {...props}>{icon&&<Icon name={icon} size={17}/>}<span>{children}</span></button>}
export function PageHeader({eyebrow,title,description,action}) {return <div className="page-heading"><div>{eyebrow&&<p className="eyebrow">{eyebrow}</p>}<h1>{title}</h1>{description&&<p className="lead">{description}</p>}</div>{action&&<div className="heading-action">{action}</div>}</div>}
export function Panel({title,subtitle,action,children,className=''}){return <section className={`panel ${className}`}><div className="panel-heading"><div><h2>{title}</h2>{subtitle&&<p className="muted small">{subtitle}</p>}</div>{action}</div>{children}</section>}
export function StatCard({label,value,detail}){return <article className="stat-card"><span className="stat-label">{label}</span><strong className="stat-value">{value}</strong>{detail&&<span className="small muted">{detail}</span>}</article>}
export function EmptyState({title='Nothing to display',description,action}){return <div className="empty-state"><Icon name="info" size={29}/><strong>{title}</strong><p>{description||'There are no items to show.'}</p>{action}</div>}
export function LoadingState({label='Loading…'}){return <div className="loading" role="status"><span className="spinner" aria-hidden="true"/>{label}</div>}
export function Field({label,id,hint,error,children}){return <div className="field"><label htmlFor={id}>{label}</label>{children}{hint&&<span className="hint">{hint}</span>}{error&&<span className="field-error" role="alert">{error}</span>}</div>}
export function DataTable({columns,rows,empty='No records to display'}){return rows.length?<div className="table-scroll"><table><thead><tr>{columns.map(c=><th key={c.key} scope="col">{c.label}</th>)}</tr></thead><tbody>{rows.map((row,i)=><tr key={row.id??i}>{columns.map(c=><td key={c.key}>{c.render?c.render(row):row[c.key]}</td>)}</tr>)}</tbody></table></div>:<EmptyState title={empty}/>}
export function DemoNote(){return <div className="demo-note" role="note"><Icon name="info" size={16}/><span>DEMO DATA — Sample records for UI design only. No live election information.</span></div>}
export function Progress({value,max=100,label}){return <div className="progress-wrap"><div className="progress-track" role="progressbar" aria-label={label||'Progress'} aria-valuemin={0} aria-valuemax={max} aria-valuenow={value}><div className="progress-fill" style={{width:`${Math.min(100,Math.max(0,100*value/max))}%`}}/></div></div>}
export function BarChart({data}){const max=Math.max(1,...data.map(d=>d.value));return <div className="bar-chart" aria-label="Illustrative vote totals"><div className="chart-rows">{data.map(d=><div className="chart-row" key={d.label}><span className="chart-label">{d.label}</span><div className="chart-rail"><div className="chart-bar" style={{width:`${100*d.value/max}%`}}/></div><strong className="chart-number">{d.value}</strong></div>)}</div></div>}
export function TextLink({to,children,navigate}){return <a href={to} onClick={e=>{if(navigate){e.preventDefault();navigate(to)}}}>{children}</a>}
