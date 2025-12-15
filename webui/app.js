// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove active class from all tabs
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        // Add active to clicked tab
        tab.classList.add('active');

        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });

        // Show selected tab content
        const tabName = tab.dataset.tab;
        document.getElementById(`${tabName}-tab`).classList.remove('hidden');
    });
});

// LLM Provider
document.getElementById('llm-send').addEventListener('click', async () => {
    const provider = document.getElementById('provider').value;
    const message = document.getElementById('llm-message').value;
    const button = document.getElementById('llm-send');
    const responseDiv = document.getElementById('llm-response');

    if (!message.trim()) {
        showResponse(responseDiv, 'Please enter a message', true);
        return;
    }

    button.disabled = true;
    button.innerHTML = '<span class="loading"></span> Sending...';
    responseDiv.innerHTML = '';

    try {
        let response;

        if (provider === 'anthropic') {
            response = await fetch('http://localhost:3000/anthropic/v1/messages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'anthropic-version': '2023-06-01'
                },
                body: JSON.stringify({
                    model: 'claude-haiku-4-5-20251001',
                    max_tokens: 500,
                    messages: [{ role: 'user', content: message }]
                })
            });

            const data = await response.json();
            if (data.content && data.content[0]) {
                showResponse(responseDiv, data.content[0].text);
            } else if (data.error) {
                showResponse(responseDiv, `Error: ${data.error.message}`, true);
            }
        } else {
            // OpenAI-compatible format for OpenAI, xAI, and Gemini
            const endpoints = {
                openai: 'http://localhost:3000/openai/v1/chat/completions',
                xai: 'http://localhost:3000/xai/v1/chat/completions',
                gemini: 'http://localhost:3000/gemini/v1/chat/completions'
            };

            const models = {
                openai: 'gpt-4o-mini',
                xai: 'grok-4-1-fast-reasoning',
                gemini: 'gemini-1.5-flash'
            };

            response = await fetch(endpoints[provider], {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: models[provider],
                    max_tokens: 500,
                    messages: [{ role: 'user', content: message }]
                })
            });

            const data = await response.json();
            if (data.choices && data.choices[0]) {
                showResponse(responseDiv, data.choices[0].message.content);
            } else if (data.error) {
                showResponse(responseDiv, `Error: ${data.error.message}`, true);
            }
        }
    } catch (error) {
        showResponse(responseDiv, `Error: ${error.message}`, true);
    } finally {
        button.disabled = false;
        button.textContent = 'Send Message';
    }
});

// MCP Tools
document.getElementById('mcp-action').addEventListener('change', (e) => {
    const echoGroup = document.getElementById('echo-input-group');
    if (e.target.value === 'echo') {
        echoGroup.style.display = 'block';
    } else {
        echoGroup.style.display = 'none';
    }
});

document.getElementById('mcp-execute').addEventListener('click', async () => {
    const action = document.getElementById('mcp-action').value;
    const button = document.getElementById('mcp-execute');
    const responseDiv = document.getElementById('mcp-response');

    button.disabled = true;
    button.innerHTML = '<span class="loading"></span> Executing...';
    responseDiv.innerHTML = '';

    try {
        let body;

        if (action === 'list') {
            body = {
                jsonrpc: '2.0',
                id: 1,
                method: 'tools/list'
            };
        } else if (action === 'echo') {
            const message = document.getElementById('echo-message').value;
            body = {
                jsonrpc: '2.0',
                id: 2,
                method: 'tools/call',
                params: {
                    name: 'echo',
                    arguments: { message }
                }
            };
        }

        const response = await fetch('http://localhost:3000/mcp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'mcp-protocol-version': '2024-11-05'
            },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (action === 'list' && data.result && data.result.tools) {
            const toolsList = data.result.tools.map(tool =>
                `• ${tool.name}: ${tool.description}`
            ).join('\n');
            showResponse(responseDiv, `Available Tools:\n\n${toolsList}`);
        } else if (data.result) {
            showResponse(responseDiv, JSON.stringify(data.result, null, 2));
        } else if (data.error) {
            showResponse(responseDiv, `Error: ${data.error.message}`, true);
        }
    } catch (error) {
        showResponse(responseDiv, `Error: ${error.message}`, true);
    } finally {
        button.disabled = false;
        button.textContent = 'Execute';
    }
});

