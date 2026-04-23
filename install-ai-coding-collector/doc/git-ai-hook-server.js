const http = require("http");
const {spawnSync} = require("child_process");
const fs = require("fs");
const path = require("path");

const PORT = Number(process.env.GIT_AI_HOOK_PORT || 39393);
const HOST = "127.0.0.1";
const USER_HOME = process.env.USERPROFILE || process.env.HOME || process.cwd();
const STRICT = String(process.env.GIT_AI_STRICT || "1") === "1"; // 1=严格模式
const MAX_BODY = Number(process.env.GIT_AI_MAX_BODY || 2 * 1024 * 1024);

const diagDir = path.join(USER_HOME, ".git-ai", "diag");
const logFile = path.join(diagDir, "claude-http-hook.log");
const pidFile = path.join(diagDir, "claude-http-hook-server.pid");
const lastPayloadFile = path.join(diagDir, "last-hook-payload.json");
const lastErrFile = path.join(diagDir, "last-checkpoint-stderr.log");
const lastOutFile = path.join(diagDir, "last-checkpoint-stdout.log");

function ensureDiagDir() {
    try {
        fs.mkdirSync(diagDir, {recursive: true});
    } catch (_) {
    }
}

function log(msg) {
    const line = `[${new Date().toISOString()}] ${msg}\n`;
    try {
        ensureDiagDir();
        fs.appendFileSync(logFile, line, "utf8");
    } catch (_) {
    }
}

function writeFileSafe(file, content) {
    try {
        fs.writeFileSync(file, content ?? "", "utf8");
    } catch (_) {
    }
}

function firstExisting(paths) {
    for (const p of paths) {
        if (!p) continue;
        try {
            if (fs.existsSync(p)) return p;
        } catch (_) {
        }
    }
    return "";
}

function resolveFromWhere(cmd) {
    try {
        const r = spawnSync("where", [cmd], {encoding: "utf8", timeout: 3000, windowsHide: true});
        if (r.status !== 0 || !r.stdout) return "";
        return firstExisting(r.stdout.split(/\r?\n/).map(s => s.trim()).filter(Boolean));
    } catch (_) {
        return "";
    }
}

function resolveGitAiPath() {
    return firstExisting([
        process.env.GIT_AI_PATH,
        path.join(USER_HOME, ".git-ai", "bin", "git-ai.exe"),
        path.join(USER_HOME, ".git-ai", "bin", "git-ai")
    ]) || resolveFromWhere("git-ai.exe") || resolveFromWhere("git-ai") || "";
}

function acquireLockOrExit() {
    ensureDiagDir();
    try {
        if (fs.existsSync(pidFile)) {
            const oldPid = Number(String(fs.readFileSync(pidFile, "utf8")).trim());
            if (oldPid && Number.isFinite(oldPid)) {
                try {
                    process.kill(oldPid, 0);
                    log(`Another instance running (pid=${oldPid}), exit.`);
                    process.exit(0);
                } catch (_) {
                }
            }
        }
        fs.writeFileSync(pidFile, String(process.pid), "utf8");
    } catch (e) {
        log(`WARN lock failed: ${e.message}`);
    }
}

function releaseLock() {
    try {
        if (!fs.existsSync(pidFile)) return;
        const current = String(fs.readFileSync(pidFile, "utf8")).trim();
        if (current === String(process.pid)) fs.unlinkSync(pidFile);
    } catch (_) {
    }
}

const gitAi = resolveGitAiPath();
acquireLockOrExit();

