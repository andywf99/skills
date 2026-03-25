import os
import time
import httpx
from datetime import datetime, timezone
import difflib
import subprocess
from mcp.server.fastmcp import FastMCP

# 初始化 MCP Server
mcp = FastMCP("CodingMetricsLocal")

# 在内存中保存修改前快照
SNAPSHOTS = {}

# Java 后端接收 Diff 报表的接口地址 (根据您的实际环境配置)
JAVA_BACKEND_URL = os.environ.get("METRICS_API_URL", "http://localhost:8080/mcp/specReportDiff")

def get_git_branch(path: str) -> str:
    """尝试从当前目录获取 Git 分支"""
    try:
        dir_path = os.path.dirname(path) if os.path.isfile(path) else path
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=dir_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"

def compute_diff(old_text: str, new_text: str):
    """简单的多行文本差异计算"""
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    
    added = 0
    removed = 0
    modified = 0
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            modified += max(i2 - i1, j2 - j1)
        elif tag == 'delete':
            removed += (i2 - i1)
        elif tag == 'insert':
            added += (j2 - j1)
            
    return added, removed, modified

@mcp.tool()
async def specBeforeEditFile(
    absoluteFilePath: str,
    appName: str,
    sessionId: str,
    teamId: str,
    userId: str,
    gitBranch: str = ""
) -> str:
    """记录修改前快照。在修改文件前必须调用本工具。不再将全文传给网络端，直接存在本地。"""
    try:
        with open(absoluteFilePath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = ""
        
    SNAPSHOTS[absoluteFilePath] = {
        "content": content,
        "startedAt": datetime.now(timezone.utc).isoformat()
    }
    
    return f"【本地防篡改】已在内存成功记录修改前快照: {absoluteFilePath}"


@mcp.tool()
async def specAfterEditFile(
    absoluteFilePath: str,
    appName: str,
    sessionId: str,
    teamId: str,
    userId: str,
    gitBranch: str = ""
) -> str:
    """记录修改后结算命令，计算差异（Diff）并将结构化指标上报给服务端。"""
    if absoluteFilePath not in SNAPSHOTS:
        return f"错误：未找 {absoluteFilePath} 的修改前快照。请确保您已经先调用了 specBeforeEditFile。"
        
    start_time = time.time()
    
    try:
        with open(absoluteFilePath, 'r', encoding='utf-8') as f:
            new_content = f.read()
    except FileNotFoundError:
        new_content = ""
        
    snapshot = SNAPSHOTS.pop(absoluteFilePath)
    old_content = snapshot["content"]
    startedAt = snapshot["startedAt"]
    
    added, removed, modified = compute_diff(old_content, new_content)
    elapsed_ms = int((time.time() - start_time) * 1000)
    
    if not gitBranch:
        gitBranch = get_git_branch(absoluteFilePath)
        
    payload = {
        "sessionId": sessionId,
        "userId": userId,
        "teamId": teamId,
        "appName": appName,
        "absoluteFilePath": absoluteFilePath,
        "operation": "afterEditFile",
        "addedLines": added,
        "removedLines": removed,
        "modifiedLines": modified,
        "addedLineNumbers": [], 
        "removedLineNumbers": [],
        "modifiedLineNumbers": [],
        "gitBranch": gitBranch,
        "elapsedMs": elapsed_ms,
        "startedAt": startedAt
    }
    
    # 异步 POST 给 Java 后端
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(JAVA_BACKEND_URL, json=payload, timeout=5.0)
            resp.raise_for_status()
    except Exception as e:
        return f"【本地Diff完成但上报失败】({added} 增, {removed} 删, {modified} 改)，接口异常：{str(e)}"
        
    return f"【本地Diff并成功上报】新增 {added} 行，移除 {removed} 行，修改 {modified} 行。"

if __name__ == "__main__":
    mcp.run()
