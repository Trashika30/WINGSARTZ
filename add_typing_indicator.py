import os

CSS = """
.typing-indicator {
  background: white;
  padding: 0.8rem 1rem;
  border-radius: 0.75rem 0.75rem 0.75rem 0;
  border: 1px solid var(--blush);
  max-width: fit-content;
  display: flex;
  gap: 4px;
  align-items: center;
}
.typing-dot {
  width: 6px;
  height: 6px;
  background: var(--pink);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}
.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }
@keyframes typing {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
"""

def update_admin():
    with open('frontend/admin.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Inject CSS
    if '.typing-indicator' not in content:
        content = content.replace('</style>', CSS)

    # Inject typing indicator creation
    old_try = "  msgs.scrollTop = msgs.scrollHeight;\n\n  try {"
    new_try = """  msgs.scrollTop = msgs.scrollHeight;
  const typingId = 'typing-' + Date.now();
  msgs.innerHTML += `<div id="${typingId}" class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>`;
  msgs.scrollTop = msgs.scrollHeight;

  try {"""
    content = content.replace(old_try, new_try)

    # Remove typing indicator on success
    old_json = "const data = await res.json();"
    new_json = """const data = await res.json();
    document.getElementById(typingId)?.remove();"""
    content = content.replace(old_json, new_json)

    # Remove typing indicator on error
    old_catch = "} catch (err) {"
    new_catch = """} catch (err) {
    document.getElementById(typingId)?.remove();"""
    content = content.replace(old_catch, new_catch)

    with open('frontend/admin.html', 'w', encoding='utf-8') as f:
        f.write(content)

def update_index():
    with open('frontend/index.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Inject CSS
    if '.typing-dot' not in content:
        content = content.replace('</style>', CSS.replace('.typing-indicator {', '.typing-indicator-ignored {')) # don't need indicator class for index

    # Inject typing indicator creation
    old_try = "  msgs.scrollTop = msgs.scrollHeight;\n\n  try {"
    new_try = """  msgs.scrollTop = msgs.scrollHeight;
  const typingId = 'typing-' + Date.now();
  msgs.innerHTML += `<div class="msg bot" id="${typingId}"><div class="msg-bubble" style="display:flex;gap:4px;align-items:center;min-height:24px;"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div></div>`;
  msgs.scrollTop = msgs.scrollHeight;

  try {"""
    content = content.replace(old_try, new_try)

    # Remove typing indicator on success
    old_json = "const data = await res.json();"
    new_json = """const data = await res.json();
    document.getElementById(typingId)?.remove();"""
    content = content.replace(old_json, new_json)

    # Remove typing indicator on error
    old_catch = "} catch (err) {"
    new_catch = """} catch (err) {
    document.getElementById(typingId)?.remove();"""
    content = content.replace(old_catch, new_catch)

    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    update_admin()
    update_index()
    print("Done")
