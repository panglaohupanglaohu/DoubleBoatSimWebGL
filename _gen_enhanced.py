import pathlib

SRC = pathlib.Path('src/frontend/agent-team-config.html.bak')
DST = pathlib.Path('src/frontend/agent-team-config.html')
orig = SRC.read_text()

# 1. CSS additions before </style>
css_new = """
.search-box{position:relative;min-width:240px}
.search-box input{width:100%;padding:8px 14px 8px 34px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);border-radius:20px;color:#e0e0e0;font-size:13px;outline:none;transition:border-color .2s}
.search-box input:focus{border-color:#4fc3f7}
.search-box .search-icon{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:#666;font-size:14px;pointer-events:none}
.search-dropdown{position:absolute;top:100%;left:0;right:0;margin-top:6px;background:#1e1e3a;border:1px solid rgba(255,255,255,.12);border-radius:12px;max-height:380px;overflow-y:auto;z-index:500;display:none;box-shadow:0 8px 32px rgba(0,0,0,.5)}
.search-dropdown.show{display:block}
.search-group-label{padding:8px 14px;font-size:11px;color:#666;text-transform:uppercase;letter-spacing:1px;border-bottom:1px solid rgba(255,255,255,.06)}
.search-item{padding:10px 14px;cursor:pointer;font-size:13px;color:#ccc;display:flex;align-items:center;gap:10px;border-bottom:1px solid rgba(255,255,255,.04)}
.search-item:hover{background:rgba(79,195,247,.08);color:#fff}
.search-item .si-name{flex:1}.search-item .si-type{font-size:11px;color:#666}
.search-no-results{padding:20px;text-align:center;color:#555;font-size:13px}
.card-header .card-title-area{cursor:pointer;flex:1;min-width:0}.card-header .card-title-area:hover h3{color:#4fc3f7}
.btn-danger{background:linear-gradient(135deg,#ef5350 0%,#c62828 100%)}.btn-danger:hover{transform:translateY(-1px)}
.btn-warning{background:linear-gradient(135deg,#ff9800 0%,#e65100 100%)}.btn-warning:hover{transform:translateY(-1px)}
.btn-success{background:linear-gradient(135deg,#4caf50 0%,#2e7d32 100%)}.btn-success:hover{transform:translateY(-1px)}
.detail-section{margin-bottom:20px;padding:16px;background:rgba(0,0,0,.15);border-radius:10px;border:1px solid rgba(255,255,255,.06)}
.detail-section h3{font-size:14px;color:#4fc3f7;margin-bottom:12px;font-weight:600}
.detail-row{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,.04);font-size:13px}
.detail-row:last-child{border-bottom:none}
.detail-row .dl{color:#888}.detail-row .dv{color:#ddd}
.agent-detail-actions{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:20px}
.log-container{background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:12px;max-height:200px;overflow-y:auto;font-family:"SF Mono",Monaco,monospace;font-size:12px;color:#aaa;line-height:1.6}
.log-container .log-time{color:#666}.log-container .log-level-info{color:#4fc3f7}.log-container .log-level-warn{color:#ff9800}.log-container .log-level-error{color:#ef5350}
"""

orig = orig.replace('</style></head>', css_new + '</style></head>')

# Make agent-card clickable
orig = orig.replace(
    '.agent-card{display:flex;align-items:center;gap:16px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:12px;padding:16px 20px;transition:all .15s}',
    '.agent-card{display:flex;align-items:center;gap:16px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:12px;padding:16px 20px;transition:all .15s;cursor:pointer}'
)

# Fix responsive for search
orig = orig.replace(
    '@media(max-width:768px){.header{padding:12px 16px}',
    '@media(max-width:768px){.header{padding:12px 16px;flex-wrap:wrap}'
)

print('CSS modifications done')

# 2. Add search box in header (after badge, before spacer)
orig = orig.replace(
    '  <span class="badge">PoseidonX</span>\n  <div style="flex:1"></div>',
    '  <span class="badge">PoseidonX</span>\n  <div class="search-box">\n    <span class="search-icon">&#x1F50D;</span>\n    <input type="text" id="globalSearchInput" placeholder="\u641c\u7d22\u56e2\u961f\u3001\u667a\u80fd\u4f53\u3001\u5de5\u5177\u3001\u6280\u80fd..." autocomplete="off">\n    <div class="search-dropdown" id="searchDropdown"></div>\n  </div>\n  <div style="flex:1"></div>'
)
print('Search box added')

# 3. Add team-selector to skills panel
orig = orig.replace(
    '<div class="tab-panel" id="panel-skills">\n  <h2 class="section-title">\u6280\u80fd\u76ee\u5f55</h2>',
    '<div class="tab-panel" id="panel-skills">\n  <div class="team-selector"><label>\u5f53\u524d\u56e2\u961f:</label><select id="skillTeamSelect" onchange="onTeamSelectChange(\'skills\')"></select></div>\n  <h2 class="section-title">\u6280\u80fd\u76ee\u5f55</h2>'
)
print('Skill team selector added')

DST.write_text(orig)
print(f'Intermediate file written: {len(orig.splitlines())} lines')
