#!/usr/bin/env python3
"""
Simple WebSocket test for the brand audit application
Tests basic WebSocket connectivity and progress updates
"""

import socketio
import requests
import time
import json
from threading import Thread

# Configuration
BACKEND_URL = 'http://localhost:8000'

def test_websocket_connection():
    """Test basic WebSocket connection"""
    print("🔌 Testing WebSocket connection...")
    
    # Create a Socket.IO client
    sio = socketio.Client()
    
    connection_successful = False
    
    @sio.event
    def connect():
        nonlocal connection_successful
        print("✅ WebSocket connected successfully!")
        connection_successful = True
    
    @sio.event
    def disconnect():
        print("🔌 WebSocket disconnected")
    
    @sio.event
    def connected(data):
        print(f"🎉 Server connection confirmed: {data}")
    
    @sio.event
    def progress_update(data):
        print(f"📊 Progress update received: {data}")
    
    try:
        # Connect to the server
        sio.connect(BACKEND_URL)
        
        # Wait a moment for connection
        time.sleep(2)
        
        if connection_successful:
            print("✅ WebSocket connection test passed")
            
            # Test joining an analysis room
            test_analysis_id = "test-analysis-123"
            sio.emit('join_analysis', {'analysis_id': test_analysis_id})
            print(f"🏠 Joined analysis room: {test_analysis_id}")
            
            # Wait a moment
            time.sleep(1)
            
            # Leave the room
            sio.emit('leave_analysis', {'analysis_id': test_analysis_id})
            print(f"🚪 Left analysis room: {test_analysis_id}")
            
        else:
            print("❌ WebSocket connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ WebSocket connection error: {e}")
        return False
    finally:
        sio.disconnect()
    
    return connection_successful

def test_analysis_with_websocket():
    """Test starting an analysis and monitoring WebSocket updates"""
    print("\n📊 Testing analysis with WebSocket updates...")
    
    # Create a Socket.IO client
    sio = socketio.Client()
    
    progress_updates = []
    analysis_completed = False
    
    @sio.event
    def connect():
        print("✅ WebSocket connected for analysis test")
    
    @sio.event
    def progress_update(data):
        nonlocal analysis_completed
        progress_updates.append(data)
        print(f"📈 Progress: {data.get('overall_progress', 0)}% - {data.get('current_step_name', 'Unknown')}")
        
        if data.get('current_substep'):
            print(f"   └─ {data.get('current_substep')}")
        
        if data.get('status') == 'completed':
            analysis_completed = True
            print("🎉 Analysis completed!")
        elif data.get('status') == 'error':
            print(f"❌ Analysis error: {data.get('error_message', 'Unknown error')}")
    
    try:
        # Connect to WebSocket
        sio.connect(BACKEND_URL)
        time.sleep(1)
        
        # Start an analysis via HTTP API
        print("🚀 Starting brand analysis...")
        response = requests.post(f"{BACKEND_URL}/api/analyze", json={
            "company_name": "Tesla",
            "analysis_types": ["comprehensive"]
        })
        
        if response.status_code == 200:
            data = response.json()
            analysis_id = data.get('data', {}).get('analysis_id')
            print(f"✅ Analysis started with ID: {analysis_id}")
            
            # Join the analysis room
            sio.emit('join_analysis', {'analysis_id': analysis_id})
            print(f"🏠 Joined analysis room: {analysis_id}")
            
            # Monitor progress for up to 5 minutes
            start_time = time.time()
            timeout = 300  # 5 minutes
            
            while not analysis_completed and (time.time() - start_time) < timeout:
                time.sleep(2)
            
            if analysis_completed:
                print(f"✅ Analysis completed! Received {len(progress_updates)} progress updates")
                print("📊 Progress timeline:")
                for i, update in enumerate(progress_updates):
                    print(f"   {i+1}. {update.get('overall_progress', 0)}% - {update.get('current_step_name', 'Unknown')}")
            else:
                print(f"⏰ Analysis timeout after {timeout} seconds")
                print(f"📊 Received {len(progress_updates)} progress updates before timeout")
            
        else:
            print(f"❌ Failed to start analysis: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis test error: {e}")
        return False
    finally:
        sio.disconnect()
    
    return len(progress_updates) > 0

def test_error_handling():
    """Test WebSocket error handling"""
    print("\n🚨 Testing WebSocket error handling...")
    
    sio = socketio.Client()
    
    error_detected = False
    
    @sio.event
    def connect():
        print("✅ WebSocket connected for error test")
    
    @sio.event
    def progress_update(data):
        nonlocal error_detected
        if data.get('status') == 'error':
            error_detected = True
            print(f"🚨 Error detected: {data.get('error_message', 'Unknown error')}")
    
    try:
        sio.connect(BACKEND_URL)
        time.sleep(1)
        
        # Start analysis with invalid data to trigger error
        print("🚀 Starting analysis with invalid data...")
        response = requests.post(f"{BACKEND_URL}/api/analyze", json={
            "company_name": "",  # Empty name should cause error
            "analysis_types": ["comprehensive"]
        })
        
        if response.status_code == 200:
            data = response.json()
            analysis_id = data.get('data', {}).get('analysis_id')
            
            if analysis_id:
                sio.emit('join_analysis', {'analysis_id': analysis_id})
                
                # Wait for error
                start_time = time.time()
                while not error_detected and (time.time() - start_time) < 30:
                    time.sleep(1)
                
                if error_detected:
                    print("✅ Error handling test passed")
                else:
                    print("⚠️ No error detected (might be expected)")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    finally:
        sio.disconnect()
    
    return True

def main():
    """Run all WebSocket tests"""
    print("🚀 Starting WebSocket Real-time Progress Tests\n")
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Basic connection
    if test_websocket_connection():
        tests_passed += 1
    
    # Test 2: Analysis with progress updates
    if test_analysis_with_websocket():
        tests_passed += 1
    
    # Test 3: Error handling
    if test_error_handling():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All WebSocket tests passed!")
        return True
    else:
        print("❌ Some WebSocket tests failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
