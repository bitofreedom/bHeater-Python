#!/bin/bash

echo "================================================================================"
echo "Office Miner Test - Setting to HIGH mode"
echo "================================================================================"

# Start the service on port 5001
echo ""
echo "Starting heater service on port 5001..."
./venv/bin/python -c "from heaterService import app; app.run(host='0.0.0.0', port=5001)" &
SERVICE_PID=$!

# Wait for service to start
echo "Waiting for service to start (PID: $SERVICE_PID)..."
sleep 4

# Test the /set_heater endpoint
echo ""
echo "Testing: Setting office miner to HIGH mode"
echo "URL: http://localhost:5001/set_heater"
echo "Payload: {\"heaterName\": \"office\", \"action\": \"high\"}"
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:5001/set_heater \
  -H "Content-Type: application/json" \
  -d '{"heaterName": "office", "action": "high"}')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

echo "HTTP Status: $HTTP_CODE"
echo "Response Body: $BODY"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ SUCCESS: Office miner configuration set to HIGH mode"
    echo ""
    echo "The bosminer-quiet-high.toml file was transferred to ellsworth-office.local"
else
    echo "✗ FAILED: Request failed with status $HTTP_CODE"
    echo "Error: $BODY"
fi

# Clean up
echo ""
echo "================================================================================"
echo "Stopping heater service..."
kill $SERVICE_PID 2>/dev/null
wait $SERVICE_PID 2>/dev/null

echo "Test complete."
echo "================================================================================"