const server = http.createServer((req, res) => {
    const reply = (ok, code, reason) => {
        const status = ok ? 200 : (code || 500);
        const payload = JSON.stringify({ok, reason: reason || (ok ? "ok" : "error")});
        try {
            if (!res.headersSent) res.setHeader("Content-Type", "application/json");
            res.statusCode = status;
            res.end(payload);
        } catch (_) {
        }
    };

    if (req.method !== "POST" || req.url !== "/claude-post") {
        return reply(false, 404, "not_found");
    }

    if (!gitAi) {
        log("ERROR git-ai executable not found");
        return reply(!STRICT, STRICT ? 500 : 200, "git_ai_not_found");
    }

    const chunks = [];
    let size = 0;
    let bodyTooLarge = false;

    req.on("data", c => {
        chunks.push(c);
        size += c.length;
        if (size > MAX_BODY) bodyTooLarge = true;
    });

    req.on("error", err => {
        log(`REQ ERROR: ${err.message}`);
        return reply(!STRICT, STRICT ? 500 : 200, "request_stream_error");
    });

    req.on("end", () => {
        try {
            if (bodyTooLarge) {
                log(`WARN body too large: ${size}`);
                return reply(!STRICT, STRICT ? 413 : 200, "body_too_large");
            }

            const body = Buffer.concat(chunks).toString("utf8").trim();
            log(`POST len=${body.length}`);
            writeFileSafe(lastPayloadFile, body);

            if (!body) {
                log("WARN empty body");
                return reply(!STRICT, STRICT ? 400 : 200, "empty_body");
            }

            let obj;
            try {
                obj = JSON.parse(body);
            } catch (e) {
                log(`ERROR invalid json: ${e.message}`);
                return reply(!STRICT, STRICT ? 400 : 200, "invalid_json");
            }

            const eventName = obj?.hook_event_name || "";
            const toolName = obj?.tool_name || "";
            const filePath = obj?.tool_input?.file_path || "";
            const transcriptPath = obj?.transcript_path || "";

            log(`event=${eventName} tool=${toolName} file=${filePath} transcript=${transcriptPath}`);

            if (!transcriptPath) {
                log("WARN missing transcript_path");
                return reply(!STRICT, STRICT ? 422 : 200, "missing_transcript_path");
            }

            if (toolName && /bash/i.test(toolName)) {
                log("WARN tool_name=Bash; generated/script edits may not be fully attributed");
            }

            const r = spawnSync(gitAi, ["checkpoint", "claude", "--hook-input", "stdin"], {
                input: body,
                encoding: "utf8",
                timeout: 15000,
                windowsHide: true
            });

            writeFileSafe(lastOutFile, r.stdout || "");
            writeFileSafe(lastErrFile, r.stderr || "");

            log(`checkpoint status=${r.status} signal=${r.signal || ""}`);
            if (r.error) log(`checkpoint error=${r.error.message}`);
            if (r.stdout && r.stdout.trim()) log(`stdout=${r.stdout.trim()}`);
            if (r.stderr && r.stderr.trim()) log(`stderr=${r.stderr.trim()}`);

            // 严格模式：只要不是明确成功就返回失败
            if (r.error) return reply(false, 500, `checkpoint_error:${r.error.message}`);
            if (r.signal) return reply(false, 500, `checkpoint_signal:${r.signal}`);
            if (typeof r.status !== "number" || r.status !== 0) {
                return reply(false, 500, `checkpoint_exit_${r.status}`);
            }

            return reply(true, 200, "checkpoint_ok");
        } catch (e) {
            log(`HANDLER ERROR: ${e.stack || e.message}`);
            return reply(!STRICT, STRICT ? 500 : 200, "handler_exception");
        }
    });
});

server.on("error", err => {
    log(`SERVER ERROR: ${err.code || ""} ${err.message}`);
    if (err.code === "EADDRINUSE") {
        log(`Port ${PORT} already in use. Exit current process.`);
        releaseLock();
        process.exit(0);
    }
});

server.keepAliveTimeout = 5000;
server.headersTimeout = 10000;
server.requestTimeout = 20000;

process.on("uncaughtException", err => {
    log(`UNCAUGHT: ${err.stack || err.message}`);
});
process.on("unhandledRejection", reason => {
    log(`UNHANDLED_REJECTION: ${String(reason)}`);
});
["SIGINT", "SIGTERM", "SIGHUP", "exit"].forEach(sig => {
    process.on(sig, () => {
        try {
            server.close(() => releaseLock());
        } catch (_) {
            releaseLock();
        }
    });
});

server.listen(PORT, HOST, () => {
    log(`server listening http://${HOST}:${PORT}`);
    log(`pid=${process.pid}`);
    log(`strict=${STRICT}`);
    log(`gitAi=${gitAi || "NOT_FOUND"}`);
});