#!/usr/bin/env node
/**
 * Claude Code ↔ Ollama Proxy
 *
 * Solves the issue where Claude Code CLI uses deprecated url.parse()
 * which breaks on Node ≥ 22. This proxy uses the WHATWG URL API and
 * properly forwards all requests to Ollama.
 *
 * Usage:
 *   node scripts/claude-ollama-proxy.mjs [--port 11435] [--ollama-port 11434]
 *
 * Then set in ~/.claude/settings.json:
 *   "ANTHROPIC_BASE_URL": "http://127.0.0.1:11435"
 */

import http from 'node:http';
import { argv } from 'node:process';

// Parse CLI args
const args = argv.slice(2);
const getArg = (name, def) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : def;
};

const PROXY_PORT = parseInt(getArg('--port', '11435'), 10);
const OLLAMA_HOST = getArg('--ollama-host', '127.0.0.1');
const OLLAMA_PORT = parseInt(getArg('--ollama-port', '11434'), 10);

// Endpoints that Claude Code calls
const KNOWN_ENDPOINTS = new Set([
  '/v1/messages',
  '/v1/models',
  '/v1/chat/completions',
  '/v1/completions',
]);

function log(tag, msg) {
  const ts = new Date().toISOString().slice(11, 19);
  console.log(`[${ts}] [${tag}] ${msg}`);
}

