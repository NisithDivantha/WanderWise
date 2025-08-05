"""
Web interface for the Travel Planner API.
Simple HTML interface for testing the API without external tools.
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WanderWise Travel Planner</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #34495e;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            background-color: #3498db;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background-color: #2980b9;
        }
        button:disabled {
            background-color: #bdc3c7;
            cursor: not-allowed;
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 5px;
            display: none;
        }
        .success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .error {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .itinerary-day {
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .activity {
            margin-bottom: 10px;
            padding: 10px;
            background-color: white;
            border-radius: 3px;
            border-left: 3px solid #3498db;
        }
        .poi-list, .hotel-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .poi-item, .hotel-item {
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border: 1px solid #e9ecef;
        }
        .rating {
            color: #f39c12;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 WanderWise Travel Planner</h1>
        
        <form id="travelForm">
            <div class="form-group">
                <label for="destination">Destination (City, Country):</label>
                <input type="text" id="destination" name="destination" placeholder="e.g., Paris, France" required>
            </div>
            
            <div class="form-group">
                <label for="startDate">Start Date:</label>
                <input type="date" id="startDate" name="startDate" required>
            </div>
            
            <div class="form-group">
                <label for="endDate">End Date:</label>
                <input type="date" id="endDate" name="endDate" required>
            </div>
            
            <div class="form-group">
                <label for="budget">Budget (Optional):</label>
                <select id="budget" name="budget">
                    <option value="">Select budget range</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="interests">Interests (Optional, comma-separated):</label>
                <input type="text" id="interests" name="interests" placeholder="e.g., culture, food, history, art">
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" id="useLLM" name="useLLM" checked>
                    Use AI for smart itinerary generation
                </label>
            </div>
            
            <button type="submit">Generate Travel Plan</button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Generating your travel plan... This may take a few minutes.</p>
        </div>
        
        <div class="result" id="result"></div>
    </div>

    <script>
        document.getElementById('travelForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = {
                destination: formData.get('destination'),
                start_date: formData.get('startDate'),
                end_date: formData.get('endDate'),
                use_llm: formData.get('useLLM') === 'on'
            };
            
            if (formData.get('budget')) {
                data.budget = formData.get('budget');
            }
            
            if (formData.get('interests')) {
                data.interests = formData.get('interests').split(',').map(s => s.trim());
            }
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            document.querySelector('button[type="submit"]').disabled = true;
            
            try {
                const response = await fetch('/generate-travel-plan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    displayResult(result);
                } else {
                    displayError(result.detail || 'An error occurred');
                }
                
            } catch (error) {
                displayError('Failed to connect to the server: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
                document.querySelector('button[type="submit"]').disabled = false;
            }
        });
        
        function displayResult(data) {
            const resultDiv = document.getElementById('result');
            resultDiv.className = 'result success';
            
            let html = `
                <h2>Travel Plan for ${data.destination}</h2>
                <p><strong>Dates:</strong> ${data.start_date} to ${data.end_date}</p>
                <p><strong>Generated:</strong> ${new Date(data.generation_timestamp).toLocaleString()}</p>
                
                <h3>Executive Summary</h3>
                <p>${data.executive_summary}</p>
            `;
            
            if (data.points_of_interest && data.points_of_interest.length > 0) {
                html += `<h3>Points of Interest (${data.points_of_interest.length})</h3>`;
                html += '<div class="poi-list">';
                data.points_of_interest.forEach(poi => {
                    html += `
                        <div class="poi-item">
                            <h4>${poi.name}</h4>
                            <p class="rating">Rating: ${poi.rating}/5</p>
                            <p>${poi.description}</p>
                        </div>
                    `;
                });
                html += '</div>';
            }
            
            if (data.hotels && data.hotels.length > 0) {
                html += `<h3>Hotels (${data.hotels.length})</h3>`;
                html += '<div class="hotel-list">';
                data.hotels.forEach(hotel => {
                    html += `
                        <div class="hotel-item">
                            <h4>${hotel.name}</h4>
                            <p><strong>Price:</strong> ${hotel.price}</p>
                            ${hotel.rating ? `<p class="rating">Rating: ${hotel.rating}/5</p>` : ''}
                        </div>
                    `;
                });
                html += '</div>';
            }
            
            if (data.itinerary && data.itinerary.length > 0) {
                html += `<h3>Day-by-Day Itinerary (${data.itinerary.length} days)</h3>`;
                data.itinerary.forEach(day => {
                    html += `
                        <div class="itinerary-day">
                            <h4>${day.date}</h4>
                    `;
                    day.activities.forEach(activity => {
                        html += `
                            <div class="activity">
                                <strong>${activity.time}</strong> - ${activity.activity}
                                ${activity.description ? `<br><small>${activity.description}</small>` : ''}
                            </div>
                        `;
                    });
                    html += '</div>';
                });
            }
            
            resultDiv.innerHTML = html;
            resultDiv.style.display = 'block';
        }
        
        function displayError(message) {
            const resultDiv = document.getElementById('result');
            resultDiv.className = 'result error';
            resultDiv.innerHTML = `<h3>Error</h3><p>${message}</p>`;
            resultDiv.style.display = 'block';
        }
        
        // Set default dates (today and tomorrow)
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 30); // 30 days from now
        const dayAfter = new Date(tomorrow);
        dayAfter.setDate(dayAfter.getDate() + 2);
        
        document.getElementById('startDate').value = tomorrow.toISOString().split('T')[0];
        document.getElementById('endDate').value = dayAfter.toISOString().split('T')[0];
    </script>
</body>
</html>
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

def add_web_interface(app: FastAPI):
    """Add a simple web interface to the FastAPI app."""
    
    @app.get("/web", response_class=HTMLResponse)
    async def web_interface():
        """Serve the web interface."""
        return HTML_TEMPLATE
