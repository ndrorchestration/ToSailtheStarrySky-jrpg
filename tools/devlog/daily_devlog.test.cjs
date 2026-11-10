"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const {localDay,precedingDay,onDay,summarize}=require("./daily_devlog.cjs");
test("New York winter and summer date boundaries",()=>{
  assert.equal(localDay("2026-11-10T04:59:00Z"),"2026-11-09");
  assert.equal(localDay("2026-11-10T05:01:00Z"),"2026-11-10");
  assert.equal(localDay("2026-07-10T03:59:00Z"),"2026-07-09");
  assert.equal(localDay("2026-07-10T04:01:00Z"),"2026-07-10");
});
test("Prior complete day at scheduled time",()=>assert.equal(precedingDay(new Date("2026-11-11T11:00:00Z")),"2026-11-10"));
test("ET date filter excludes next day",()=>{
  assert.equal(onDay("2026-11-10T04:45:00Z","2026-11-09"),true);
  assert.equal(onDay("2026-11-10T05:01:00Z","2026-11-09"),false);
});
test("Draft PR and successful CI do not become native or merged proof",()=>{
  const report=summarize({day:"2026-11-09",repo:"owner/game",branch:"main",commits:[],issues:[],
    prs:[{number:4,title:"prototype bridge",updated_at:"2026-11-10T03:30:00Z",html_url:"https://github.com/owner/game/pull/4",draft:true,state:"open",head:{sha:"12345678901234"}}],
    runs:[{name:"Source Tests",run_number:8,updated_at:"2026-11-10T03:30:00Z",html_url:"https://github.com/owner/game/actions/runs/8",conclusion:"success",head_sha:"12345678901234"}]});
  assert.match(report,/draft, unmerged/);
  assert.match(report,/not proof of native Unreal/);
  assert.match(report,/success/);
});
test("Fix prefix remains qualified",()=>{
  const report=summarize({day:"2026-11-09",repo:"owner/game",branch:"main",prs:[],issues:[],runs:[],
    commits:[{sha:"abc123456789",commit:{committer:{date:"2026-11-10T03:00:00Z"},message:"fix: input collision"},html_url:"https://github.com/owner/game/commit/abc123456789"}]});
  assert.match(report,/fix-labeled changes, not automatically independently verified/);
});
