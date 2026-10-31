import express from "express";
import cors from "cors";
import { connectRepo, repositoryReport, issues, pulls, analyze } from "./workflow.js";

const app = express();
app.use(cors({ origin: ["http://localhost:5173", "http://127.0.0.1:5173"] }));
app.use(express.json({ limit: "1mb" }));
const requestToken = req => String(req.get("x-github-token") || "").trim() || undefined;

app.get("/api/health", (_req,res) => res.json({ok:true}));
app.post("/api/repos/connect", async (req,res,next) => {
  try { res.json(await connectRepo(req.body?.url,requestToken(req))); } catch(e) { next(e); }
});
app.get("/api/repos/:owner/:repo/report", async (req,res,next) => {
  try { res.json(await repositoryReport(req.params.owner,req.params.repo,requestToken(req))); } catch(e) { next(e); }
});
app.get("/api/repos/:owner/:repo/issues", async (req,res,next) => {
  try { res.json(await issues(req.params.owner,req.params.repo,requestToken(req))); } catch(e) { next(e); }
});
app.get("/api/repos/:owner/:repo/pulls", async (req,res,next) => {
  try { res.json(await pulls(req.params.owner,req.params.repo,requestToken(req))); } catch(e) { next(e); }
});
app.post("/api/analysis/issue", async (req,res,next) => {
  try { res.json(await analyze({...req.body,type:"issue"},requestToken(req))); } catch(e) { next(e); }
});
app.post("/api/analysis/pr", async (req,res,next) => {
  try { res.json(await analyze({...req.body,type:"pr"},requestToken(req))); } catch(e) { next(e); }
});
app.use((err,_req,res,_next) => {
  if ((err.status || 500) >= 500) console.error(err);
  res.status(err.status || 500).json({error:err.message || "Internal server error"});
});
export default app;
