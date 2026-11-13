"use client";
import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
type User = { email: string; tenant_id: string };

export default function Home() {
  const [mode,setMode] = useState<"register"|"login">("register");
  const [email,setEmail] = useState("");
  const [password,setPassword] = useState("");
  const [workspace,setWorkspace] = useState("My Career Workspace");
  const [token,setToken] = useState("");
  const [user,setUser] = useState<User|null>(null);
  const [status,setStatus] = useState("");
  const [facts,setFacts] = useState<any[]>([]);
  const [profile,setProfile] = useState<any>(null);
  const [file,setFile] = useState<File|null>(null);
  const [jobs,setJobs] = useState<any[]>([]);
  const [jobQuery,setJobQuery] = useState("");
  const [jobLocation,setJobLocation] = useState("");
  const [sources,setSources] = useState<any[]>([]);
  const [provider,setProvider] = useState("greenhouse");
  const [companyName,setCompanyName] = useState("");
  const [boardToken,setBoardToken] = useState("");

  async function request(path:string, options:RequestInit={}) {
    const response = await fetch(`${API}/api/v1${path}`, {
      ...options,
      headers: { ...(options.body instanceof FormData ? {} : {"Content-Type":"application/json"}), ...(token ? {Authorization:`Bearer ${token}`} : {}), ...(options.headers||{}) }
    });
    const data = await response.json().catch(()=>({detail:"Unexpected server response"}));
    if (!response.ok) throw new Error(data.detail || "Request failed");
    return data;
  }

  async function authenticate(e:React.FormEvent) {
    e.preventDefault(); setStatus("Please wait...");
    try {
      const path = mode==="register" ? "/auth/register" : "/auth/login";
      const body = mode==="register" ? {email,password,workspace_name:workspace} : {email,password};
      const result = await fetch(`${API}/api/v1${path}`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
      const data = await result.json();
      if (!result.ok) throw new Error(data.detail || "Authentication failed");
      setToken(data.access_token);
      const meRes = await fetch(`${API}/api/v1/auth/me`,{headers:{Authorization:`Bearer ${data.access_token}`}});
      const me = await meRes.json();
      setUser({email:me.email,tenant_id:me.tenant_id});
      const authHeaders={Authorization:`Bearer ${data.access_token}`};
      const [sourceResponse,jobResponse]=await Promise.all([
        fetch(`${API}/api/v1/sources`,{headers:authHeaders}),
        fetch(`${API}/api/v1/jobs`,{headers:authHeaders})
      ]);
      if(sourceResponse.ok) setSources(await sourceResponse.json());
      if(jobResponse.ok) setJobs((await jobResponse.json()).items || []);
      setStatus("Welcome to CareerPilot.");
    } catch(err:any) { setStatus(err.message); }
  }

  async function loadWorkspace() {
    try {
      const p = await request("/profile");
      const f = await request("/profile/facts");
      setProfile(p); setFacts(f);
    } catch(err:any) { setStatus(err.message); }
  }

  async function uploadResume() {
    if (!file) return;
    const form = new FormData(); form.append("file",file);
    try {
      const result = await request("/resumes",{method:"POST",body:form});
      setStatus(`Resume processed. ${result.extracted_characters} characters extracted. Review proposed facts below.`);
      await loadWorkspace();
    } catch(err:any) { setStatus(err.message); }
  }

  async function loadJobs() {
    try {
      const params = new URLSearchParams();
      if (jobQuery.trim()) params.set("q",jobQuery.trim());
      if (jobLocation.trim()) params.set("location",jobLocation.trim());
      const result = await request(`/jobs?${params.toString()}`);
      setJobs(result.items || []);
    } catch(err:any) { setStatus(err.message); }
  }

  async function loadSources() {
    try { setSources(await request("/sources")); }
    catch(err:any) { setStatus(err.message); }
  }

  async function addSource(e:React.FormEvent) {
    e.preventDefault();
    try {
      await request("/sources",{method:"POST",body:JSON.stringify({provider,company_name:companyName,board_token:boardToken})});
      setCompanyName(""); setBoardToken("");
      await loadSources();
      setStatus("Job source added.");
    } catch(err:any) { setStatus(err.message); }
  }

  async function syncSource(id:string) {
    try {
      const result = await request(`/sources/${id}/sync`,{method:"POST"});
      setStatus(`Sync complete: ${result.fetched} fetched, ${result.created} new, ${result.updated} updated, ${result.marked_stale} stale.`);
      await loadSources(); await loadJobs();
    } catch(err:any) { setStatus(err.message); await loadSources(); }
  }

  async function confirmFact(id:string,statusValue:"confirmed"|"rejected", value?:string) {
    try {
      await request(`/profile/facts/${id}/confirm`,{method:"POST",body:JSON.stringify({status:statusValue,corrected_value:value||null})});
      await loadWorkspace();
    } catch(err:any) { setStatus(err.message); }
  }

  if (!user) return <main style={{maxWidth:480,margin:"8vh auto",padding:28,background:"white",borderRadius:18,boxShadow:"0 12px 45px #1d2d4a12"}}>
    <p style={{fontWeight:800,color:"#5366b2",letterSpacing:2}}>CAREERPILOT AI</p>
    <h1 style={{fontSize:34,marginBottom:8}}>Your next career move starts here.</h1>
    <p style={{color:"#667085",lineHeight:1.6}}>Create your private workspace to organize your career profile and discover relevant opportunities.</p>
    <div style={{display:"flex",gap:8,margin:"24px 0"}}>
      <button onClick={()=>setMode("register")} style={tab(mode==="register")}>Create account</button>
      <button onClick={()=>setMode("login")} style={tab(mode==="login")}>Sign in</button>
    </div>
    <form onSubmit={authenticate} style={{display:"grid",gap:14}}>
      {mode==="register" && <Field label="Workspace name" value={workspace} onChange={setWorkspace}/>}
      <Field label="Email" value={email} onChange={setEmail} type="email"/>
      <Field label="Password (minimum 10 characters)" value={password} onChange={setPassword} type="password"/>
      <button style={primary}>{mode==="register"?"Create workspace":"Sign in"}</button>
    </form>
    <p aria-live="polite" style={{color:"#667085",fontSize:13,marginTop:16}}>{status}</p>
  </main>;

  return <main style={{maxWidth:1000,margin:"40px auto",padding:24}}>
    <header style={{display:"flex",justifyContent:"space-between",alignItems:"center",gap:12,flexWrap:"wrap"}}>
      <div><p style={{fontWeight:800,color:"#5366b2",letterSpacing:2}}>CAREERPILOT AI</p><h1 style={{margin:"4px 0"}}>Candidate workspace</h1><p style={{color:"#667085"}}>{user.email}</p></div>
      <button onClick={()=>{setUser(null);setToken("");}} style={secondary}>Sign out</button>
    </header>
    <section style={panel}>
      <h2>Job discovery</h2>
      <p style={{color:"#667085"}}>Search active jobs ingested from public Greenhouse, Lever and Ashby job boards.</p>
      <div style={{display:"flex",gap:8,flexWrap:"wrap"}}>
        <input placeholder="Role, skill or company" value={jobQuery} onChange={e=>setJobQuery(e.target.value)} style={searchInput}/>
        <input placeholder="Location (e.g. India, Bengaluru)" value={jobLocation} onChange={e=>setJobLocation(e.target.value)} style={searchInput}/>
        <button onClick={loadJobs} style={primary}>Search jobs</button>
      </div>
      <div style={{display:"grid",gap:12,marginTop:16}}>
        {jobs.map(job=><article key={job.id} style={{border:"1px solid #e5e9f0",borderRadius:10,padding:14}}>
          <div style={{display:"flex",justifyContent:"space-between",gap:12,flexWrap:"wrap"}}>
            <div><b>{job.title}</b><div style={{color:"#475467",marginTop:4}}>{job.company_name} · {job.location || "Location not specified"}</div><small style={{color:"#667085"}}>{job.provider} · {job.employment_type || "Type not specified"} · {job.workplace_type || "Workplace not specified"}</small></div>
            <a href={job.job_url} target="_blank" rel="noreferrer" style={{color:"#465bb5",fontWeight:700}}>View job ↗</a>
          </div>
        </article>)}
        {jobs.length===0 && <p style={{color:"#667085"}}>No jobs loaded yet. Add a job board below, sync it, then search.</p>}
      </div>
    </section>
    <section style={panel}>
      <h2>Job sources</h2>
      <p style={{color:"#667085"}}>Add a public job-board identifier. Greenhouse: board token from boards.greenhouse.io/BOARD. Lever: site name from jobs.lever.co/SITE. Ashby: final segment from jobs.ashbyhq.com/BOARD.</p>
      <form onSubmit={addSource} style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(180px,1fr))",gap:10}}>
        <select value={provider} onChange={e=>setProvider(e.target.value)} style={searchInput}><option value="greenhouse">Greenhouse</option><option value="lever">Lever</option><option value="ashby">Ashby</option></select>
        <input required placeholder="Company name" value={companyName} onChange={e=>setCompanyName(e.target.value)} style={searchInput}/>
        <input required placeholder="Board token / site name" value={boardToken} onChange={e=>setBoardToken(e.target.value)} style={searchInput}/>
        <button style={primary}>Add source</button>
      </form>
      <div style={{display:"flex",gap:8,marginTop:14}}><button onClick={loadSources} style={secondary}>Refresh sources</button><button onClick={loadJobs} style={secondary}>Refresh jobs</button></div>
      {sources.map(source=><article key={source.id} style={{borderTop:"1px solid #e7eaf0",padding:"12px 0",display:"flex",justifyContent:"space-between",gap:12,flexWrap:"wrap"}}>
        <div><b>{source.company_name}</b><div style={{color:"#667085",fontSize:13}}>{source.provider} · {source.board_token} · {source.last_sync_status}</div>{source.last_sync_error && <small style={{color:"#b42318"}}>{source.last_sync_error}</small>}</div>
        <button onClick={()=>syncSource(source.id)} style={secondary}>Sync now</button>
      </article>)}
    </section>
    <section style={panel}>
      <h2>Upload your resume</h2>
      <p style={{color:"#667085"}}>PDF or DOCX, up to 10 MB. Extracted facts remain proposed until you confirm them.</p>
      <input type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onChange={e=>setFile(e.target.files?.[0]||null)}/>
      <button onClick={uploadResume} disabled={!file} style={{...primary,marginLeft:10}}>Upload and parse</button>
    </section>
    <section style={panel}>
      <h2>Extracted facts to review</h2>
      <button onClick={loadWorkspace} style={secondary}>Refresh facts</button>
      {facts.length===0 ? <p style={{color:"#667085"}}>No extracted facts yet. Upload a resume to begin.</p> : facts.map(f=><article key={f.id} style={{borderTop:"1px solid #e7eaf0",padding:"14px 0",display:"flex",justifyContent:"space-between",gap:16,flexWrap:"wrap"}}>
        <div><b>{f.fact_key}</b><div>{f.fact_value}</div><small style={{color:"#667085"}}>{f.status} · confidence {Number(f.confidence).toFixed(2)}</small></div>
        <div style={{display:"flex",gap:8}}><button onClick={()=>confirmFact(f.id,"confirmed")} style={secondary}>Confirm</button><button onClick={()=>confirmFact(f.id,"rejected")} style={secondary}>Reject</button></div>
      </article>)}
    </section>
    <section style={panel}>
      <h2>Profile</h2>
      <button onClick={loadWorkspace} style={secondary}>Load profile</button>
      {profile && <pre style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere",background:"#f5f7fb",padding:14,borderRadius:8}}>{JSON.stringify(profile,null,2)}</pre>}
    </section>
    <p aria-live="polite" style={{color:"#667085"}}>{status}</p>
  </main>;
}

function Field({label,value,onChange,type="text"}:{label:string,value:string,onChange:(v:string)=>void,type?:string}) {
  return <label style={{display:"grid",gap:6,fontSize:14,fontWeight:600}}>{label}<input required value={value} type={type} onChange={e=>onChange(e.target.value)} style={{padding:12,border:"1px solid #d8deea",borderRadius:8,fontSize:15}}/></label>;
}
const primary:React.CSSProperties={padding:"12px 16px",background:"#465bb5",color:"white",border:0,borderRadius:9,fontWeight:700,cursor:"pointer"};
const secondary:React.CSSProperties={padding:"9px 12px",background:"white",color:"#344054",border:"1px solid #d8deea",borderRadius:8,cursor:"pointer"};
function tab(active:boolean):React.CSSProperties { return {flex:1,padding:10,border:0,borderRadius:8,background:active?"#e9edff":"#f5f7fb",color:"#344054",fontWeight:700,cursor:"pointer"}; }
const panel:React.CSSProperties={background:"white",padding:22,borderRadius:14,border:"1px solid #e5e9f0",marginTop:20};
const searchInput:React.CSSProperties={padding:11,border:"1px solid #d8deea",borderRadius:8,fontSize:14,minWidth:180,flex:1};
