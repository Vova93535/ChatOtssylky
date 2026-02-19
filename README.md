# Public Web Chat on Flask and Socket.IO

A simple yet functional real-time chat with message history and a built-in bot. All messages are visible to all connected users — perfect for small group conversations or testing web technologies.

## ? Features
- Instant message sending and receiving (WebSocket)
- Last 100 messages history on connection
- Nickname change (persists only for the session)
- Built-in bot:
  - Sends a random message to the chat every 30 minutes
  - Responds to `!bot <text>` command (echos your message)
- Responsive and clean interface (works on mobile and desktop)

## ?? Tech Stack
- **Backend:** Python + Flask + Flask-SocketIO + Eventlet
- **Frontend:** HTML, CSS, JavaScript (vanilla, no frameworks)
- **Protocols:** WebSocket (via Socket.IO)

## ?? Local Installation & Launch

### Prerequisites
- Python 3.7 or higher
- `pip` (Python package manager)

### Steps
1. **Clone the repository**
   ```bash
   git clone https://github.com/Vova93535/ChatOtssylky.git
   cd ChatOtssylky
   ```

2. **Install dependencies**
   ```bash
   pip install -r req.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open in your browser**  
   Go to `http://127.0.0.1:5000`

Done! The chat works locally. You can open multiple tabs or devices on the same network and start chatting.

## ?? Usage
- **Change nickname:** enter a new nickname in the top field and click "Change" (a random nickname like `User123` is assigned by default).
- **Send a message:** type your text in the bottom field and press Enter or click the "Send" button.
- **Bot commands:**
  - `!bot` — bot introduces itself.
  - `!bot Hello!` — bot repeats your message.

## ?? Production Deployment

### Option 1: PythonAnywhere (free)
1. Upload files via console or FTP.
2. Create a web app with manual configuration, choose Python 3.x.
3. Install dependencies: `pip install --user -r req.txt`.
4. In WSGI configuration, point to your app (Flask + SocketIO may need extra setup — better use another option).

### Option 2: Render (recommended)
1. Create a new Web Service, connect your repository.
2. Choose **Python 3** runtime.
3. Start command:
   ```bash
   gunicorn -k eventlet -w 1 app:app
   ```
4. Set any environment variables if needed.
5. Click Deploy.

### Option 3: Heroku (deprecating but still works)
1. Create a `Procfile`:
   ```
   web: gunicorn -k eventlet -w 1 app:app
   ```
2. Ensure `gunicorn` and `eventlet` are in `requirements.txt`.
3. Deploy via standard Git flow.

## ?? Project Structure
```
ChatOtssylky/
??? app.py              # Main Flask + SocketIO server
??? req.txt             # Python dependencies
??? templates/
?   ??? index.html      # Client-side interface
??? README.md           # This file
```

## ?? Contributing
If you find a bug or have a suggestion for improvement, feel free to open an issue or a pull request. We welcome contributions!
