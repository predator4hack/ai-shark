# Debugging Guide for AI-Shark Application

This guide provides comprehensive instructions for debugging the AI-Shark application using VSCode.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Debug Configurations](#debug-configurations)
- [Debugging Methods](#debugging-methods)
- [Common Debugging Scenarios](#common-debugging-scenarios)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### 1. Install Required Tools

```bash
# Ensure you have Python 3.11+ installed
python3 --version

# Install debugpy (should already be in requirements)
pip install debugpy

# Activate virtual environment
source .venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. VSCode Extensions

Install the following VSCode extensions:
- **Python** (by Microsoft) - ms-python.python
- **Pylance** (by Microsoft) - ms-python.vscode-pylance
- **Python Debugger** (by Microsoft) - ms-python.debugpy

### 3. Environment Setup

Create a `.env` file in the project root with necessary environment variables:

```bash
# Copy from .env.example if available
cp .env.example .env

# Or create manually with your API keys
cat > .env << EOF
GOOGLE_API_KEY=your_google_api_key_here
# Add other environment variables as needed
EOF
```

## Quick Start

### Method 1: Using the Launch Script

```bash
# Make the script executable (already done)
chmod +x debug_launcher.sh

# Run the launcher
./debug_launcher.sh
```

### Method 2: Using VSCode Debug Panel

1. Open VSCode in the project directory
2. Go to the Debug panel (Ctrl+Shift+D or Cmd+Shift+D)
3. Select a debug configuration from the dropdown
4. Press F5 to start debugging

## Debug Configurations

The `.vscode/launch.json` file contains the following configurations:

### 1. Debug Streamlit App
**Purpose**: Debug the main Streamlit web application

**How to use**:
1. Set breakpoints in `src/ui/streamlit_app.py` or related files
2. Select "Debug Streamlit App" from debug dropdown
3. Press F5
4. Open browser to `http://localhost:8501`

**Use cases**:
- Debug UI interactions
- Test file upload handling
- Debug session state management

### 2. Debug Pitch Deck Processor
**Purpose**: Debug the pitch deck processing logic

**How to use**:
1. Set breakpoints in `src/processors/pitch_deck_processor.py`
2. Select "Debug Pitch Deck Processor"
3. Press F5

**Use cases**:
- Debug PDF/PPT parsing
- Test metadata extraction
- Debug LLM interactions

### 3. Debug Current Python File
**Purpose**: Debug any currently open Python file

**How to use**:
1. Open the Python file you want to debug
2. Set breakpoints
3. Select "Debug Current Python File"
4. Press F5

**Use cases**:
- Quick debugging of individual modules
- Testing standalone scripts

### 4. Debug Tests
**Purpose**: Run pytest tests in debug mode

**How to use**:
1. Set breakpoints in test files or source code
2. Select "Debug Tests"
3. Press F5

**Use cases**:
- Debug failing tests
- Step through test execution
- Verify test coverage

### 5. Debug Single Test File
**Purpose**: Debug a specific test file

**How to use**:
1. Open a test file
2. Set breakpoints
3. Select "Debug Single Test File"
4. Press F5

### 6. Attach to Running Process
**Purpose**: Attach debugger to an already running process

**How to use**:
1. Start your application with debugpy:
   ```bash
   python -m debugpy --listen 5678 --wait-for-client -m streamlit run src/ui/streamlit_app.py
   ```
2. In VSCode, select "Attach to Running Process"
3. Press F5

**Use cases**:
- Debug production-like environments
- Debug long-running processes
- Remote debugging

## Debugging Methods

### Method A: VSCode Integrated Debugging

**Steps**:
1. **Set Breakpoints**
   - Click in the left gutter of the code editor (red dot appears)
   - Or press F9 on a line
   - Conditional breakpoints: Right-click → Add Conditional Breakpoint

2. **Start Debugging**
   - Press F5 or click the green play button
   - Or: Run → Start Debugging

3. **Debug Controls**
   - **F5**: Continue
   - **F10**: Step Over
   - **F11**: Step Into
   - **Shift+F11**: Step Out
   - **Ctrl+Shift+F5**: Restart
   - **Shift+F5**: Stop

4. **Inspect Variables**
   - View in Variables panel
   - Hover over variables in code
   - Add to Watch panel
   - Evaluate in Debug Console

### Method B: Command Line Debugging

**Using debugpy directly**:

```bash
# Start with debugpy and wait for client
python -m debugpy --listen 5678 --wait-for-client -m streamlit run src/ui/streamlit_app.py

# Then attach from VSCode using "Attach to Running Process"
```

**Using the debug launcher script**:

```bash
./debug_launcher.sh
# Select option from menu
```

### Method C: Add Debug Code

For quick debugging, add these lines to your Python code:

```python
# At the point where you want to break
import debugpy
debugpy.listen(5678)
print("Waiting for debugger attach")
debugpy.wait_for_client()
debugpy.breakpoint()
print("Debugger attached!")
```

Then attach from VSCode.

## Common Debugging Scenarios

### Scenario 1: Debug Streamlit Upload Processing

```python
# In src/ui/streamlit_app.py, function process_pitch_deck()

def process_pitch_deck(uploaded_file):
    """Process uploaded pitch deck"""
    # Set breakpoint on the next line
    with st.spinner("Processing pitch deck... This may take a few minutes."):
        try:
            temp_path = save_temp_file(uploaded_file)  # <- Breakpoint here

            processor = PitchDeckProcessor()
            result = processor.process(temp_path, "outputs")  # <- And here
            # ... rest of code
```

**Steps**:
1. Set breakpoints as shown above
2. Run "Debug Streamlit App"
3. Upload a file in the browser
4. Click "Process Pitch Deck"
5. Debugger will pause at breakpoints

### Scenario 2: Debug LLM API Calls

```python
# In src/processors/pitch_deck_processor.py

class PitchDeckProcessor:
    def extract_metadata(self, images):
        # Set breakpoint before LLM call
        prompt = self._create_metadata_prompt()  # <- Breakpoint

        response = self.llm_client.generate_content(prompt)  # <- Breakpoint

        # Inspect response
        metadata = self._parse_metadata(response.text)  # <- Breakpoint
        return metadata
```

**Steps**:
1. Set breakpoints in the LLM interaction code
2. Use "Debug Pitch Deck Processor" or "Debug Streamlit App"
3. Inspect:
   - Prompt content
   - Response from LLM
   - Parsed metadata

### Scenario 3: Debug Analysis Pipeline

```python
# In src/processors/analysis_pipeline.py

class AnalysisPipeline:
    def run_pipeline(self):
        # Set breakpoint at start
        results = {}  # <- Breakpoint

        for agent_name, agent in self.agents.items():
            # Breakpoint in loop
            print(f"Running {agent_name}")  # <- Breakpoint
            result = agent.analyze()  # <- Breakpoint
            results[agent_name] = result

        return results
```

**Steps**:
1. Set breakpoints in pipeline execution
2. Run "Debug Streamlit App" and trigger analysis
3. Step through each agent execution
4. Inspect agent results

### Scenario 4: Debug Tests

```python
# In tests/test_pitch_deck_processor.py

def test_metadata_extraction():
    processor = PitchDeckProcessor()

    # Set breakpoint
    metadata = processor.extract_metadata(sample_images)  # <- Breakpoint

    # Inspect results
    assert metadata is not None  # <- Breakpoint
    assert 'company_name' in metadata
```

**Steps**:
1. Set breakpoints in test code
2. Run "Debug Single Test File"
3. Step through test execution
4. Verify assertions

## Debugging Tips

### 1. Use Logpoints Instead of Print Statements

Instead of adding `print()` statements:
- Right-click in gutter → Add Logpoint
- Enter message with {variable} syntax
- No code changes needed!

Example: `Company name: {company_name}, Status: {result['status']}`

### 2. Conditional Breakpoints

For loops or frequently called functions:
- Right-click breakpoint → Edit Breakpoint → Expression
- Enter condition: `company_name == "TestCo"` or `i > 10`

### 3. Exception Breakpoints

To break when exceptions occur:
1. Debug panel → Breakpoints section
2. Check "Uncaught Exceptions" or "Raised Exceptions"

### 4. Debug Console

Use the Debug Console to:
- Execute Python code: `print(variable)`
- Evaluate expressions: `len(results)`
- Modify variables: `company_name = "NewName"`
- Call functions: `processor.extract_metadata(images)`

### 5. Watch Variables

Add expressions to Watch panel:
- Click + in Watch panel
- Add: `len(uploaded_files)`, `st.session_state`, etc.
- Watches update as you step through code

## Environment Variables During Debugging

The launch configurations automatically set `PYTHONPATH` to the workspace folder. You can add more environment variables:

```json
"env": {
    "PYTHONPATH": "${workspaceFolder}",
    "DEBUG_MODE": "true",
    "LOG_LEVEL": "DEBUG"
}
```

Or use `.env` file (automatically loaded by python-dotenv).

## Troubleshooting

### Issue: "Module not found" errors

**Solution**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Check PYTHONPATH in launch.json
```

### Issue: Breakpoints not hitting

**Solutions**:
1. Ensure `justMyCode` is `false` in launch.json (to debug libraries)
2. Check file paths are correct
3. Verify code is actually executing
4. Try adding `debugpy.breakpoint()` in code

### Issue: Debugger connects but immediately exits

**Solution**:
- Check for exceptions in Debug Console
- Verify environment variables are set
- Check file permissions
- Look at integrated terminal output

### Issue: Cannot connect to remote debugger

**Solution**:
```bash
# Check if port is available
netstat -an | grep 5678

# Try different port in launch.json and code
# Ensure firewall allows connection
```

### Issue: Streamlit auto-reloads breaking debugging

**Solution**:
Add to streamlit command:
```json
"args": [
    "run",
    "${workspaceFolder}/src/ui/streamlit_app.py",
    "--server.runOnSave=false",  // Disable auto-reload
    "--server.port=8501"
]
```

## Advanced Debugging

### Remote Debugging (e.g., Docker container)

1. **In container, add to code**:
```python
import debugpy
debugpy.listen(("0.0.0.0", 5678))
debugpy.wait_for_client()
```

2. **Expose port in docker-compose.yml**:
```yaml
ports:
  - "8501:8501"
  - "5678:5678"  # Debug port
```

3. **Use "Attach to Running Process" configuration**

### Multi-threaded/Async Debugging

For debugging async code:
```python
import asyncio
import debugpy

async def main():
    debugpy.breakpoint()  # Works in async functions
    await some_async_function()

asyncio.run(main())
```

### Debugging LLM Prompts

Create a helper to save prompts:
```python
def debug_llm_call(prompt, response):
    import json
    with open('debug_llm.json', 'a') as f:
        json.dump({
            'prompt': prompt,
            'response': response
        }, f, indent=2)
    # Set breakpoint here
    debugpy.breakpoint()
```

## Useful Keyboard Shortcuts

| Action | Windows/Linux | macOS |
|--------|--------------|-------|
| Start Debugging | F5 | F5 |
| Stop Debugging | Shift+F5 | Shift+F5 |
| Restart Debugging | Ctrl+Shift+F5 | Cmd+Shift+F5 |
| Continue | F5 | F5 |
| Step Over | F10 | F10 |
| Step Into | F11 | F11 |
| Step Out | Shift+F11 | Shift+F11 |
| Toggle Breakpoint | F9 | F9 |
| Show Debug Console | Ctrl+Shift+Y | Cmd+Shift+Y |

## Resources

- [VSCode Python Debugging Guide](https://code.visualstudio.com/docs/python/debugging)
- [debugpy Documentation](https://github.com/microsoft/debugpy)
- [Streamlit Debugging Tips](https://docs.streamlit.io/knowledge-base/using-streamlit/how-do-i-debug-streamlit)

## Quick Reference Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Run Streamlit normally
streamlit run src/ui/streamlit_app.py

# Run Streamlit with debugpy
python -m debugpy --listen 5678 --wait-for-client -m streamlit run src/ui/streamlit_app.py

# Run tests with debugpy
python -m debugpy --listen 5678 --wait-for-client -m pytest tests/ -v

# Check if debugpy is installed
pip show debugpy

# Install debugpy if missing
pip install debugpy
```

---

**Happy Debugging! 🐛🔍**
