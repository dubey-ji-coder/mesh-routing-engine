import socket
from flask import Flask, render_template_string, request, jsonify
app = Flask(__name__)
registered_nodes = {}
live_transmission_logs = []
chat_messages = []
class MeshRoutingEngine:
    def get_dynamic_graph(self):
        base_name = socket.gethostname() + "_Laptop_Base"
        node_list = list(registered_nodes.keys())
        all_nodes = [base_name] + node_list
        
        # Smart Mesh Bus Topology: Base connects to chain, nodes form a natural sequential link
        graph = {node: {} for node in all_nodes}
        if len(all_nodes) >= 2:
            for i in range(len(all_nodes) - 1):
                u = all_nodes[i]
                v = all_nodes[i+1]
                graph[u][v] = 2
                graph[v][u] = 2
        return graph

    def bellman_ford(self, source, destination):
        graph = self.get_dynamic_graph()
        nodes = list(graph.keys())
        if source not in nodes or destination not in nodes:
            return None, "Invalid Source or Destination Node!"
        distances = {node: float('inf') for node in nodes}
        predecessors = {node: None for node in nodes}
        distances[source] = 0
        for _ in range(len(nodes) - 1):
            for u in graph:
                for v, weight in graph[u].items():
                    if distances[u] + weight < distances[v]:
                        distances[v] = distances[u] + weight
                        predecessors[v] = u
        path = []
        curr = destination
        while curr is not None:
            path.insert(0, curr)
            curr = predecessors[curr]
        if distances[destination] == float('inf'):
            return None, "Destination unreachable or node offline!"
        return path, distances[destination]

    def packetize(self, message, chunk_size=4):
        chunks = [message[i:i+chunk_size] for i in range(0, len(message), chunk_size)]
        return [{"packet_id": i+1, "total": len(chunks), "payload": c} for i, c in enumerate(chunks)]

router = MeshRoutingEngine()

