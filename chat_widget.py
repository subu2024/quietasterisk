"""
AI Chat widget HTML generator for AWS Lambda integration.
"""

from config import (
    ENABLE_AI_CHAT, 
    AI_CHAT_TITLE, 
    AI_CHAT_PLACEHOLDER,
    AWS_API_ENDPOINT,
    AWS_API_TOKEN
)


def get_chat_widget_html() -> str:
    """Generate AI chat widget HTML with JavaScript for AWS Lambda."""
    if not ENABLE_AI_CHAT:
        return ""
    
    return f"""
<section class="section" style="background: var(--color-sand); padding: 4rem 0;">
  <div class="container" style="max-width: 48rem;">
    <div style="background: white; border: 2px solid var(--color-rust); border-radius: 8px; padding: 2rem;">
      <h3 style="font-family: var(--font-serif); font-size: 1.75rem; margin-bottom: 1rem; color: var(--color-charcoal);">
        {AI_CHAT_TITLE}
      </h3>
      <p style="color: var(--color-slate); margin-bottom: 1.5rem; font-size: 0.875rem;">
        Ask questions on uncertainity that matter to you. 
      </p>
      
      <div id="chat-messages" style="max-height: 400px; overflow-y: auto; margin-bottom: 1rem; padding: 1rem; background: var(--color-cream); border-radius: 4px; display: none;">
      </div>
      
      <div style="display: flex; gap: 0.5rem;">
        <input 
          type="text" 
          id="chat-input" 
          placeholder="{AI_CHAT_PLACEHOLDER}"
          style="flex: 1; padding: 0.75rem; border: 2px solid var(--color-sand); border-radius: 4px; font-family: var(--font-sans); font-size: 1rem;"
          onkeypress="if(event.key === 'Enter') sendMessage()"
        />
        <button 
          id="send-btn"
          onclick="sendMessage()"
          style="padding: 0.75rem 2rem; background: var(--color-rust); color: white; border: none; border-radius: 4px; cursor: pointer; font-family: var(--font-sans); font-weight: 500; transition: background 0.3s;"
          onmouseover="this.style.background='#A03D2F'"
          onmouseout="this.style.background='var(--color-rust)'"
        >
          Send
        </button>
      </div>
      
      <div id="error-message" style="margin-top: 1rem; padding: 0.75rem; background: #fee; border-left: 4px solid var(--color-rust); border-radius: 4px; display: none; font-size: 0.875rem;">
      </div>
    </div>
  </div>
</section>

<script>
const AWS_API_ENDPOINT = '{AWS_API_ENDPOINT}';
const AWS_API_TOKEN = '{AWS_API_TOKEN}';

async function sendMessage() {{
  const input = document.getElementById('chat-input');
  const messagesDiv = document.getElementById('chat-messages');
  const sendBtn = document.getElementById('send-btn');
  const errorDiv = document.getElementById('error-message');
  
  const message = input.value.trim();
  if (!message) return;
  
  // Hide error
  errorDiv.style.display = 'none';
  
  // Show messages container
  messagesDiv.style.display = 'block';
  
  // Add user message
  const userMessageDiv = document.createElement('div');
  userMessageDiv.style.cssText = 'margin-bottom: 1.5rem; text-align: right;';
  userMessageDiv.innerHTML = `
    <div style="display: inline-block; max-width: 80%; background: var(--color-rust); color: white; padding: 0.75rem 1rem; border-radius: 12px; text-align: left;">
      <strong>You:</strong><br/>
      ${{message}}
    </div>
  `;
  messagesDiv.appendChild(userMessageDiv);
  
  input.value = '';
  sendBtn.disabled = true;
  sendBtn.textContent = 'Thinking...';
  
  // Add loading indicator
  const loadingDiv = document.createElement('div');
  loadingDiv.id = 'loading-indicator';
  loadingDiv.style.cssText = 'margin-bottom: 1.5rem;';
  loadingDiv.innerHTML = `
    <div style="display: inline-block; max-width: 80%; background: white; border: 2px solid var(--color-sand); padding: 0.75rem 1rem; border-radius: 12px;">
      <strong style="color: var(--color-rust);">Claude:</strong><br/>
      <span style="color: var(--color-slate);">Thinking...</span>
    </div>
  `;
  messagesDiv.appendChild(loadingDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
  
  try {{
    const response = await fetch(AWS_API_ENDPOINT, {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${{AWS_API_TOKEN}}`
      }},
      body: JSON.stringify({{
        message: message
      }})
    }});
    
    // Remove loading indicator
    loadingDiv.remove();
    
    if (!response.ok) {{
      throw new Error(`API request failed: ${{response.status}} ${{response.statusText}}`);
    }}
    
    const data = await response.json();
    
    if (data.response || data.message || data.reply) {{
      const reply = data.response || data.message || data.reply;
      
      const assistantMessageDiv = document.createElement('div');
      assistantMessageDiv.style.cssText = 'margin-bottom: 1.5rem;';
      assistantMessageDiv.innerHTML = `
        <div style="display: inline-block; max-width: 80%; background: white; border: 2px solid var(--color-sand); padding: 0.75rem 1rem; border-radius: 12px;">
          <strong style="color: var(--color-rust);">Claude:</strong><br/>
          ${{reply}}
        </div>
      `;
      messagesDiv.appendChild(assistantMessageDiv);
    }} else {{
      throw new Error('No response from API');
    }}
  }} catch (error) {{
    // Remove loading indicator if still present
    const loading = document.getElementById('loading-indicator');
    if (loading) loading.remove();
    
    console.error('Error:', error);
    
    errorDiv.innerHTML = `<strong>Error:</strong> Unable to get response. ${{error.message}}`;
    errorDiv.style.display = 'block';
    
    const errorMessageDiv = document.createElement('div');
    errorMessageDiv.style.cssText = 'margin-bottom: 1.5rem;';
    errorMessageDiv.innerHTML = `
      <div style="display: inline-block; max-width: 80%; background: #fee; border: 2px solid var(--color-rust); padding: 0.75rem 1rem; border-radius: 12px;">
        <strong style="color: var(--color-rust);">Error:</strong><br/>
        Unable to get response. Please try again.
      </div>
    `;
    messagesDiv.appendChild(errorMessageDiv);
  }} finally {{
    sendBtn.disabled = false;
    sendBtn.textContent = 'Send';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }}
}}

// Allow clearing chat
function clearChat() {{
  const messagesDiv = document.getElementById('chat-messages');
  messagesDiv.innerHTML = '';
  messagesDiv.style.display = 'none';
}}
</script>
"""