const server = http.createServer((req, res) => {
  // Use WHATWG URL API (not deprecated url.parse)
  const reqUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const path = reqUrl.pathname;

  log('→', `${req.method} ${path}`);

  // Collect request body
  const chunks = [];
  req.on('data', (chunk) => chunks.push(chunk));
  req.on('end', () => {
    const body = Buffer.concat(chunks);

    // ────── Anthropic /v1/messages → OpenAI /v1/chat/completions ──────
    if (path === '/v1/messages' && req.method === 'POST') {
      let data;
      try { data = JSON.parse(body.toString()); } catch { data = {}; }
      const msgs = data.messages?.length || 0;
      const tools = data.tools?.length || 0;
      const model = data.model || '?';
      const stream = data.stream ?? false;
      log('→', `  model=${model} msgs=${msgs} tools=${tools} stream=${stream}`);

      // Convert Anthropic messages to OpenAI format
      const openaiMessages = [];

      // System prompt
      if (data.system) {
        const sysTxt = typeof data.system === 'string'
          ? data.system
          : (Array.isArray(data.system) ? data.system.map(b => b.text || '').join('\n') : '');
        if (sysTxt) openaiMessages.push({ role: 'system', content: sysTxt });
      }

      // Convert messages
      for (const msg of (data.messages || [])) {
        const role = msg.role === 'assistant' ? 'assistant' : 'user';
        if (typeof msg.content === 'string') {
          openaiMessages.push({ role, content: msg.content });
        } else if (Array.isArray(msg.content)) {
          // Multi-part content → concatenate text blocks
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

      // Convert tools to OpenAI format
      let openaiTools = undefined;
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

      // Model name mapping
      const MODEL_MAP = {
        'qwen3.5-35b-claude': 'qwen3.5-40B:latest',
        'qwen3.5-40b-claude': 'qwen3.5-40B:latest',
      };
      const ollamaModel = MODEL_MAP[model] || MODEL_MAP[model.toLowerCase()] || model;

      const openaiBody = {
        model: ollamaModel,
        messages: openaiMessages,
        stream: false, // always non-stream for conversion simplicity
        temperature: data.temperature ?? 0.3,
        max_tokens: data.max_tokens || 8192,
      };
      if (openaiTools) openaiBody.tools = openaiTools;

      const fwdBody = Buffer.from(JSON.stringify(openaiBody));
      log('⇒', `Translated to /v1/chat/completions model=${ollamaModel} msgs=${openaiMessages.length}`);

      const fwdReq = http.request(
        {
          hostname: OLLAMA_HOST,
          port: OLLAMA_PORT,
          method: 'POST',
          path: '/v1/chat/completions',
          headers: {
            'content-type': 'application/json',
            'content-length': fwdBody.length,
            'host': `${OLLAMA_HOST}:${OLLAMA_PORT}`,
          },
          timeout: 300_000,
        },
        (fwdRes) => {
          log('←', `${fwdRes.statusCode} /v1/chat/completions`);
          const respChunks = [];
          fwdRes.on('data', (c) => respChunks.push(c));
          fwdRes.on('end', () => {
            const raw = Buffer.concat(respChunks).toString();
            try {
              const oaiResp = JSON.parse(raw);
              const choice = oaiResp.choices?.[0] || {};
              const assistantMsg = choice.message || {};

              // Build Anthropic response
              const content = [];

              // Text
              if (assistantMsg.content) {
                content.push({ type: 'text', text: assistantMsg.content });
              }

              // Tool calls → tool_use blocks
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

              const anthropicResp = {
                id: 'msg_' + Math.random().toString(36).slice(2, 14),
                type: 'message',
                role: 'assistant',
                model: data.model || ollamaModel,
                content,
                stop_reason: stopReason,
                stop_sequence: null,
                usage: {
                  input_tokens: oaiResp.usage?.prompt_tokens || 0,
                  output_tokens: oaiResp.usage?.completion_tokens || 0,
                },
              };

              const respBody = JSON.stringify(anthropicResp);
              log('⇐', `Translated response: ${content.length} blocks, stop=${stopReason}`);
              res.writeHead(200, {
                'content-type': 'application/json',
                'content-length': Buffer.byteLength(respBody),
              });
              res.end(respBody);
            } catch (e) {
              log('!', `Response parse error: ${e.message}`);
              log('!', `Raw: ${raw.slice(0, 200)}`);
              if (!res.headersSent) {
                res.writeHead(502, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: { type: 'proxy_error', message: 'Failed to parse Ollama response: ' + e.message } }));
              }
            }
          });
        }
      );

      fwdReq.on('error', (err) => {
        log('!', `Error forwarding to Ollama: ${err.message}`);
        if (!res.headersSent) {
          res.writeHead(502, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: { type: 'proxy_error', message: err.message } }));
        }
      });
      fwdReq.on('timeout', () => {
        log('!', `Ollama request timed out`);
        fwdReq.destroy();
        if (!res.headersSent) {
          res.writeHead(504, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: { type: 'timeout', message: 'Ollama timed out' } }));
        }
      });
      fwdReq.write(fwdBody);
      fwdReq.end();
      return;
    }

    // ────── Pass-through for all other endpoints ──────
    if (body.length > 0 && path !== '/v1/messages') {
      try {
        const data = JSON.parse(body.toString());
        log('→', `  model=${data.model || '?'}`);
      } catch { /* ignore */ }
    }

    // Forward to Ollama
    const fwdHeaders = {};
    for (const [k, v] of Object.entries(req.headers)) {
      if (k !== 'host' && k !== 'transfer-encoding') {
        fwdHeaders[k] = v;
      }
    }
    fwdHeaders['host'] = `${OLLAMA_HOST}:${OLLAMA_PORT}`;
    fwdHeaders['content-length'] = body.length;

    const fwdReq = http.request(
      {
        hostname: OLLAMA_HOST,
        port: OLLAMA_PORT,
        method: req.method,
        path: path + reqUrl.search,
        headers: fwdHeaders,
        timeout: 300_000, // 5 min
      },
      (fwdRes) => {
        log('←', `${fwdRes.statusCode} ${path}`);

        // Copy response headers
        const resHeaders = {};
        for (const [k, v] of Object.entries(fwdRes.headers)) {
          if (k !== 'transfer-encoding') {
            resHeaders[k] = v;
          }
        }

        res.writeHead(fwdRes.statusCode, resHeaders);

        // Stream response body back to Claude Code
        fwdRes.on('data', (chunk) => {
          res.write(chunk);
        });
        fwdRes.on('end', () => {
          res.end();
        });
      }
    );

    fwdReq.on('error', (err) => {
      log('!', `Error forwarding to Ollama: ${err.message}`);
      if (!res.headersSent) {
        res.writeHead(502, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: { type: 'proxy_error', message: err.message } }));
      }
    });

    fwdReq.on('timeout', () => {
      log('!', `Request to Ollama timed out`);
      fwdReq.destroy();
      if (!res.headersSent) {
        res.writeHead(504, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: { type: 'timeout', message: 'Ollama request timed out' } }));
      }
    });

    fwdReq.write(body);
    fwdReq.end();
  });

  req.on('error', (err) => {
    log('!', `Client request error: ${err.message}`);
  });
});

server.listen(PROXY_PORT, '127.0.0.1', () => {
  log('✓', `Claude-Ollama proxy listening on 127.0.0.1:${PROXY_PORT}`);
  log('✓', `Forwarding to Ollama at ${OLLAMA_HOST}:${OLLAMA_PORT}`);
  log('✓', `Set ANTHROPIC_BASE_URL=http://127.0.0.1:${PROXY_PORT}`);
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    log('!', `Port ${PROXY_PORT} already in use. Kill existing process or use --port <N>`);
  } else {
    log('!', `Server error: ${err.message}`);
  }
  process.exit(1);
});
