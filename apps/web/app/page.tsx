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
