#!/usr/bin/env node
/**
 * Claude Code ↔ DeepSeek Proxy
 *
 * Translates Anthropic Messages API (/v1/messages) → OpenAI Chat Completions
 * and forwards to DeepSeek API (https://api.deepseek.com/v1).
 *
 * Usage:
 *   node scripts/claude-deepseek-proxy.mjs --port 11435 --api-key sk-xxx
 *
 * Then set in ~/.claude/settings.json:
 *   "ANTHROPIC_BASE_URL": "http://127.0.0.1:11435"
 *   "ANTHROPIC_MODEL": "claude-sonnet-4-20250514"
 */

import http from 'node:http';
import https from 'node:https';
import { argv } from 'node:process';

// ── CLI Args ─────────────────────────────────────────────────
const args = argv.slice(2);
const getArg = (name, def) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : def;
};

const PROXY_PORT = parseInt(getArg('--port', '11435'), 10);
const DEEPSEEK_API_KEY = getArg('--api-key', process.env.DEEPSEEK_API_KEY || '');
const DEEPSEEK_HOST = 'api.deepseek.com';
const DEEPSEEK_MODEL = getArg('--model', 'deepseek-chat');

// Model name mapping: Claude model names → DeepSeek model names
const MODEL_MAP = {
  'claude-sonnet-4-20250514': DEEPSEEK_MODEL,
  'claude-3-5-sonnet-20241022': DEEPSEEK_MODEL,
  'claude-3-5-haiku-20241022': DEEPSEEK_MODEL,
};

function log(tag, msg) {
  const ts = new Date().toISOString().slice(11, 19);
  console.log(`[${ts}] [${tag}] ${msg}`);
}

// ── Anthropic → OpenAI message conversion ────────────────────
function convertMessages(data) {
  const openaiMessages = [];

  // System prompt
  if (data.system) {
    const sysTxt = typeof data.system === 'string'
      ? data.system
      : (Array.isArray(data.system) ? data.system.map(b => b.text || '').join('\n') : '');
    if (sysTxt) openaiMessages.push({ role: 'system', content: sysTxt });
  }

  // Messages
  for (const msg of (data.messages || [])) {
    const role = msg.role === 'assistant' ? 'assistant' : 'user';
    if (typeof msg.content === 'string') {
      openaiMessages.push({ role, content: msg.content });
    } else if (Array.isArray(msg.content)) {
      const parts = [];
      const toolCalls = [];
      const toolResults = [];
      for (const block of msg.content) {
        if (block.type === 'text') {
          parts.push(block.text || '');
        } else if (block.type === 'tool_use') {
          toolCalls.push({
            id: block.id || ('call_' + Math.random().toString(36).slice(2, 10)),
            type: 'function',
            function: { name: block.name, arguments: JSON.stringify(block.input || {}) },
          });
        } else if (block.type === 'tool_result') {
          const content = typeof block.content === 'string'
            ? block.content
            : (Array.isArray(block.content)
              ? block.content.map(b => b.text || '').join('\n')
              : JSON.stringify(block.content || ''));
          toolResults.push({ tool_call_id: block.tool_use_id, role: 'tool', content });
        }
      }
      if (toolCalls.length > 0) {
        openaiMessages.push({ role: 'assistant', content: parts.join('\n') || null, tool_calls: toolCalls });
      } else if (toolResults.length > 0) {
        for (const tr of toolResults) openaiMessages.push(tr);
      } else if (parts.length > 0) {
        openaiMessages.push({ role, content: parts.join('\n') });
      }
    }
  }

  // Tools
  let openaiTools;
  if (data.tools && data.tools.length > 0) {
    openaiTools = data.tools.map(t => ({
      type: 'function',
      function: {
        name: t.name,
        description: t.description || '',
        parameters: t.input_schema || { type: 'object', properties: {} },
      },
    }));
  }

  return { openaiMessages, openaiTools };
}

// ── OpenAI response → Anthropic response ─────────────────────
function convertResponse(oaiResp, requestModel) {
  const choice = oaiResp.choices?.[0] || {};
  const assistantMsg = choice.message || {};
  const content = [];

  if (assistantMsg.content) {
    content.push({ type: 'text', text: assistantMsg.content });
  }

  if (assistantMsg.tool_calls) {
    for (const tc of assistantMsg.tool_calls) {
      let args = {};
      try { args = JSON.parse(tc.function?.arguments || '{}'); } catch { /* */ }
      content.push({
        type: 'tool_use',
        id: tc.id || ('toolu_' + Math.random().toString(36).slice(2, 12)),
        name: tc.function?.name || 'unknown',
        input: args,
      });
    }
  }

  if (content.length === 0) {
    content.push({ type: 'text', text: assistantMsg.content || 'No response.' });
  }

  const stopReason = assistantMsg.tool_calls ? 'tool_use' :
    (choice.finish_reason === 'length' ? 'max_tokens' : 'end_turn');

  return {
    id: 'msg_' + Math.random().toString(36).slice(2, 14),
    type: 'message',
    role: 'assistant',
    model: requestModel,
    content,
    stop_reason: stopReason,
    stop_sequence: null,
    usage: {
      input_tokens: oaiResp.usage?.prompt_tokens || 0,
      output_tokens: oaiResp.usage?.completion_tokens || 0,
    },
  };
}

