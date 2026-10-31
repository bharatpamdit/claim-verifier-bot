from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any
import ast, re
from pathlib import PurePosixPath

app=FastAPI(title="IssueLens Analyzer",version="1.0.0")

class Request(BaseModel):
    claims:list[dict[str,Any]]
    files:list[dict[str,str]]

STOP={"the","and","for","with","from","that","this","when","then","does","not","but","are","was","were","has","have","returns","return","error","issue","after","before","into","request","valid"}

def terms(claim):
    raw=re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", " ".join([claim.get("claim",""),claim.get("component","")," ".join(claim.get("keywords",[]) or [])]))
    return list(dict.fromkeys(x.lower() for x in raw if x.lower() not in STOP))[:16]

def symbols(path,content):
    found=[]
    if path.endswith(".py"):
        try:
            tree=ast.parse(content)
            for n in ast.walk(tree):
                if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                    found.append({"name":n.name,"line":n.lineno,"kind":"class" if isinstance(n,ast.ClassDef) else "function"})
        except SyntaxError: pass
    elif path.endswith((".js",".jsx",".ts",".tsx")):
        for pat,kind in [(r"function\s+([\w$]+)\s*\(","function"),(r"class\s+([\w$]+)","class"),(r"\.(get|post|put|patch|delete)\s*\(\s*['\"`]([^'\"`]+)","route")]:
            for m in re.finditer(pat,content):
                line=content.count("\n",0,m.start())+1
                name=(m.group(1).upper()+" "+m.group(2)) if kind=="route" else m.group(1)
                found.append({"name":name,"line":line,"kind":kind})
    return found

@app.get("/health")
def health(): return {"ok":True}

@app.post("/analyze")
def analyze(req:Request):
    allowed={".py",".js",".jsx",".ts",".tsx",".md",".json"}
    fs=[]
    for f in req.files:
        path=f.get("path",""); content=f.get("content","")
        if PurePosixPath(path).suffix.lower() in allowed and len(content)<100000:
            fs.append((path,content))
    output=[]
    for c in req.claims:
        ts=terms(c); matches=[]
        for path,content in fs:
            lines=content.splitlines()
            syms=symbols(path,content)
            for i,line in enumerate(lines,1):
                lowered=line.lower()
                hits=[t for t in ts if re.search(r"(?<![a-z0-9_])"+re.escape(t)+r"(?![a-z0-9_])", lowered)]
                if hits:
                    lo=max(1,i-3); hi=min(len(lines),i+3)
                    snippet="\n".join(f"{j}: {lines[j-1]}" for j in range(lo,hi+1))
                    matches.append({"file":path,"startLine":lo,"endLine":hi,"matchedLine":i,"matchedTerms":hits[:8],"snippet":snippet,"symbolsNearMatch":[s for s in syms if abs(s["line"]-i)<=15][:5],"evidenceType":"static_code_match","strength":"candidate"})
                    if len(matches)>=8: break
            if len(matches)>=8: break
        output.append({"claimId":c.get("id"),"claim":c.get("claim"),"matches":matches,"evidenceCount":len(matches),"status":"candidate_evidence_found" if matches else "no_candidate_evidence_found"})
    return {"evidence":output,"filesScanned":len(fs),"warning":"Keyword/static matches are candidate leads, not proof of runtime behavior."}
