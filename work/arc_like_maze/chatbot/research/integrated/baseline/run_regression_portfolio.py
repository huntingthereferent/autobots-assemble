import pathlib,sys,subprocess, re
root=pathlib.Path(__file__).parent
files=sorted(p.stem for p in root.glob('test_ab_chatbot_*.py'))
count=0;fail=[]; summaries=[]
for name in files:
 try:
  p=subprocess.run([sys.executable,'-m','unittest','-q',name],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=36)
  match=re.search(r'Ran (\d+) tests?',p.stdout)
  num=int(match.group(1)) if match else 0
  if p.returncode==0 and match:
   count+=num; print('PASS',name,num,flush=True);summaries.append(f'PASS {name}: {num}')
  else:
   print('FAIL',name,p.returncode,p.stdout[-1200:],flush=True);fail.append(name)
 except subprocess.TimeoutExpired:
  print('TIMEOUT',name,flush=True);fail.append(name)
report=f"Local regression: {count} completed passing tests / {len(summaries)} modules; not completed: {fail}\n"+'\n'.join(summaries)+'\n'
(root/'REGRESSION_PORTFOLIO_2026-10-12.txt').write_text(report)
print('SUMMARY',count,'modules',len(summaries),'issues',fail,flush=True)
