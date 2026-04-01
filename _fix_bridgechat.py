import pathlib
F = "/Users/panglaohu/Downloads/DoubleBoatClawSystem/src/frontend/digital-twin/layer1-interface/BridgeChat.js"
p = pathlib.Path(F)
lines = p.read_text().split(chr(10))
print("Total lines:", len(lines))
# Verify lines 404-409 (0-indexed 403-408)
assert "_callLLM(message, menuResult.executed" in lines[403], "Line 404 mismatch: " + repr(lines[403])
assert "let displayContent = response.content" in lines[404], "Line 405 mismatch"
assert "if (menuResult.executed)" in lines[405], "Line 406 mismatch"
print("Assertions passed - lines match expected bug pattern")
# Build replacement lines
chk = chr(9989)
yz = chr(24050)+chr(25191)+chr(34892)+chr(65306)
SQ = chr(39)
new_lines = []
new_lines.append("      // If menu action executed, skip LLM and return immediately")
new_lines.append("      if (menuResult.executed) {")
new_lines.append("        this._removeMessage(thinkingId);")
new_lines.append("        this._addMessage(" + SQ + "assistant" + SQ + ", " + SQ + chk + " " + yz + SQ + " + menuResult.label);")
new_lines.append("        this.conversationHistory.push({ role: " + SQ + "assistant" + SQ + ", content: " + SQ + yz + SQ + " + menuResult.label, timestamp: new Date().toISOString() });")
new_lines.append("        this.emit(" + SQ + "message:sent" + SQ + ", { message, response: { source: " + SQ + "menu-action" + SQ + ", label: menuResult.label } });")
new_lines.append("        return;")
new_lines.append("      }")
new_lines.append("")
new_lines.append("      const response = await this._callLLM(message, null);")
new_lines.append("      let displayContent = response.content;")
# Replace lines 404-409 (0-indexed 403-408) with new_lines
result = lines[:403] + new_lines + lines[409:]
p.write_text(chr(10).join(result))
print("Fix applied! New line count:", len(result))
