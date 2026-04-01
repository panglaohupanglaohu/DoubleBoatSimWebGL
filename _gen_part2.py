import pathlib

DST = pathlib.Path('src/frontend/agent-team-config.html')
orig = DST.read_text()

# Add new modals before agentWizardModal
new_modals = """
<!-- Edit Team Modal -->
<div class="modal-overlay" id="editTeamModal">
  <div class="modal">
    <button class="modal-close" onclick="closeModal('editTeamModal')">&times;</button>
    <h2>编辑团队</h2>
    <input type="hidden" id="editTeamId">
    <div class="form-group"><label>团队名称 *</label><input id="editTeamName" placeholder="团队名称" maxlength="128"></div>
    <div class="form-group"><label>描述</label><textarea id="editTeamDesc" placeholder="团队描述..." rows="3"></textarea></div>
    <div class="modal-actions"><button class="btn btn-ghost" onclick="closeModal('editTeamModal')">取消</button><button class="btn" onclick="saveTeamEdit()">保存</button></div>
  </div>
</div>
<!-- Edit Model Modal -->
<div class="modal-overlay" id="editModelModal">
  <div class="modal">
    <button class="modal-close" onclick="closeModal('editModelModal')">&times;</button>
    <h2>编辑模型</h2>
    <input type="hidden" id="editModelId">
    <div class="form-group"><label>Provider</label><select id="editModelProvider"><option value="anthropic">Anthropic</option><option value="openai">OpenAI</option><option value="google">Google</option><option value="mistral">Mistral</option><option value="local">Local</option></select></div>
    <div class="form-group"><label>模型名称</label><input id="editModelName"></div>
    <div class="form-group"><label>Max Tokens</label><div class="slider-group"><input type="range" id="editModelTokens" min="1024" max="200000" step="1024" value="8192" oninput="document.getElementById('editTokensVal').textContent=this.value"><span class="slider-val" id="editTokensVal">8192</span></div></div>
    <div class="form-group"><label>Temperature</label><div class="slider-group"><input type="range" id="editModelTemp" min="0" max="2" step="0.05" value="0.7" oninput="document.getElementById('editTempVal').textContent=parseFloat(this.value).toFixed(2)"><span class="slider-val" id="editTempVal">0.70</span></div></div>
    <div class="form-group" style="display:flex;align-items:center;gap:10px"><label style="margin:0">默认模型</label><div class="toggle" id="editModelDefault" onclick="this.classList.toggle('on')"></div></div>
    <div class="modal-actions"><button class="btn btn-ghost" onclick="closeModal('editModelModal')">取消</button><button class="btn" onclick="saveModelEdit()">保存</button></div>
  </div>
</div>
<!-- Agent Detail Modal -->
<div class="modal-overlay" id="agentDetailModal">
  <div class="modal" style="max-width:720px">
    <button class="modal-close" onclick="closeModal('agentDetailModal')">&times;</button>
    <h2 id="agentDetailTitle">智能体详情</h2>
    <div class="agent-detail-actions" id="agentDetailActions"></div>
    <div id="agentDetailContent"></div>
    <div class="detail-section" id="agentLogsSection" style="display:none">
      <h3>&#x1F4DC; 运行日志</h3>
      <div class="log-container" id="agentLogsContainer"></div>
    </div>
  </div>
</div>
<!-- Edit Agent Modal -->
<div class="modal-overlay" id="editAgentModal">
  <div class="modal" style="max-width:700px">
    <button class="modal-close" onclick="closeModal('editAgentModal')">&times;</button>
    <h2>编辑智能体</h2>
    <input type="hidden" id="editAgentId">
    <div class="form-group"><label>名称 *</label><input id="editAgentName" placeholder="智能体名称"></div>
    <div class="form-row">
      <div class="form-group"><label>角色</label><input id="editAgentRole" placeholder="角色"></div>
      <div class="form-group"><label>模板类型</label><select id="editAgentTemplate"><option value="custom">自定义</option><option value="researcher">研究员</option><option value="developer">开发者</option><option value="analyst">分析师</option><option value="navigator">导航员</option><option value="engineer">工程师</option><option value="coordinator">协调员</option></select></div>
    </div>
    <div class="form-group"><label>描述</label><textarea id="editAgentDesc" placeholder="智能体描述..." rows="2"></textarea></div>
    <div class="form-group"><label>关联模型</label><select id="editAgentModelId"><option value="">-- 未指定 --</option></select></div>
    <div class="form-group"><label>System Prompt</label><textarea id="editAgentSysPrompt" placeholder="系统提示词..." rows="4"></textarea></div>
    <div class="modal-actions"><button class="btn btn-ghost" onclick="closeModal('editAgentModal')">取消</button><button class="btn" onclick="saveAgentEdit()">保存</button></div>
  </div>
</div>
"""

orig = orig.replace(
    '<div class="modal-overlay" id="agentWizardModal">',
    new_modals + '<div class="modal-overlay" id="agentWizardModal">'
)

DST.write_text(orig)
print(f'Modals added. Lines: {len(orig.splitlines())}')
