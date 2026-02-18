/**
 * AI Native 双船模拟后端服务
 * 使用 Node.js + Express + MCP + MiniMax LLM
 */

import express from 'express';
import cors from 'cors';
import bodyParser from 'body-parser';
import { config } from 'dotenv';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

config({ path: join(dirname(fileURLToPath(import.meta.url)), '.env') });

const app = express();
const PORT = process.env.PORT || 3001;

// 中间件
app.use(cors());
app.use(bodyParser.json({ limit: '10mb' }));
app.use(express.static(join(dirname(fileURLToPath(import.meta.url)), '..')));
// 首页 - 重定向到 index-refactored.html
app.get('/', (req, res) => {
  res.sendFile(join(dirname(fileURLToPath(import.meta.url)), '..', 'index-refactored.html'));
});

// ============================================
// MiniMax LLM 集成
// ============================================

class MiniMaxClient {
  constructor(apiKey, baseUrl, model) {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
    this.model = model;
  }

  async chat(messages, temperature = 0.7) {
    const response = await fetch(`${this.baseUrl}/text/chatcompletion_v2`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        model: this.model,
        messages,
        temperature,
        max_tokens: 4096
      })
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`MiniMax API error: ${error}`);
    }

    const data = await response.json();
    return data.choices?.[0]?.message?.content || '';
  }
}

// 初始化 MiniMax 客户端
const minimax = new MiniMaxClient(
  process.env.MINIMAX_API_KEY,
  process.env.MINIMAX_BASE_URL,
  process.env.MINIMAX_MODEL || 'abab6.5s-chat'
);

// ============================================
// MCP 服务 - AI Agent 核心
// ============================================

class SimulationAgent {
  constructor(llmClient) {
    this.llm = llmClient;
    
    // 默认场景配置
    this.defaultScene = {
      ocean: {
        waveHeight: 1.5,
        waveSpeed: 1.0,
        waveFrequency: 0.5,
        waterColor: '#006994',
        fogDensity: 0.02
      },
      physics: {
        gravity: -9.81,
        waterDensity: 1025,
        linearDamping: 0.1,
        angularDamping: 0.3,
        buoyancyPoints: 8
      },
      boats: {
        boat1: {
          position: { x: -5, y: 0, z: 0 },
          rotation: { x: 0, y: 0, z: 0 },
          scale: 1.0,
          mass: 500
        },
        boat2: {
          position: { x: 5, y: 0, z: 0 },
          rotation: { x: 0, y: 0, z: 0 },
          scale: 1.0,
          mass: 500
        }
      },
      lighting: {
        ambientIntensity: 0.4,
        directionalIntensity: 1.0,
        sunPosition: { x: 50, y: 100, z: 50 }
      },
      camera: {
        position: { x: 0, y: 15, z: 30 },
        fov: 60,
        near: 0.1,
        far: 1000
      }
    };
    
    this.currentScene = JSON.parse(JSON.stringify(this.defaultScene));
  }

  // 系统提示词
  getSystemPrompt() {
    return `你是双船模拟器的 AI 控制器。你可以根据用户请求生成场景配置、调整物理参数、控制3D模型。

可用的控制能力：
1. 场景生成 - 生成不同环境（海洋、天气、时间）
2. 物理模拟参数调整 - 重力、水密度、阻尼、浮力点数
3. 3D模型控制 - 船只位置、旋转、缩放
4. 灯光控制 - 环境光强度、太阳位置
5. 相机控制 - 位置、视野

物理参数范围：
- 重力: -20 ~ 0 (默认 -9.81)
- 水密度: 500 ~ 2000 (默认 1025 kg/m³)
- 线性阻尼: 0 ~ 1 (默认 0.1)
- 角阻尼: 0 ~ 1 (默认 0.3)
- 波浪高度: 0 ~ 10 (默认 1.5)
- 波浪速度: 0 ~ 5 (默认 1.0)

返回 JSON 格式，结构如下：
{
  "action": "scene|physics|model|light|camera|status",
  "params": { ... },
  "reasoning": "你的推理过程"
}`;
  }

  // 处理用户请求
  async processRequest(userMessage) {
    const messages = [
      { role: 'system', content: this.getSystemPrompt() },
      { 
        role: 'user', 
        content: `当前场景配置: ${JSON.stringify(this.currentScene, null, 2)}\n\n用户请求: ${userMessage}`
      }
    ];

    try {
      const response = await this.llm.chat(messages, 0.7);
      const parsed = this.parseLLMResponse(response);
      return this.executeAction(parsed);
    } catch (error) {
      return {
        success: false,
        error: error.message,
        scene: this.currentScene
      };
    }
  }

