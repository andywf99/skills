import os
import time
import logging
import httpx
from datetime import datetime
import difflib
import subprocess
from mcp.server.fastmcp import FastMCP

# 初始化 MCP Server
mcp = FastMCP("CodingMetricsLocal")

# 避免 httpx/httpcore 请求日志污染 stdio 型 MCP 通道
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

# 在内存中保存修改前快照
SNAPSHOTS = {}

# Java 后端接收 Diff 报表的接口地址 (根据您的实际环境配置)
JAVA_BACKEND_URL = os.environ.get("METRICS_API_URL", "http://10.21.61.76:32627/mcp/specReportDiff")

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
    """按 Git 风格统计新增/删除行，替换视为删除旧行并新增新行"""
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    
    added = 0
    removed = 0
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            removed += (i2 - i1)
            added += (j2 - j1)
        elif tag == 'delete':
            removed += (i2 - i1)
        elif tag == 'insert':
            added += (j2 - j1)
            
    return added, removed

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
        "startedAt": datetime.now().replace(microsecond=0).isoformat()
    }
    
    return "【本地specBeforeEditFile并成功上报】"


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
    
    added, removed = compute_diff(old_content, new_content)
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
        "modifiedLines": 0,
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
        return "【本地specAfterEditFile成功上报但结算失败】，接口异常：{str(e)}"
        
    return "【本地specAfterEditFile成功上报并结算成功】"

if __name__ == "__main__":
    mcp.run()
