# 🌐 Decentralized Offline-First Mesh Network Routing Engine

An offline-first, decentralized network routing and chat application built for emergency communication scenarios where internet infrastructure or cellular networks are unavailable. Developed as a Design and Analysis of Algorithms (DAA) mini-project.

---

## 🚀 Features
* **100% Offline Local Communication:** Connects mobile devices and a laptop command base over a local Wi-Fi hotspot without requiring internet data or an ISP.
* **Shortest Path Optimization:** Implements graph-based iterative edge relaxation (Bellman-Ford algorithm) to compute optimal multi-hop paths between network nodes.
* **Smart Bus / Linear Chain Topology:** Forces realistic multi-hop traversal through intermediate nodes rather than direct shortcuts.
* **Packet Fragmentation (Chunking):** Splits large message payloads into structured 4-byte packets with unique IDs and reassembles them securely at the destination.
* **WhatsApp-Styled Mobile Chat:** A responsive dark-mode web interface (`/`) for mobile users to register nodes and exchange private messages.
* **Command Base Dashboard & Live Topology Map:** A comprehensive laptop control center (`/base`) featuring active device registries, transmission logs, and an HTML5 Canvas visualizer with animated moving pulses for active path hops.

---

## 🛠️ Technologies Used
* **Backend:** Python, Flask API (`render_template_string`, `request`, `jsonify`)
* **Networking:** Python `socket` module for local IP resolution and host binding
* **Frontend:** HTML5, CSS3, JavaScript, HTML5 Canvas API (for real-time topology mapping)

---

## ⚙️ Installation & Running the Application

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/dubey-ji-coder/mesh-routing-engine.git](https://github.com/dubey-ji-coder/mesh-routing-engine.git)
   cd mesh-routing-engine