  // 解析 LLM 响应
  parseLLMResponse(response) {
    try {
      // 尝试提取 JSON
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      throw new Error('No JSON found in response');
    } catch (e) {
      // 返回状态查询
      return {
        action: 'status',
        params: {},
        reasoning: '无法解析响应，返回当前状态'
      };
    }
  }

  // 执行动作
  executeAction(parsed) {
    const { action, params, reasoning } = parsed;
    let result = { success: true, reasoning };

    switch (action) {
      case 'scene':
        this.currentScene = { ...this.currentScene, ...params };
        result.scene = this.currentScene;
        result.message = '场景配置已更新';
        break;

      case 'physics':
        this.currentScene.physics = { ...this.currentScene.physics, ...params };
        result.scene = this.currentScene;
        result.message = '物理参数已更新';
        break;

      case 'model':
        if (params.boat1) {
          this.currentScene.boats.boat1 = { ...this.currentScene.boats.boat1, ...params.boat1 };
        }
        if (params.boat2) {
          this.currentScene.boats.boat2 = { ...this.currentScene.boats.boat2, ...params.boat2 };
        }
        result.scene = this.currentScene;
        result.message = '3D模型参数已更新';
        break;

      case 'light':
        this.currentScene.lighting = { ...this.currentScene.lighting, ...params };
        result.scene = this.currentScene;
        result.message = '灯光配置已更新';
        break;

      case 'camera':
        this.currentScene.camera = { ...this.currentScene.camera, ...params };
        result.scene = this.currentScene;
        result.message = '相机配置已更新';
        break;

      case 'status':
      default:
        result.scene = this.currentScene;
        result.message = '返回当前场景状态';
        break;
    }

    return result;
  }

  // 获取当前场景
  getScene() {
    return this.currentScene;
  }

  // 重置为默认场景
  resetScene() {
    this.currentScene = JSON.parse(JSON.stringify(this.defaultScene));
    return this.currentScene;
  }
}

// 创建 AI Agent 实例
const agent = new SimulationAgent(minimax);

// ============================================
// MCP 工具定义
// ============================================

const mcpTools = [
  {
    name: 'generate_scene',
    description: '生成新的场景配置（海洋、天气、时间）',
    inputSchema: {
      type: 'object',
      properties: {
        type: { type: 'string', enum: ['calm', 'stormy', 'sunset', 'night'] },
        waveHeight: { type: 'number' },
        waterColor: { type: 'string' }
      }
    }
  },
  {
    name: 'adjust_physics',
    description: '调整物理模拟参数',
    inputSchema: {
      type: 'object',
      properties: {
        gravity: { type: 'number' },
        waterDensity: { type: 'number' },
        linearDamping: { type: 'number' },
        angularDamping: { type: 'number' }
      }
    }
  },
  {
    name: 'control_boat',
    description: '控制3D船只模型',
    inputSchema: {
      type: 'object',
      properties: {
        boatId: { type: 'string', enum: ['boat1', 'boat2'] },
        position: { type: 'object' },
        rotation: { type: 'object' },
        scale: { type: 'number' }
      }
    }
  },
  {
    name: 'adjust_lighting',
    description: '调整场景灯光',
    inputSchema: {
      type: 'object',
      properties: {
        ambientIntensity: { type: 'number' },
        directionalIntensity: { type: 'number' },
        sunPosition: { type: 'object' }
      }
    }
  },
  {
    name: 'get_scene_status',
    description: '获取当前场景状态',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  },
  {
    name: 'reset_scene',
    description: '重置场景为默认配置',
    inputSchema: {
      type: 'object',
      properties: {}
    }
  }
];

// ============================================
// API 路由
// ============================================

// MCP 工具列表
app.get('/api/mcp/tools', (req, res) => {
  res.json({
    tools: mcpTools,
    protocol: 'mcp',
    version: '1.0.0'
  });
});