// A2A Agents
document.getElementById('agent').addEventListener('change', (e) => {
    const helloForm = document.getElementById('hello-agent-form');
    const calcForm = document.getElementById('calculator-agent-form');

    if (e.target.value === 'hello') {
        helloForm.style.display = 'block';
        calcForm.style.display = 'none';
    } else {
        helloForm.style.display = 'none';
        calcForm.style.display = 'block';
    }
});

document.getElementById('hello-skill').addEventListener('change', (e) => {
    const nameGroup = document.getElementById('hello-name-group');
    const langGroup = document.getElementById('hello-language-group');

    if (e.target.value === 'introduce') {
        nameGroup.style.display = 'none';
        langGroup.style.display = 'none';
    } else {
        nameGroup.style.display = 'block';
        langGroup.style.display = 'block';
    }
});

document.getElementById('calc-skill').addEventListener('change', (e) => {
    const calcInputs = document.getElementById('calculate-inputs');
    const powerInputs = document.getElementById('power-inputs');
    const sqrtInputs = document.getElementById('sqrt-inputs');

    calcInputs.style.display = 'none';
    powerInputs.style.display = 'none';
    sqrtInputs.style.display = 'none';

    if (e.target.value === 'calculate') {
        calcInputs.style.display = 'block';
    } else if (e.target.value === 'power') {
        powerInputs.style.display = 'block';
    } else if (e.target.value === 'sqrt') {
        sqrtInputs.style.display = 'block';
    }
});

document.getElementById('a2a-execute').addEventListener('click', async () => {
    const agent = document.getElementById('agent').value;
    const button = document.getElementById('a2a-execute');
    const responseDiv = document.getElementById('a2a-response');

    button.disabled = true;
    button.innerHTML = '<span class="loading"></span> Executing...';
    responseDiv.innerHTML = '';

    try {
        let endpoint, body;

        if (agent === 'hello') {
            const skill = document.getElementById('hello-skill').value;
            endpoint = 'http://localhost:3000/agent/hello/task';

            if (skill === 'introduce') {
                body = { skill, parameters: {} };
            } else {
                const name = document.getElementById('hello-name').value;
                const language = document.getElementById('hello-language').value;
                body = {
                    skill,
                    parameters: { name, language }
                };
            }
        } else {
            const skill = document.getElementById('calc-skill').value;
            endpoint = 'http://localhost:3000/agent/calculator/task';

            if (skill === 'calculate') {
                const operation = document.getElementById('calc-operation').value;
                const a = parseFloat(document.getElementById('calc-a').value);
                const b = parseFloat(document.getElementById('calc-b').value);
                body = {
                    skill,
                    parameters: { operation, a, b }
                };
            } else if (skill === 'power') {
                const base = parseFloat(document.getElementById('power-base').value);
                const exponent = parseFloat(document.getElementById('power-exponent').value);
                body = {
                    skill,
                    parameters: { base, exponent }
                };
            } else if (skill === 'sqrt') {
                const number = parseFloat(document.getElementById('sqrt-number').value);
                body = {
                    skill,
                    parameters: { number }
                };
            }
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (data.success && data.output) {
            showResponse(responseDiv, data.output.text || JSON.stringify(data.output, null, 2));
        } else if (data.error) {
            showResponse(responseDiv, `Error: ${data.error.message}`, true);
        } else {
            showResponse(responseDiv, JSON.stringify(data, null, 2));
        }
    } catch (error) {
        showResponse(responseDiv, `Error: ${error.message}`, true);
    } finally {
        button.disabled = false;
        button.textContent = 'Execute';
    }
});

// Helper function to show responses
function showResponse(element, content, isError = false) {
    element.innerHTML = `
        <div class="response ${isError ? 'error' : ''}">
            <h3>${isError ? '❌ Error' : '✅ Response'}</h3>
            <div class="response-content">${content}</div>
        </div>
    `;
}
