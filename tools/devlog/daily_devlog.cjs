"use strict";
const ZONE="America/New_York";
function localDay(value) {
  const p=Object.fromEntries(new Intl.DateTimeFormat("en-US",{timeZone:ZONE,year:"numeric",month:"2-digit",day:"2-digit"}).formatToParts(new Date(value)).map(x=>[x.type,x.value]));
  return [p.year,p.month,p.day].join("-");
}
function precedingDay(now=new Date()){return localDay(new Date(new Date(now).getTime()-86400000));}
function onDay(timestamp,day){return !!timestamp && localDay(timestamp)===day;}
function clean(v){return String(v||"").replace(/[\r\n]+/g," ").replace(/[\[\]]/g,"");}
function link(title,url){return "["+clean(title)+"]("+url+")";}
function bullets(items,fn){return items.length?items.map(x=>"- "+fn(x)).join("\n"):"- No entries found in the bounded GitHub sample.";}
function summarize({day,repo,branch,commits,prs,issues,runs}){
  const dc=commits.filter(c=>onDay(c.commit?.committer?.date||c.commit?.author?.date,day));
  const dp=prs.filter(p=>onDay(p.updated_at,day)||onDay(p.merged_at,day));
  const di=issues.filter(i=>!i.pull_request&&onDay(i.updated_at,day));
  const dr=runs.filter(r=>onDay(r.updated_at||r.created_at,day)&&r.name!=="Daily development evidence log");
  const fc=dc.filter(c=>/^fix(?:\([^)]*\))?[!:]/i.test(c.commit?.message||""));
  const fp=dp.filter(p=>onDay(p.merged_at,day)&&/\b(?:fix|repair|bug)\b/i.test(p.title||""));
  const xp=dp.filter(p=>/\b(?:experiment|prototype|trial|spike|research|try)\b/i.test(p.title||""));
  const failed=dr.filter(r=>["failure","timed_out","cancelled","action_required"].includes(r.conclusion));
  const open=di.filter(i=>i.state==="open");
  const afz=[];
  if(failed.length)afz.push("**Failure diary candidate:** What failed in "+link(failed[0].name+" #"+failed[0].run_number,failed[0].html_url)+" and how I plan to verify the repair. A failed run is not evidence that the defect was fixed.");
  if(xp.length)afz.push("**Prototype diary candidate:** What I tried with "+link("#"+xp[0].number+" "+xp[0].title,xp[0].html_url)+" and what remains unverified.");
  const draft=dp.find(p=>p.draft);
  if(draft && !xp.some(p=>p.number===draft.number))afz.push("**Beginner progress candidate:** Why "+link("draft PR #"+draft.number+" "+draft.title,draft.html_url)+" isn't yet proof I have a playable feature.");
  if(!afz.length && dr.some(r=>r.conclusion==="success")){const ok=dr.find(r=>r.conclusion==="success");afz.push("**Testing lesson candidate:** What a green "+link(ok.name+" CI run",ok.html_url)+" does and does not prove about playing the game.");}
  const short=s=>String(s||"").slice(0,12);
  const pr=p=>link("#"+p.number+" "+p.title,p.html_url)+" — "+(p.merged_at?"merged":p.draft?"draft, unmerged":p.state+", unmerged")+"; head "+short(p.head?.sha);
  return [
    "# Daily development log — "+day+" (America/New_York)","",
    "**Repository:** "+repo,
    "**Coverage:** GitHub API bounded snapshot; default branch "+branch+" commits, updated PRs/issues, and workflow runs. Draft branch commits appear through PRs only.","",
    "## Work recorded",
    bullets(dc,c=>link(short(c.sha)+" "+(c.commit?.message||"").split("\n")[0],c.html_url)),"",
    "## Pull requests and feature work",bullets(dp,pr),"",
    "## Fixes (evidence-qualified)",
    "These are fix-labeled changes, not automatically independently verified defect resolutions:",
    bullets(fc.map(c=>({title:(c.commit?.message||"").split("\n")[0],url:c.html_url})).concat(fp.map(p=>({title:"merged PR #"+p.number+" "+p.title,url:p.html_url}))),x=>link(x.title,x.url)),"",
    "## Tests and CI tried",
    "GitHub Actions conclusions are not proof of native Unreal, PIE, GPU rendering, creator approval, or release.",
    bullets(dr,r=>link(r.name+" #"+r.run_number,r.html_url)+" — "+(r.conclusion||r.status||"unknown")+"; SHA "+short(r.head_sha)),"",
    "## Experiments or prototypes mentioned in PR titles",bullets(xp,pr),"",
    "## Problems and open blockers",bullets(failed,r=>link(r.name+" #"+r.run_number,r.html_url)+" — "+r.conclusion),"",
    "**Open issues updated that day** (updates do not prove a new issue arose):",
    bullets(open,i=>link("#"+i.number+" "+i.title,i.html_url)),"",
    "## AFZ story lead suggestions — review only",
    "These are optional beginner-build-diary editorial hooks from public GitHub activity, not scripts, assigned episodes, approved game footage, or published YouTube playlists. Verify source dates, spoilers, native evidence and rights before using. Submit selected leads to the relevant AFZ game story pipeline in Notion.",
    bullets(afz,x=>x),"",
    "## Evidence boundaries / next review",
    "- This is a source-activity index, not an accepted-feature changelog or a complete work-session record.",
    "- Coverage is limited to the latest 100 records per GitHub endpoint and this repository; local work, unpushed branches, private receipts, Notion-only work, and cross-repo activity are not included.",
    "- Review failed CI and unmerged PRs at exact heads before asserting completeness or quality.",
    "- This log does not authorize merges, canon changes, Starbourne access, or releases.",""
  ].join("\n");
}
async function collectAndPublish({github,context,core,now=new Date()}){
  const {owner,repo}=context.repo;
  const day=context.payload?.inputs?.date||precedingDay(now);
  const parsed=new Date(day+"T12:00:00Z");
  if(!/^\d{4}-\d{2}-\d{2}$/.test(day)||Number.isNaN(parsed.valueOf())||parsed.toISOString().slice(0,10)!==day)throw new Error("Invalid YYYY-MM-DD date");
  const info=(await github.rest.repos.get({owner,repo})).data;
  const branch=info.default_branch;
  const since=new Date(now.getTime()-8*86400000).toISOString();
  const [c,p,i,w]=await Promise.all([
    github.rest.repos.listCommits({owner,repo,sha:branch,since,per_page:100}),
    github.rest.pulls.list({owner,repo,state:"all",sort:"updated",direction:"desc",per_page:100}),
    github.rest.issues.listForRepo({owner,repo,state:"all",sort:"updated",direction:"desc",per_page:100}),
    github.rest.actions.listWorkflowRunsForRepo({owner,repo,per_page:100})
  ]);
  const report=summarize({day,repo:owner+"/"+repo,branch,commits:c.data,prs:p.data,issues:i.data,runs:w.data.workflow_runs||[]});
  const archive="automation/daily-devlog",ref="heads/"+archive,path="docs/devlog/"+day+".md";
  let old;
  try{old=(await github.rest.git.getRef({owner,repo,ref})).data.object.sha;}
  catch(e){if(e.status!==404)throw e; const base=(await github.rest.repos.getBranch({owner,repo,branch})).data.commit.sha;
    await github.rest.git.createRef({owner,repo,ref:"refs/"+ref,sha:base});old=base;}
  try{const existing=(await github.rest.repos.getContent({owner,repo,path,ref:archive})).data;
    if(!Array.isArray(existing)&&existing.content&&Buffer.from(existing.content,"base64").toString("utf8")===report){core.info("Unchanged: "+path);return;}}
  catch(e){if(e.status!==404)throw e;}
  const root=(await github.rest.git.getCommit({owner,repo,commit_sha:old})).data;
  const tree=(await github.rest.git.createTree({owner,repo,base_tree:root.tree.sha,tree:[{path,mode:"100644",type:"blob",content:report}]})).data;
  const commit=(await github.rest.git.createCommit({owner,repo,message:"docs(devlog): record "+day+" ET activity",tree:tree.sha,parents:[old]})).data;
  await github.rest.git.updateRef({owner,repo,ref,sha:commit.sha,force:false});
  core.info("Published "+path+" at "+commit.sha+" on "+archive);
}
module.exports={localDay,precedingDay,onDay,summarize,collectAndPublish};
