#!/bin/bash

# Configuration
STAGING_DIR="staging_build"
STAGING_PORT=8502
PID_FILE="staging.pid"

echo "🚀 Deploying to Local Staging Environment..."

# 1. Create/Clean Staging Directory
echo "🧹 Cleaning staging directory..."
rm -rf $STAGING_DIR
mkdir $STAGING_DIR

# 2. Copy Files (Simulating a 'build' artifact)
echo "📦 Copying application files..."
cp app.py $STAGING_DIR/
cp email_agent.py $STAGING_DIR/
cp requirements.txt $STAGING_DIR/
cp email_icon.png $STAGING_DIR/
# Copy .env if it exists
if [ -f .env ]; then
    cp .env $STAGING_DIR/
fi

# 3. Stop Existing Staging Process
if [ -f $PID_FILE ]; then
    echo "🛑 Stopping existing staging process..."
    kill $(cat $PID_FILE) 2>/dev/null || true
    rm $PID_FILE
fi

# 4. Run Streamlit from Staging Directory
echo "▶️ Starting Staging Server on port $STAGING_PORT..."
cd $STAGING_DIR

# Run in background, no auto-reload (mimicking prod)
nohup streamlit run app.py \
    --server.port $STAGING_PORT \
    --server.headless true \
    --server.runOnSave false \
    > ../staging.log 2>&1 &

# Save PID
echo $! > ../$PID_FILE

echo "✅ Staging Deployed Successfully!"
echo "🌍 Staging URL: http://localhost:$STAGING_PORT"
echo "📝 Logs: staging.log"
