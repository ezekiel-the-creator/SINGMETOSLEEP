from flask import Flask, request, render_template_string, redirect, url_for
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'models')))
from recommend_music import recommend_music, get_sleep_playlist

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    output = None  # Initialize output to avoid UnboundLocalError
    if request.method == 'POST':
        try:
            mode = request.form['mode']
            age = int(request.form['age'])
            gender = request.form['gender']
            if mode == 'single':
                _, result = recommend_music(age, gender)
                output = result
            else:  # sleep mode
                recommendations, playlist_url = get_sleep_playlist(age, gender)
                if recommendations:
                    output = "🌙 Sleep Mode Results:\n" + "\n".join(recommendations)
                    output += f"\n\nPlay it here: <a href='{playlist_url}' target='_blank'>{playlist_url}</a>"
                else:
                    output = "No videos found for sleep playlist. Try again, G!"
        except Exception as e:
            output = f"Error: {e}. Try again, G!"
        if output is None:
            output = "Something went wrong. Please try again, G!"
        # Render the result page, but include the form below the results
        return render_template_string('''
            <h1>🌙 Sleep Mode Music Generator 🌙</h1>
            <p style="white-space: pre-line">{{ output | safe }}</p>
            <a href="{{ url_for('index') }}">Back to Dreamland</a>
            <h2>Generate Another Playlist</h2>
            <form method="post">
                Mode: <select name="mode" required>
                    <option value="single">Single Song</option>
                    <option value="sleep" selected>Sleep Playlist (7 Songs)</option>
                </select><br><br>
                Age: <input type="number" name="age" required><br><br>
                Gender: <select name="gender" required>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                </select><br><br>
                <input type="submit" value="Generate Dreamy Tunes">
            </form>
            <style>
                body { 
                    font-family: 'Lora', serif; 
                    text-align: center; 
                    background: linear-gradient(to bottom, #1a1a2e, #16213e); 
                    color: #e0e0e0; 
                    margin: 0; 
                    padding: 20px; 
                    min-height: 100vh; 
                    display: flex; 
                    flex-direction: column; 
                    justify-content: center; 
                }
                h1 { 
                    font-family: 'Dancing Script', cursive; 
                    font-size: 3em; 
                    color: #a3bffa; 
                    text-shadow: 0 0 10px rgba(163, 191, 250, 0.5); 
                    margin-bottom: 20px; 
                }
                h2 {
                    font-family: 'Lora', serif;
                    font-size: 1.5em;
                    color: #a3bffa;
                    margin-top: 30px;
                }
                p { 
                    font-size: 1.2em; 
                    background: rgba(255, 255, 255, 0.05); 
                    padding: 15px; 
                    border-radius: 10px; 
                    max-width: 600px; 
                    margin: 0 auto 20px; 
                }
                form { 
                    background: rgba(255, 255, 255, 0.05); 
                    padding: 20px; 
                    border-radius: 15px; 
                    max-width: 400px; 
                    margin: 0 auto; 
                    box-shadow: 0 0 20px rgba(163, 191, 250, 0.2); 
                }
                select, input[type="number"] { 
                    padding: 10px; 
                    font-size: 1em; 
                    margin: 10px 0; 
                    border: none; 
                    border-radius: 5px; 
                    background: #e0e0e0; 
                    color: #333; 
                    width: 200px; 
                }
                input[type="submit"] { 
                    background: #a3bffa; 
                    color: #1a1a2e; 
                    border: none; 
                    padding: 10px 20px; 
                    font-size: 1em; 
                    border-radius: 5px; 
                    cursor: pointer; 
                    transition: background 0.3s ease, transform 0.1s ease; 
                }
                input[type="submit"]:hover { 
                    background: #c3e0ff; 
                    transform: scale(1.05); 
                }
                a { 
                    color: #a3bffa; 
                    text-decoration: none; 
                    font-weight: bold; 
                    transition: color 0.3s ease; 
                    display: inline-block; 
                    margin-bottom: 20px; 
                }
                a:hover { 
                    color: #c3e0ff; 
                    text-shadow: 0 0 5px rgba(195, 224, 255, 0.7); 
                }
            </style>
        ''', output=output)
    # GET request: Show the form
    return render_template_string('''
        <h1>🌙 Sleep Mode Music Generator 🌙</h1>
        <p>Welcome to Sleep Mode Music Generator! Select your options to get started.</p>
        <form method="post">
            Mode: <select name="mode" required>
                <option value="single">Single Song</option>
                <option value="sleep" selected>Sleep Playlist (7 Songs)</option>
            </select><br><br>
            Age: <input type="number" name="age" required><br><br>
            Gender: <select name="gender" required>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
            </select><br><br>
            <input type="submit" value="Generate Dreamy Tunes">
        </form>
        <style>
            body { 
                font-family: 'Lora', serif; 
                text-align: center; 
                background: linear-gradient(to bottom, #1a1a2e, #16213e); 
                color: #e0e0e0; 
                margin: 0; 
                padding: 20px; 
                min-height: 100vh; 
                display: flex; 
                flex-direction: column; 
                justify-content: center; 
            }
            h1 { 
                font-family: 'Dancing Script', cursive; 
                font-size: 3em; 
                color: #a3bffa; 
                text-shadow: 0 0 10px rgba(163, 191, 250, 0.5); 
                margin-bottom: 20px; 
            }
            p { 
                font-size: 1.2em; 
                margin-bottom: 20px; 
            }
            form { 
                background: rgba(255, 255, 255, 0.05); 
                padding: 20px; 
                border-radius: 15px; 
                max-width: 400px; 
                margin: 0 auto; 
                box-shadow: 0 0 20px rgba(163, 191, 250, 0.2); 
            }
            select, input[type="number"] { 
                padding: 10px; 
                font-size: 1em; 
                margin: 10px 0; 
                border: none; 
                border-radius: 5px; 
                background: #e0e0e0; 
                color: #333; 
                width: 200px; 
            }
            input[type="submit"] { 
                background: #a3bffa; 
                color: #1a1a2e; 
                border: none; 
                padding: 10px 20px; 
                font-size: 1em; 
                border-radius: 5px; 
                cursor: pointer; 
                transition: background 0.3s ease, transform 0.1s ease; 
            }
            input[type="submit"]:hover { 
                background: #c3e0ff; 
                transform: scale(1.05); 
            }
        </style>
    ''')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)