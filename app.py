from flask import Flask, jsonify, request
import os
import json
from datetime import datetime

app = Flask(__name__)

# Simple file-based storage for now (we'll upgrade to PostgreSQL next)
DATA_FILE = 'verifications.json'

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'verifications': [], 'stats': {'total': 0, 'verified': 0, 'rejected': 0}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

@app.route('/')
def home():
    data = load_data()
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Indigenous Business Verification System</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
                color: white;
                padding: 40px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 30px;
            }}
            h1 {{
                margin: 0;
                font-size: 2.5em;
            }}
            .status-live {{
                display: inline-block;
                background: #10b981;
                padding: 8px 20px;
                border-radius: 20px;
                margin-top: 10px;
                font-weight: bold;
            }}
            .dashboard {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .stat-number {{
                font-size: 3em;
                font-weight: bold;
                margin: 10px 0;
            }}
            .stat-label {{
                color: #666;
                text-transform: uppercase;
                font-size: 0.9em;
            }}
            .verify-section {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}
            input {{
                width: 100%;
                padding: 15px;
                font-size: 18px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin: 10px 0;
                box-sizing: border-box;
            }}
            input:focus {{
                outline: none;
                border-color: #3b82f6;
            }}
            button {{
                width: 100%;
                padding: 15px;
                font-size: 18px;
                background: #1e40af;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
            }}
            button:hover {{
                background: #1e3a8a;
            }}
            .result {{
                margin-top: 20px;
                padding: 20px;
                border-radius: 8px;
                display: none;
            }}
            .result.verified {{
                background: #d1fae5;
                border: 2px solid #10b981;
            }}
            .result.rejected {{
                background: #fee2e2;
                border: 2px solid #ef4444;
            }}
            .recent-verifications {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e5e7eb;
            }}
            th {{
                background: #f9fafb;
                font-weight: bold;
            }}
            .badge {{
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.875em;
                font-weight: bold;
            }}
            .badge-verified {{
                background: #d1fae5;
                color: #065f46;
            }}
            .badge-rejected {{
                background: #fee2e2;
                color: #991b1b;
            }}
            .text-green {{ color: #10b981; }}
            .text-red {{ color: #ef4444; }}
            .text-yellow {{ color: #f59e0b; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛡️ Indigenous Business Verification System</h1>
            <p>Protecting $1.6B in procurement from phantom partnerships</p>
            <div class="status-live">🟢 SYSTEM OPERATIONAL</div>
        </div>
        
        <div class="dashboard">
            <div class="stat-card">
                <div class="stat-label">Total Verifications</div>
                <div class="stat-number text-blue">{data['stats']['total']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Verified</div>
                <div class="stat-number text-green">{data['stats']['verified']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Rejected</div>
                <div class="stat-number text-red">{data['stats']['rejected']}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Success Rate</div>
                <div class="stat-number text-yellow">{int(data['stats']['verified'] / max(data['stats']['total'], 1) * 100)}%</div>
            </div>
        </div>
        
        <div class="verify-section">
            <h2>🔍 Verify a Business</h2>
            <p>Enter a 9-digit business number to check Indigenous verification status:</p>
            
            <input type="text" 
                   id="businessNumber" 
                   placeholder="Example: 123456789" 
                   maxlength="9"
                   pattern="[0-9]{{9}}">
            
            <button onclick="verifyBusiness()">Verify Business</button>
            
            <div id="result" class="result"></div>
            
            <div style="background: #fef3c7; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <strong>🧪 Test Examples:</strong><br>
                ✅ Verified business: Any number starting with 1 (e.g., 123456789)<br>
                ❌ High risk business: Any number starting with 2 (e.g., 234567890)<br>
                🔍 Try any 9-digit number!
            </div>
        </div>
        
        <div class="recent-verifications">
            <h2>📊 Recent Verifications</h2>
            <table>
                <thead>
                    <tr>
                        <th>Business Number</th>
                        <th>Status</th>
                        <th>Risk Score</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody id="recentList">
                    {''.join([f'''
                    <tr>
                        <td>{v['business_number']}</td>
                        <td><span class="badge badge-{'verified' if v['verified'] else 'rejected'}">{v['status']}</span></td>
                        <td>{v['risk_score']}/100</td>
                        <td>{v['timestamp']}</td>
                    </tr>
                    ''' for v in data['verifications'][-5:]][::-1]) if data['verifications'] else '<tr><td colspan="4" style="text-align: center; color: #999;">No verifications yet</td></tr>'}
                </tbody>
            </table>
        </div>
        
        <div style="text-align: center; margin-top: 40px; color: #666;">
            <p>
                API Endpoint: <code style="background: #f3f4f6; padding: 4px 8px; border-radius: 4px;">/api/verify?bn=[BUSINESS_NUMBER]</code><br>
                Built by IndigeniousCA | <a href="https://github.com/indigeniousCA/indigenous-verify">GitHub</a>
            </p>
        </div>
        
        <script>
            function verifyBusiness() {{
                const bn = document.getElementById('businessNumber').value;
                const resultDiv = document.getElementById('result');
                
                if (bn.length !== 9 || !/^\d+$/.test(bn)) {{
                    alert('Please enter exactly 9 digits');
                    return;
                }}
                
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '⏳ Verifying...';
                resultDiv.className = 'result';
                
                fetch('/api/verify?bn=' + bn)
                    .then(response => response.json())
                    .then(data => {{
                        const isVerified = data.verified;
                        
                        resultDiv.className = 'result ' + (isVerified ? 'verified' : 'rejected');
                        resultDiv.innerHTML = `
                            <h3>${{isVerified ? '✅ Verification Successful' : '❌ Verification Failed'}}</h3>
                            <p><strong>Business Number:</strong> ${{data.business_number}}</p>
                            <p><strong>Status:</strong> ${{data.status}}</p>
                            <p><strong>Risk Score:</strong> ${{data.risk_score}}/100 
                                ${{data.risk_score > 70 ? '🚨 HIGH RISK' : '✅ Low Risk'}}
                            </p>
                            ${{data.phantom_risk ? '<p style="color: red; font-weight: bold;">⚠️ WARNING: Potential phantom partnership detected!</p>' : ''}}
                            <p><strong>Timestamp:</strong> ${{new Date().toLocaleString()}}</p>
                        `;
                        
                        // Reload page to update stats
                        setTimeout(() => location.reload(), 2000);
                    }})
                    .catch(error => {{
                        resultDiv.className = 'result rejected';
                        resultDiv.innerHTML = '❌ Error: Could not verify business';
                    }});
            }}
            
            document.getElementById('businessNumber').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    verifyBusiness();
                }}
            }});
        </script>
    </body>
    </html>
    '''

@app.route('/api/verify')
def verify():
    bn = request.args.get('bn', '')
    
    # Load existing data
    data = load_data()
    
    # Simple verification logic
    is_verified = bn.startswith('1')
    risk_score = 15 if is_verified else 85
    
    # Create verification record
    verification = {
        'business_number': bn,
        'status': 'VERIFIED' if is_verified else 'REJECTED',
        'risk_score': risk_score,
        'verified': is_verified,
        'phantom_risk': risk_score > 70,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'message': 'Verification complete'
    }
    
    # Update stats
    data['stats']['total'] += 1
    if is_verified:
        data['stats']['verified'] += 1
    else:
        data['stats']['rejected'] += 1
    
    # Add to verifications list
    data['verifications'].append(verification)
    
    # Keep only last 100 verifications
    if len(data['verifications']) > 100:
        data['verifications'] = data['verifications'][-100:]
    
    # Save data
    save_data(data)
    
    return jsonify(verification)

@app.route('/api/stats')
def stats():
    data = load_data()
    return jsonify({
        'stats': data['stats'],
        'recent_verifications': data['verifications'][-10:][::-1]
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'version': '2.0'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    print(f"Starting Indigenous Verify API v2.0 on port {port}")
    app.run(host='0.0.0.0', port=port)
def send_alert_email(verification):
    """Send email alert for high-risk verifications"""
    if verification['risk_score'] > 70:
        # In production, this would use SendGrid or similar
        # For now, we'll just log it
        alert = f"""
        🚨 HIGH RISK ALERT 🚨
        
        Business Number: {verification['business_number']}
        Risk Score: {verification['risk_score']}/100
        Status: {verification['status']}
        Phantom Risk: {'YES' if verification['phantom_risk'] else 'NO'}
        Time: {verification['timestamp']}
        
        Action Required: Manual review recommended
        """
        print(f"EMAIL ALERT: {alert}")
        # In real implementation, send actual email here