#chat interface (frontend)
VISITOR_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MeshNet Secure Chat</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #0b141a; color: #e9edef; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .phone-frame { width: 100%; max-width: 480px; height: 100vh; background: #111b21; display: flex; flex-direction: column; border-left: 1px solid #222d34; border-right: 1px solid #222d34; box-shadow: 0 0 20px rgba(0,0,0,0.8); }
        .wa-header { background: #202c33; padding: 12px 15px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #222d34; }
        .wa-title { font-size: 16px; font-weight: bold; color: #e9edef; }
        .wa-subtitle { font-size: 11px; color: #8696a0; }
        .reg-screen { padding: 30px 20px; display: flex; flex-direction: column; justify-content: center; height: 100%; text-align: center; }
        .reg-screen h2 { color: #00a884; margin-bottom: 10px; }
        .reg-screen input { width: 100%; padding: 12px; margin-bottom: 15px; background: #2a3942; border: none; color: #fff; border-radius: 8px; font-size: 14px; box-sizing: border-box; outline: none; }
        .wa-btn { background: #00a884; color: #fff; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; font-size: 14px; }
        .chat-body { flex: 1; background: #0b141a; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .chat-bubble { max-width: 75%; padding: 10px 12px; border-radius: 8px; font-size: 13px; line-height: 1.4; word-wrap: break-word; box-shadow: 0 1px 0.5px rgba(0,0,0,0.3); }
        .bubble-sent { background: #005c4b; align-self: flex-end; border-top-right-radius: 0; }
        .bubble-recv { background: #202c33; align-self: flex-start; border-top-left-radius: 0; }
        .meta-info { font-size: 10px; color: #8696a0; margin-top: 4px; display: block; text-align: right; font-family: monospace; }
        .route-badge { background: rgba(0,0,0,0.3); color: #34d399; padding: 2px 6px; border-radius: 4px; font-size: 10px; display: inline-block; margin-top: 4px; }
        .wa-footer-box { background: #202c33; padding: 10px 15px; display: flex; flex-direction: column; gap: 8px; border-top: 1px solid #222d34; }
        .wa-row { display: flex; gap: 8px; align-items: center; }
        .wa-footer-box select, .wa-footer-box input { background: #2a3942; border: none; color: #fff; padding: 10px; border-radius: 8px; font-size: 13px; outline: none; }
        .wa-footer-box select { width: 40%; }
        .wa-footer-box input { flex: 1; }
        .send-icon-btn { background: #00a884; color: white; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 16px; }
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div class="phone-frame">
        <div class="wa-header">
            <div>
                <div class="wa-title">MeshNet Secure Chat</div>
                <div class="wa-subtitle" id="statusSub">Online Node</div>
            </div>
            <div id="userBadge" style="font-size: 11px; background: #005c4b; padding: 3px 8px; border-radius: 12px; color: #34d399;">Offline</div>
        </div>

        <div id="regContainer" class="reg-screen">
            <h2>Join Mesh Chat</h2>
            <p style="color: #8696a0; font-size: 13px; margin-bottom: 20px;">Enter your name to start messaging peers.</p>
            <input type="text" id="deviceName" placeholder="e.g. Poco">
            <button class="wa-btn" onclick="registerVisitor()">Connect</button>
        </div>

        <div id="chatContainer" class="hidden" style="display: flex; flex-direction: column; height: calc(100vh - 65px);">
            <div id="chatBody" class="chat-body"></div>
            <div class="wa-footer-box">
                <div class="wa-row">
                    <select id="targetDest">
                        <option value="">Recipient</option>
                    </select>
                    <input type="text" id="msgPayload" placeholder="Type a message..." onkeypress="if(event.key === 'Enter') sendChatMessage()">
                    <button class="send-icon-btn" onclick="sendChatMessage()">➤</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let myUsername = "";

        async function registerVisitor() {
            const name = document.getElementById('deviceName').value;
            if(!name) return alert("Enter name!");
            const res = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: name})
            });
            const data = await res.json();
            if(data.success) {
                myUsername = name;
                document.getElementById('regContainer').classList.add('hidden');
                document.getElementById('chatContainer').classList.remove('hidden');
                document.getElementById('userBadge').innerText = myUsername;
                document.getElementById('statusSub').innerText = "Connected";
                fetchChatData();
                setInterval(fetchChatData, 2000);
            }
        }

        async function fetchChatData() {
            try {
                const res = await fetch('/api/chat_data');
                const data = await res.json();

                let options = `<option value="${data.base_name}">${data.base_name} (Base)</option>`;
                for(let [name, info] of Object.entries(data.nodes)) {
                    if(name !== myUsername) {
                        options += `<option value="${name}">${name}</option>`;
                    }
                }
                const curDest = document.getElementById('targetDest').value;
                document.getElementById('targetDest').innerHTML = options;
                if(curDest) document.getElementById('targetDest').value = curDest;

                let chatHTML = '';
                data.messages.forEach(m => {
                    if(m.source === myUsername || m.destination === myUsername) {
                        let isSent = (m.source === myUsername);
                        chatHTML += `<div class="chat-bubble ${isSent ? 'bubble-sent' : 'bubble-recv'}">
                            <div style="font-size:10px; color:${isSent ? '#a7f3d0' : '#38bdf8'}; font-weight:bold;">${m.source} ➔ ${m.destination}</div>
                            <div><b>Msg:</b> ${m.message}</div>
                            <div class="route-badge">🗺️ Route: ${m.path.join(' ➔ ')}</div>
                        </div>`;
                    }
                });
                const body = document.getElementById('chatBody');
                body.innerHTML = chatHTML || `<div style="text-align:center; color:#8696a0; margin-top:50px; font-size:12px;">No messages yet.</div>`;
                body.scrollTop = body.scrollHeight;
            } catch(e) {}
        }

        async function sendChatMessage() {
            const dst = document.getElementById('targetDest').value;
            const msg = document.getElementById('msgPayload').value;
            if(!dst || !msg) return alert("Select recipient and enter message!");

            const res = await fetch('/api/mobile_send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({source: myUsername, destination: dst, message: msg})
            });
            const data = await res.json();
            if(data.success) {
                document.getElementById('msgPayload').value = "";
                fetchChatData();
            }
        }
    </script>
</body>
</html>
"""

# --- LAPTOP COMMAND BASE DASHBOARD ---
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MeshNet Command Base</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #090d16; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 1350px; margin: auto; background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 15px 30px rgba(0,0,0,0.6); }
        h1 { color: #38bdf8; font-size: 22px; margin-bottom: 3px; }
        p.subtitle { color: #94a3b8; font-size: 12px; margin-bottom: 15px; }
        .main-grid { display: grid; grid-template-columns: 1fr 1fr 340px; gap: 15px; }
        .section { background: #0f172a; padding: 12px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 12px; }
        label { display: block; font-size: 11px; color: #94a3b8; margin-bottom: 4px; font-weight: bold; }
        select, textarea, input { width: 100%; padding: 7px; margin-bottom: 8px; background: #1e293b; border: 1px solid #475569; color: #fff; border-radius: 6px; box-sizing: border-box; font-size: 12px; }
        button { background: #0284c7; color: white; border: none; padding: 8px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; font-size: 12px; }
        button:hover { background: #0ea5e9; }
        .danger-btn { background: #dc2626; padding: 3px 6px; font-size: 10px; width: auto; }
        .log-box { background: #090d16; padding: 10px; border-radius: 6px; border-left: 3px solid #38bdf8; font-family: monospace; white-space: pre-wrap; font-size: 11px; height: 240px; overflow-y: auto; color: #34d399; }
        .device-card { background: #1e293b; border: 1px solid #334155; padding: 6px 10px; border-radius: 6px; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center; font-size: 11px; }
        .minimap-container { background: #0b141a; border: 1px solid #38bdf8; border-radius: 8px; height: 480px; position: relative; overflow: hidden; display: flex; flex-direction: column; align-items: center; justify-content: center; }
        canvas { background: #0b141a; display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>MeshNet: Command Base Station</h1>
        <p class="subtitle">Server IP: {{ host_ip }} | Bellman-Ford Shortest Path Routing</p>
        
        <div class="main-grid">
            <div>
                <div class="section">
                    <h3>Active Device Registry</h3>
                    <div id="deviceList" style="max-height: 140px; overflow-y: auto;">Scanning nodes...</div>
                </div>

                <div class="section">
                    <h3>Manual Routing Simulation</h3>
                    <label>Source Node:</label>
                    <select id="srcNode"></select>
                    <label>Destination Node:</label>
                    <select id="dstNode"></select>
                    <label>Message Payload:</label>
                    <textarea id="msgPayload" rows="2">SOS_TEST</textarea>
                    <button onclick="simulateManualRoute()">Compute Shortest Path & Transmit</button>
                </div>
            </div>

            <div>
                <div class="section" style="height: 100%;">
                    <h3>Live Packet Chunks & Feed</h3>
                    <div id="liveLogs" class="log-box">[SYSTEM READY] Monitoring transmissions...</div>
                </div>
            </div>

            <div>
                <div class="section" style="height: 100%; display: flex; flex-direction: column;">
                    <h3 style="margin-bottom: 8px;">Topology & Hop Animation</h3>
                    <div class="minimap-container">
                        <canvas id="topologyCanvas" width="310" height="430"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let dashOffset = 0;

        async function fetchDashboardData() {
            try {
                const res = await fetch('/api/dashboard_data');
                const data = await res.json();
                
                let html = '';
                let srcOpts = `<option value="${data.base_name}">${data.base_name} (Base)</option>`;
                let dstOpts = `<option value="${data.base_name}">${data.base_name} (Base)</option>`;

                for (let [name, info] of Object.entries(data.nodes)) {
                    html += `<div class="device-card">
                        <span>📱 <b>${name}</b><br><small style="color:#94a3b8;">IP: ${info.ip}</small></span>
                        <button class="danger-btn" onclick="unregisterDevice('${name}')">Unregister</button>
                    </div>`;
                    srcOpts += `<option value="${name}">${name}</option>`;
                    dstOpts += `<option value="${name}">${name}</option>`;
                }
                document.getElementById('deviceList').innerHTML = html || "<span style='color:#94a3b8; font-size:11px;'>No nodes connected.</span>";

                const srcSel = document.getElementById('srcNode');
                const dstSel = document.getElementById('dstNode');
                const curSrc = srcSel.value;
                const curDst = dstSel.value;
                srcSel.innerHTML = srcOpts;
                dstSel.innerHTML = dstOpts;
                if(curSrc) srcSel.value = curSrc;
                if(curDst) dstSel.value = curDst;

                let logText = "";
                if(data.logs.length === 0) {
                    logText = "[SYSTEM READY] Waiting for data exchange...";
                } else {
                    data.logs.forEach(l => {
                        logText += `------------------------------------\n`;
                        logText += `[EVENT] ${l.source} ➔ ${l.destination}\n`;
                        logText += `Path Hops: ${l.path.join(' ➔ ')} | Cost: ${l.cost}ms\n`;
                        logText += `Msg: "${l.message}"\n`;
                        l.chunks.forEach(c => {
                            logText += `  ↳ [#${c.packet_id}/${c.total}] [${c.payload}]\n`;
                        });
                    });
                }
                document.getElementById('liveLogs').innerText = logText;

                window.latestLogs = data.logs;
                window.latestNodes = data.nodes;
                window.baseName = data.base_name;
                window.graphEdges = data.graph_edges;

            } catch(e) {}
        }

        function renderBusMapLoop() {
            const canvas = document.getElementById('topologyCanvas');
            if(canvas) {
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                let baseName = window.baseName || "Base";
                let nodes = window.latestNodes || {};
                let logs = window.latestLogs || [];
                let edges = window.graphEdges || {};

                let allNodes = [baseName];
                for(let name in nodes) allNodes.push(name);

                let startY = 40;
                let stepY = canvas.height / (allNodes.length + 1);
                let nodeCoords = {};

                allNodes.forEach((name, idx) => {
                    let x = canvas.width / 2;
                    let y = startY + (idx + 1) * stepY;
                    nodeCoords[name] = {x: x, y: y};
                });

                // Draw static grey edges
                ctx.strokeStyle = '#334155';
                ctx.lineWidth = 2;
                if(edges) {
                    for(let u in edges) {
                        for(let v in edges[u]) {
                            let p1 = nodeCoords[u];
                            let p2 = nodeCoords[v];
                            if(p1 && p2) {
                                ctx.beginPath();
                                ctx.moveTo(p1.x, p1.y);
                                ctx.lineTo(p2.x, p2.y);
                                ctx.stroke();
                            }
                        }
                    }
                }

                // Animate ONLY the exact shortest path hops from the latest message!
                if(logs.length > 0) {
                    let latestPath = logs[0].path;
                    dashOffset -= 2;

                    ctx.strokeStyle = '#34d399';
                    ctx.lineWidth = 4;
                    ctx.setLineDash([6, 6]);
                    ctx.lineDashOffset = dashOffset;

                    for(let k=0; k<latestPath.length-1; k++) {
                        let p1 = nodeCoords[latestPath[k]];
                        let p2 = nodeCoords[latestPath[k+1]];
                        if(p1 && p2) {
                            ctx.beginPath();
                            ctx.moveTo(p1.x, p1.y);
                            ctx.lineTo(p2.x, p2.y);
                            ctx.stroke();
                        }
                    }
                    ctx.setLineDash([]);
                }

                // Draw Nodes
                for(let name in nodeCoords) {
                    let pt = nodeCoords[name];
                    ctx.beginPath();
                    ctx.arc(pt.x, pt.y, 16, 0, 2 * Math.PI);
                    ctx.fillStyle = (name === baseName) ? '#0284c7' : '#00a884';
                    ctx.fill();
                    ctx.lineWidth = 2;
                    ctx.strokeStyle = '#fff';
                    ctx.stroke();

                    ctx.fillStyle = '#f8fafc';
                    ctx.font = '11px sans-serif';
                    ctx.textAlign = 'left';
                    ctx.fillText(name, pt.x + 24, pt.y + 4);
                }
            }
            requestAnimationFrame(renderBusMapLoop);
        }

        async function unregisterDevice(name) {
            await fetch('/api/unregister', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: name})
            });
            fetchDashboardData();
        }

        async function simulateManualRoute() {
            const src = document.getElementById('srcNode').value;
            const dst = document.getElementById('dstNode').value;
            const msg = document.getElementById('msgPayload').value;
            if(!src || !dst || !msg) return alert("Fill all fields!");

            const res = await fetch('/api/route', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({source: src, destination: dst, message: msg})
            });
            const data = await res.json();
            if(data.success) fetchDashboardData();
        }

        setInterval(fetchDashboardData, 2000);
        window.onload = () => {
            fetchDashboardData();
            requestAnimationFrame(renderBusMapLoop);
        };
    </script>
</body>
</html>
"""

@app.route('/')
def visitor_view():
    return render_template_string(VISITOR_TEMPLATE)

@app.route('/base')
def base_view():
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"
    return render_template_string(BASE_TEMPLATE, host_ip=local_ip)

@app.route('/api/registry', methods=['GET'])
def get_registry():
    hostname = socket.gethostname()
    return jsonify({"base_name": hostname + "_Laptop_Base", "nodes": registered_nodes})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    if not name: return jsonify({"success": False})
    registered_nodes[name] = {"ip": request.remote_addr, "status": "Active"}
    return jsonify({"success": True})

@app.route('/api/unregister', methods=['POST'])
def unregister():
    data = request.get_json()
    name = data.get('name')
    if name in registered_nodes: del registered_nodes[name]
    return jsonify({"success": True})

@app.route('/api/route', methods=['POST'])
def route():
    data = request.get_json()
    src, dst, msg = data.get('source'), data.get('destination'), data.get('message')
    path, cost = router.bellman_ford(src, dst)
    if not path: return jsonify({"success": False, "error": cost})
    chunks = router.packetize(msg, chunk_size=4)
    
    log_entry = {"source": src, "destination": dst, "path": path, "cost": cost, "message": msg, "chunks": chunks}
    live_transmission_logs.insert(0, log_entry)
    chat_messages.insert(0, log_entry)
    return jsonify({"success": True, "path": path, "cost": cost, "chunks": chunks})

@app.route('/api/mobile_send', methods=['POST'])
def mobile_send():
    data = request.get_json()
    src, dst, msg = data.get('source'), data.get('destination'), data.get('message')
    path, cost = router.bellman_ford(src, dst)
    if not path: return jsonify({"success": False, "error": cost})
    chunks = router.packetize(msg, chunk_size=4)
    
    log_entry = {"source": src, "destination": dst, "path": path, "cost": cost, "message": msg, "chunks": chunks}
    live_transmission_logs.insert(0, log_entry)
    chat_messages.insert(0, log_entry)
    return jsonify({"success": True, "path": path, "cost": cost, "chunks": chunks})

@app.route('/api/chat_data', methods=['GET'])
def chat_data():
    hostname = socket.gethostname()
    return jsonify({"base_name": hostname + "_Laptop_Base", "nodes": registered_nodes, "messages": chat_messages})

@app.route('/api/dashboard_data', methods=['GET'])
def dashboard_data():
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"
    return jsonify({
        "base_name": hostname + "_Laptop_Base", 
        "base_ip": local_ip, 
        "nodes": registered_nodes, 
        "logs": live_transmission_logs,
        "graph_edges": router.get_dynamic_graph()
    })

if __name__ == '__main__':
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = "127.0.0.1"
    print(f"\nLAPTOP BASE: http://{local_ip}:5000/base")
    print(f"VISITOR CHAT: http://{local_ip}:5000/\n")
    app.run(host='0.0.0.0', port=5000, debug=True)