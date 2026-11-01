# -*- coding: utf-8 -*-
"""Install a disabled launchd job; activation is a separate explicit command."""
import argparse,os,plistlib,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LABEL='com.paperwiki.inbox'
def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','enable','pause','remove','status']);args=p.parse_args()
    path=Path.home()/'Library/LaunchAgents'/ (LABEL+'.plist');domain='gui/'+str(os.getuid());service=domain+'/'+LABEL
    def launch(*xs):return subprocess.run(['launchctl',*xs],check=False).returncode
    if args.action=='prepare':
        if path.exists():raise SystemExit('任务已存在；请先查看，避免覆盖。')
        (ROOT/'state/logs').mkdir(parents=True,exist_ok=True);path.parent.mkdir(parents=True,exist_ok=True)
        data=dict(Label=LABEL,ProgramArguments=['/bin/bash',str(ROOT/'run.sh')],WorkingDirectory=str(ROOT),StartInterval=43200,RunAtLoad=True,Disabled=True,ProcessType='Background',StandardOutPath=str(ROOT/'state/logs/launchd.out.log'),StandardErrorPath=str(ROOT/'state/logs/launchd.err.log'),EnvironmentVariables={'PATH':'/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS','PYTHONUTF8':'1'})
        path.write_bytes(plistlib.dumps(data));print('已安装停用的任务：'+str(path)+'；尚未 bootstrap。')
    elif args.action=='enable':
        if not path.exists():raise SystemExit('请先 prepare')
        data=plistlib.loads(path.read_bytes());data['Disabled']=False;path.write_bytes(plistlib.dumps(data))
        if launch('enable',service):raise SystemExit('enable 失败')
        if launch('bootstrap',domain,str(path)):raise SystemExit('bootstrap 失败；若已载入请查看 status')
    elif args.action=='pause':launch('disable',service);launch('bootout',service)
    elif args.action=='remove':
        launch('disable',service);launch('bootout',service);path.unlink(missing_ok=True)
    else:
        print('配置文件：'+str(path));print('配置存在：'+str(path.exists()));launch('print',service);launch('print-disabled',domain)
if __name__=='__main__':main()