// ── Server ───────────────────────────────────────────────────
const server = http.createServer((req, res) => {
  const reqUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const path = reqUrl.pathname;
  log('→', `${req.method} ${path}`);

  const chunks = [];
  req.on('data', (chunk) => chunks.push(chunk));
  req.on('end', () => {
    const body = Buffer.concat(chunks);

    // ── /v1/messages → DeepSeek /v1/chat/completions ──
    if (path === '/v1/messages' && req.method === 'POST') {
      let data;
      try { data = JSON.parse(body.toString()); } catch { data = {}; }
      const model = data.model || '?';
      log('→', `  model=${model} msgs=${data.messages?.length || 0} tools=${data.tools?.length || 0}`);

      const targetModel = MODEL_MAP[model] || MODEL_MAP[model.toLowerCase()] || DEEPSEEK_MODEL;
      const { openaiMessages, openaiTools } = convertMessages(data);

      const openaiBody = {
        model: targetModel,
        messages: openaiMessages,
        stream: false,
        temperature: data.temperature ?? 0.3,
        max_tokens: Math.min(data.max_tokens || 8192, 8192),
      };
      if (openaiTools) openaiBody.tools = openaiTools;

      const fwdBody = Buffer.from(JSON.stringify(openaiBody));
      log('⇒', `→ DeepSeek model=${targetModel} msgs=${openaiMessages.length}`);

      const fwdReq = https.request(
        {
          hostname: DEEPSEEK_HOST,
          port: 443,
          method: 'POST',
          path: '/v1/chat/completions',
          headers: {
            'content-type': 'application/json',
            'content-length': fwdBody.length,
            'authorization': `Bearer ${DEEPSEEK_API_KEY}`,
          },
          timeout: 120_000,
        },
        (fwdRes) => {
          log('←', `${fwdRes.statusCode} /v1/chat/completions`);
          const respChunks = [];
          fwdRes.on('data', (c) => respChunks.push(c));
          fwdRes.on('end', () => {
            const raw = Buffer.concat(respChunks).toString();
            try {
              const oaiResp = JSON.parse(raw);

              if (fwdRes.statusCode !== 200) {
                log('!', `DeepSeek error: ${raw.slice(0, 300)}`);
                res.writeHead(fwdRes.statusCode, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                  type: 'error',
                  error: { type: 'api_error', message: oaiResp.error?.message || `HTTP ${fwdRes.statusCode}` },
                }));
                return;
              }

              const anthropicResp = convertResponse(oaiResp, model);
              const respBody = JSON.stringify(anthropicResp);
              log('⇐', `OK ${anthropicResp.content.length} blocks, stop=${anthropicResp.stop_reason}, tokens=${anthropicResp.usage.output_tokens}`);
              res.writeHead(200, {
                'content-type': 'application/json',
                'content-length': Buffer.byteLength(respBody),
              });
              res.end(respBody);
            } catch (e) {
              log('!', `Parse error: ${e.message} — raw: ${raw.slice(0, 200)}`);
              if (!res.headersSent) {
                res.writeHead(502, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: { type: 'proxy_error', message: e.message } }));
              }
            }
          });
        }
      );

      fwdReq.on('error', (err) => {
        log('!', `DeepSeek request error: ${err.message}`);
        if (!res.headersSent) {
          res.writeHead(502, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: { type: 'proxy_error', message: err.message } }));
        }
      });
      fwdReq.on('timeout', () => {
        log('!', 'DeepSeek request timed out');
        fwdReq.destroy();
        if (!res.headersSent) {
          res.writeHead(504, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: { type: 'timeout', message: 'DeepSeek timed out' } }));
        }
      });
      fwdReq.write(fwdBody);
      fwdReq.end();
      return;
    }

    // ── /v1/models — return fake Anthropic model list ──
    if (path === '/v1/models' || path === '/models') {
      const body = JSON.stringify({
        object: 'list',
        data: Object.keys(MODEL_MAP).map(id => ({
          id, object: 'model', created: Math.floor(Date.now() / 1000), owned_by: 'deepseek-proxy',
        })),
      });
      res.writeHead(200, { 'content-type': 'application/json', 'content-length': Buffer.byteLength(body) });
      res.end(body);
      return;
    }

    // ── Fallback ──
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: { type: 'not_found', message: `Unknown endpoint: ${path}` } }));
  });

  req.on('error', (err) => log('!', `Client error: ${err.message}`));
});

// ── Start ────────────────────────────────────────────────────
if (!DEEPSEEK_API_KEY) {
  log('!', 'Missing --api-key or DEEPSEEK_API_KEY environment variable');
  process.exit(1);
}

server.listen(PROXY_PORT, '127.0.0.1', () => {
  log('✓', `Claude-DeepSeek proxy on 127.0.0.1:${PROXY_PORT}`);
  log('✓', `Forwarding to DeepSeek API (model: ${DEEPSEEK_MODEL})`);
  log('✓', `API key: ${DEEPSEEK_API_KEY.slice(0, 6)}...${DEEPSEEK_API_KEY.slice(-4)}`);
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    log('!', `Port ${PROXY_PORT} already in use`);
  } else {
    log('!', `Server error: ${err.message}`);
  }
  process.exit(1);
});