// AI 对话接口
app.post('/api/ai/chat', async (req, res) => {
  try {
    const { message } = req.body;
    
    if (!message) {
      return res.status(400).json({ error: '消息不能为空' });
    }

    const result = await agent.processRequest(message);
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 场景状态接口
app.get('/api/scene', (req, res) => {
  res.json(agent.getScene());
});

// 重置场景
app.post('/api/scene/reset', (req, res) => {
  res.json({
    success: true,
    scene: agent.resetScene(),
    message: '场景已重置为默认配置'
  });
});

// MCP 工具调用接口
app.post('/api/mcp/call', async (req, res) => {
  try {
    const { tool, parameters } = req.body;

    if (!tool) {
      return res.status(400).json({ error: '工具名称不能为空' });
    }

    let result;
    const scene = agent.getScene();

    switch (tool) {
      case 'generate_scene':
        if (parameters.type === 'calm') {
          scene.ocean = { ...scene.ocean, waveHeight: 0.3, waveSpeed: 0.5 };
        } else if (parameters.type === 'stormy') {
          scene.ocean = { ...scene.ocean, waveHeight: 5, waveSpeed: 2.5 };
        } else if (parameters.type === 'sunset') {
          scene.lighting = { ...scene.lighting, ambientIntensity: 0.3, directionalIntensity: 0.8 };
          scene.ocean.waterColor = '#ff7f50';
        } else if (parameters.type === 'night') {
          scene.lighting = { ...scene.lighting, ambientIntensity: 0.1, directionalIntensity: 0.2 };
        }
        
        if (parameters.waveHeight !== undefined) scene.ocean.waveHeight = parameters.waveHeight;
        if (parameters.waterColor) scene.ocean.waterColor = parameters.waterColor;
        
        result = { success: true, scene, message: `场景类型已切换为 ${parameters.type}` };
        break;

      case 'adjust_physics':
        scene.physics = { ...scene.physics, ...parameters };
        result = { success: true, scene, message: '物理参数已更新' };
        break;

      case 'control_boat':
        const { boatId, ...boatParams } = parameters;
        if (boatId && scene.boats[boatId]) {
          scene.boats[boatId] = { ...scene.boats[boatId], ...boatParams };
        }
        result = { success: true, scene, message: `${boatId} 模型已更新` };
        break;

      case 'adjust_lighting':
        scene.lighting = { ...scene.lighting, ...parameters };
        result = { success: true, scene, message: '灯光配置已更新' };
        break;

      case 'get_scene_status':
        result = { success: true, scene, message: '当前场景状态' };
        break;

      case 'reset_scene':
        result = { success: true, scene: agent.resetScene(), message: '场景已重置' };
        break;

      default:
        return res.status(400).json({ error: `未知工具: ${tool}` });
    }

    res.json(result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 快速预设接口
app.post('/api/scene/preset', (req, res) => {
  const { preset } = req.body;
  const scene = agent.getScene();

  const presets = {
    calm: {
      ocean: { waveHeight: 0.3, waveSpeed: 0.5, waveFrequency: 0.3 },
      physics: { linearDamping: 0.05, angularDamping: 0.1 }
    },
    stormy: {
      ocean: { waveHeight: 4, waveSpeed: 2, waveFrequency: 1.2 },
      physics: { linearDamping: 0.3, angularDamping: 0.5 }
    },
    sunset: {
      ocean: { waveHeight: 1, waveSpeed: 0.8, waterColor: '#ff6b35' },
      lighting: { ambientIntensity: 0.3, directionalIntensity: 0.7 }
    },
    night: {
      ocean: { waveHeight: 0.8, waveSpeed: 0.6, waterColor: '#001a33' },
      lighting: { ambientIntensity: 0.1, directionalIntensity: 0.2 }
    }
  };

  if (!presets[preset]) {
    return res.status(400).json({ error: `未知预设: ${preset}` });
  }

  Object.assign(scene, presets[preset]);
  res.json({ success: true, scene, message: `已应用 ${preset} 预设` });
});

// ============================================
// 健康检查
// ============================================

app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'DoubleBoat AI Native Server',
    version: '1.0.0',
    mcp: 'enabled',
    llm: 'minimax',
    model: process.env.MINIMAX_MODEL
  });
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║         🚀 DoubleBoat AI Native Server 启动完成             ║
╠════════════════════════════════════════════════════════════╣
║  服务地址: http://localhost:${PORT}                          ║
║  MCP协议:  已启用                                            ║
║  LLM:      MiniMax (${process.env.MINIMAX_MODEL})                 ║
╠════════════════════════════════════════════════════════════╣
║  API 端点:                                                  ║
║  - GET  /api/health        健康检查                         ║
║  - GET  /api/mcp/tools     MCP工具列表                      ║
║  - POST /api/mcp/call      调用MCP工具                      ║
║  - POST /api/ai/chat       AI对话                           ║
║  - GET  /api/scene         获取场景状态                     ║
║  - POST /api/scene/reset  重置场景                         ║
║  - POST /api/scene/preset 应用预设                         ║
╚════════════════════════════════════════════════════════════╝
  `);
});

export default app;
