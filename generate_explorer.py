import json

def generate_explorer():
    with open("chain_state.json", "r") as f:
        data = json.load(f)

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['chain_name']} Explorer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{ background-color: #f3f4f6; font-family: 'Inter', sans-serif; }}
        .glass {{ background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px); }}
        .card {{ transition: all 0.3s ease; }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }}
        .eth-gradient {{ background: linear-gradient(135deg, #627eea 0%, #4834d4 100%); }}
    </style>
</head>
<body>
    <nav class="eth-gradient text-white p-4 shadow-lg">
        <div class="container mx-auto flex justify-between items-center">
            <h1 class="text-2xl font-bold flex items-center gap-2">
                <i class="fas fa-shield-alt"></i> {data['chain_name']} Explorer
            </h1>
            <div class="flex gap-4 items-center">
                <span class="bg-white/20 px-3 py-1 rounded-full text-sm">Chain ID: {data['chain_id']}</span>
                <span class="bg-green-500 px-3 py-1 rounded-full text-sm font-bold">LIVE</span>
            </div>
        </div>
    </nav>

    <main class="container mx-auto p-6">
        <!-- Dashboard -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="glass p-6 rounded-2xl shadow-sm card border border-white">
                <p class="text-gray-500 text-sm uppercase font-semibold">Total Supply</p>
                <h2 class="text-3xl font-bold text-gray-800">1,000,000,000 T-ETH</h2>
            </div>
            <div class="glass p-6 rounded-2xl shadow-sm card border border-white">
                <p class="text-gray-500 text-sm uppercase font-semibold">Transactions</p>
                <h2 class="text-3xl font-bold text-gray-800">{len(data['transactions'])}</h2>
            </div>
            <div class="glass p-6 rounded-2xl shadow-sm card border border-white">
                <p class="text-gray-500 text-sm uppercase font-semibold">Active Contracts</p>
                <h2 class="text-3xl font-bold text-gray-800">{len(data['contracts'])}</h2>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Latest Blocks -->
            <div class="lg:col-span-2">
                <div class="glass rounded-2xl shadow-sm border border-white overflow-hidden">
                    <div class="p-4 border-b border-gray-200 bg-white/50 font-bold text-gray-700 flex items-center gap-2">
                        <i class="fas fa-cubes text-indigo-600"></i> Latest Blocks
                    </div>
                    <table class="w-full text-left">
                        <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
                            <tr>
                                <th class="p-4">Block</th>
                                <th class="p-4">Timestamp</th>
                                <th class="p-4">Hash</th>
                                <th class="p-4">Txs</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 text-sm">
                            {{{{ generateBlocks() }}}}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Top Holders -->
            <div>
                <div class="glass rounded-2xl shadow-sm border border-white overflow-hidden">
                    <div class="p-4 border-b border-gray-200 bg-white/50 font-bold text-gray-700 flex items-center gap-2">
                        <i class="fas fa-wallet text-indigo-600"></i> Top Holders
                    </div>
                    <div class="p-4 space-y-4">
                        {{{{ generateHolders() }}}}
                    </div>
                </div>
            </div>
        </div>

        <!-- Recent Transactions -->
        <div class="mt-8">
            <div class="glass rounded-2xl shadow-sm border border-white overflow-hidden">
                <div class="p-4 border-b border-gray-200 bg-white/50 font-bold text-gray-700 flex items-center gap-2">
                    <i class="fas fa-exchange-alt text-indigo-600"></i> Recent Transactions
                </div>
                <table class="w-full text-left">
                    <thead class="bg-gray-50 text-gray-500 text-xs uppercase">
                        <tr>
                            <th class="p-4">Tx Hash</th>
                            <th class="p-4">From</th>
                            <th class="p-4">To</th>
                            <th class="p-4">Value</th>
                            <th class="p-4">Type</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 text-sm">
                        {{{{ generateTxs() }}}}
                    </tbody>
                </table>
            </div>
        </div>
    </main>

    <script>
        const data = {json.dumps(data)};

        function shorten(addr) {{
            return addr.substring(0, 6) + '...' + addr.substring(addr.length - 4);
        }}

        function generateBlocks() {{
            return data.blocks.slice().reverse().map(b => `
                <tr class="hover:bg-indigo-50 transition-colors">
                    <td class="p-4 font-bold text-indigo-600">#${{b.number}}</td>
                    <td class="p-4 text-gray-500">${{b.timestamp}}</td>
                    <td class="p-4 font-mono text-xs text-gray-400">${{b.hash}}</td>
                    <td class="p-4">${{b.transactions.length}}</td>
                </tr>
            `).join('');
        }}

        function generateHolders() {{
            const sorted = Object.entries(data.balances).sort((a, b) => b[1] - a[1]);
            return sorted.slice(0, 5).map(([addr, bal]) => `
                <div class="flex justify-between items-center p-2 hover:bg-white rounded-lg transition-colors">
                    <span class="font-mono text-xs text-gray-600">${{shorten(addr)}}</span>
                    <span class="font-bold text-gray-800">${{bal.toLocaleString()}} T-ETH</span>
                </div>
            `).join('');
        }}

        function generateTxs() {{
            return data.transactions.slice().reverse().map(tx => `
                <tr class="hover:bg-indigo-50 transition-colors">
                    <td class="p-4 font-mono text-xs text-indigo-500">${{tx.hash}}</td>
                    <td class="p-4 text-gray-600">${{shorten(tx.from)}}</td>
                    <td class="p-4 text-gray-600">${{shorten(tx.to)}}</td>
                    <td class="p-4 font-bold text-gray-800">${{tx.value.toLocaleString()}} T-ETH</td>
                    <td class="p-4">
                        <span class="px-2 py-1 rounded-full text-xs font-semibold ${{tx.type === 'Transfer' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}}">
                            ${{tx.type}}
                        </span>
                    </td>
                </tr>
            `).join('');
        }}

        // Inject the generated content
        document.addEventListener('DOMContentLoaded', () => {{
            document.body.innerHTML = document.body.innerHTML.replace('{{{{ generateBlocks() }}}}', generateBlocks());
            document.body.innerHTML = document.body.innerHTML.replace('{{{{ generateHolders() }}}}', generateHolders());
            document.body.innerHTML = document.body.innerHTML.replace('{{{{ generateTxs() }}}}', generateTxs());
        }});
    </script>
</body>
</html>
"""
    with open("explorer.html", "w") as f:
        f.write(html_template)
    print("✅ Explorer generated: explorer.html")

if __name__ == "__main__":
    generate_explorer()
