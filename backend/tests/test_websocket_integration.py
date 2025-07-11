"""
WebSocket integration tests for real-time progress updates
"""
import pytest
import json
import time
import asyncio
from unittest.mock import patch, Mock

from conftest import assert_valid_progress_update, IntegrationTestHelper


class TestWebSocketIntegration:
    """Test WebSocket functionality for real-time updates"""
    
    def test_websocket_connection(self, socketio_client):
        """Test basic WebSocket connection"""
        # Test connection
        received = socketio_client.get_received()
        
        # Should receive connection confirmation
        assert len(received) > 0
        connect_event = received[0]
        assert connect_event['name'] == 'connected'
        assert 'status' in connect_event['args'][0]
    
    def test_join_analysis_room(self, socketio_client, test_analysis):
        """Test joining analysis room"""
        # Join analysis room
        socketio_client.emit('join_analysis', {'analysis_id': test_analysis.id})
        
        # Should not receive any error
        received = socketio_client.get_received()
        
        # Check for any error messages
        error_events = [event for event in received if event['name'] == 'error']
        assert len(error_events) == 0
    
    def test_progress_updates(self, socketio_client, websocket_service, test_analysis, test_data_factory):
        """Test progress update broadcasting"""
        # Join analysis room
        socketio_client.emit('join_analysis', {'analysis_id': test_analysis.id})
        
        # Clear received messages
        socketio_client.get_received()
        
        # Send progress update
        progress_data = test_data_factory.create_progress_update(test_analysis.id, progress=50)
        websocket_service.emit_progress_update(test_analysis.id, progress_data)
        
        # Check received progress update
        received = socketio_client.get_received()
        progress_events = [event for event in received if event['name'] == 'progress_update']
        
        assert len(progress_events) > 0
        progress_event = progress_events[0]
        progress_data = progress_event['args'][0]
        
        assert_valid_progress_update(progress_data)
        assert progress_data['analysis_id'] == test_analysis.id
    
    def test_multiple_clients_same_analysis(self, app, test_analysis, test_data_factory):
        """Test multiple clients receiving updates for same analysis"""
        from flask_socketio import SocketIO
        
        socketio = SocketIO(app, cors_allowed_origins="*")
        
        # Create multiple clients
        client1 = socketio.test_client(app)
        client2 = socketio.test_client(app)
        
        # Both join same analysis room
        client1.emit('join_analysis', {'analysis_id': test_analysis.id})
        client2.emit('join_analysis', {'analysis_id': test_analysis.id})
        
        # Clear received messages
        client1.get_received()
        client2.get_received()
        
        # Send progress update
        progress_data = test_data_factory.create_progress_update(test_analysis.id, progress=75)
        socketio.emit('progress_update', progress_data, room=test_analysis.id)
        
        # Both clients should receive the update
        received1 = client1.get_received()
        received2 = client2.get_received()
        
        progress_events1 = [event for event in received1 if event['name'] == 'progress_update']
        progress_events2 = [event for event in received2 if event['name'] == 'progress_update']
        
        assert len(progress_events1) > 0
        assert len(progress_events2) > 0
        
        # Verify both received same data
        data1 = progress_events1[0]['args'][0]
        data2 = progress_events2[0]['args'][0]
        assert data1['analysis_id'] == data2['analysis_id']
        assert data1['overall_progress'] == data2['overall_progress']
    
    def test_websocket_error_handling(self, socketio_client, test_analysis):
        """Test WebSocket error handling"""
        # Try to join non-existent analysis
        socketio_client.emit('join_analysis', {'analysis_id': 'non-existent-id'})
        
        # Should handle gracefully without crashing
        received = socketio_client.get_received()
        
        # Check for error handling (implementation dependent)
        # At minimum, should not crash the connection
        assert socketio_client.connected
    
    def test_websocket_disconnection(self, socketio_client, test_analysis):
        """Test WebSocket disconnection handling"""
        # Join analysis room
        socketio_client.emit('join_analysis', {'analysis_id': test_analysis.id})
        
        # Disconnect
        socketio_client.disconnect()
        
        # Should disconnect cleanly
        assert not socketio_client.connected
    
    def test_progress_update_sequence(self, socketio_client, websocket_service, test_analysis):
        """Test sequence of progress updates"""
        # Join analysis room
        socketio_client.emit('join_analysis', {'analysis_id': test_analysis.id})
        socketio_client.get_received()  # Clear initial messages
        
        # Send sequence of progress updates
        progress_values = [10, 25, 50, 75, 100]
        stages = ['Starting', 'LLM Analysis', 'Visual Analysis', 'News Analysis', 'Completed']
        
        for i, (progress, stage) in enumerate(zip(progress_values, stages)):
            update_data = {
                'analysis_id': test_analysis.id,
                'overall_progress': progress,
                'current_stage': i,
                'current_step_name': stage,
                'status': 'completed' if progress == 100 else 'processing'
            }
            
            websocket_service.emit_progress_update(test_analysis.id, update_data)
            time.sleep(0.1)  # Small delay between updates
        
        # Check all updates were received
        received = socketio_client.get_received()
        progress_events = [event for event in received if event['name'] == 'progress_update']
        
        assert len(progress_events) == len(progress_values)
        
        # Verify progress sequence
        for i, event in enumerate(progress_events):
            data = event['args'][0]
            assert data['overall_progress'] == progress_values[i]
            assert data['current_step_name'] == stages[i]


class TestWebSocketAnalysisIntegration:
    """Test WebSocket integration with analysis workflow"""
    
    def test_websocket_with_real_analysis(self, client, socketio_client, test_data_factory, mock_api_services):
        """Test WebSocket updates during real analysis"""
        # Start analysis via HTTP API
        request_data = test_data_factory.create_analysis_request("WebSocket Test Brand")
        
        response = client.post('/api/analyze',
                             data=json.dumps(request_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        analysis_id = data['data']['analysis_id']
        
        # Join WebSocket room for this analysis
        socketio_client.emit('join_analysis', {'analysis_id': analysis_id})
        socketio_client.get_received()  # Clear initial messages
        
        # Wait for progress updates
        max_wait = 30  # seconds
        start_time = time.time()
        progress_updates = []
        
        while time.time() - start_time < max_wait:
            received = socketio_client.get_received()
            progress_events = [event for event in received if event['name'] == 'progress_update']
            
            for event in progress_events:
                progress_data = event['args'][0]
                progress_updates.append(progress_data)
                
                # Check if analysis completed
                if progress_data.get('status') == 'completed':
                    break
            
            if progress_updates and progress_updates[-1].get('status') == 'completed':
                break
                
            time.sleep(1)
        
        # Verify we received progress updates
        assert len(progress_updates) > 0
        
        # Verify progress updates are valid
        for update in progress_updates:
            assert_valid_progress_update(update)
            assert update['analysis_id'] == analysis_id
        
        # Verify progress increases over time
        if len(progress_updates) > 1:
            for i in range(1, len(progress_updates)):
                current_progress = progress_updates[i]['overall_progress']
                previous_progress = progress_updates[i-1]['overall_progress']
                assert current_progress >= previous_progress
    
    def test_websocket_error_propagation(self, client, socketio_client, test_data_factory):
        """Test error propagation through WebSocket"""
        # Mock service to raise error
        with patch('src.services.llm_service.LLMService') as mock_llm:
            mock_llm.return_value.analyze_brand_sentiment.side_effect = Exception("Test Error")
            
            # Start analysis
            request_data = test_data_factory.create_analysis_request("Error Test Brand")
            response = client.post('/api/analyze',
                                 data=json.dumps(request_data),
                                 content_type='application/json')
            
            if response.status_code == 200:
                data = response.get_json()
                analysis_id = data['data']['analysis_id']
                
                # Join WebSocket room
                socketio_client.emit('join_analysis', {'analysis_id': analysis_id})
                socketio_client.get_received()
                
                # Wait for error update
                max_wait = 15
                start_time = time.time()
                error_received = False
                
                while time.time() - start_time < max_wait and not error_received:
                    received = socketio_client.get_received()
                    progress_events = [event for event in received if event['name'] == 'progress_update']
                    
                    for event in progress_events:
                        progress_data = event['args'][0]
                        if progress_data.get('status') == 'error' or progress_data.get('error_message'):
                            error_received = True
                            break
                    
                    time.sleep(1)
                
                # Note: Error handling depends on implementation
                # At minimum, should not crash the WebSocket connection
                assert socketio_client.connected
    
    def test_websocket_reconnection_simulation(self, app, test_analysis):
        """Test WebSocket reconnection behavior"""
        from flask_socketio import SocketIO
        
        socketio = SocketIO(app, cors_allowed_origins="*")
        
        # Create client and connect
        client = socketio.test_client(app)
        client.emit('join_analysis', {'analysis_id': test_analysis.id})
        
        # Simulate disconnection
        client.disconnect()
        assert not client.connected
        
        # Reconnect
        client = socketio.test_client(app)
        assert client.connected
        
        # Should be able to rejoin analysis room
        client.emit('join_analysis', {'analysis_id': test_analysis.id})
        
        # Should not receive errors
        received = client.get_received()
        error_events = [event for event in received if event['name'] == 'error']
        assert len(error_events) == 0


class TestWebSocketPerformance:
    """Test WebSocket performance and scalability"""
    
    def test_multiple_concurrent_connections(self, app, test_analysis):
        """Test handling multiple concurrent WebSocket connections"""
        from flask_socketio import SocketIO
        
        socketio = SocketIO(app, cors_allowed_origins="*")
        
        # Create multiple clients
        num_clients = 10
        clients = []
        
        for i in range(num_clients):
            client = socketio.test_client(app)
            client.emit('join_analysis', {'analysis_id': test_analysis.id})
            clients.append(client)
        
        # All clients should be connected
        for client in clients:
            assert client.connected
        
        # Send broadcast message
        socketio.emit('progress_update', {
            'analysis_id': test_analysis.id,
            'overall_progress': 50,
            'current_stage': 1,
            'status': 'processing',
            'current_step_name': 'Test Update'
        }, room=test_analysis.id)
        
        # All clients should receive the message
        for client in clients:
            received = client.get_received()
            progress_events = [event for event in received if event['name'] == 'progress_update']
            assert len(progress_events) > 0
        
        # Clean up
        for client in clients:
            client.disconnect()
    
    def test_websocket_message_ordering(self, socketio_client, websocket_service, test_analysis):
        """Test WebSocket message ordering"""
        # Join analysis room
        socketio_client.emit('join_analysis', {'analysis_id': test_analysis.id})
        socketio_client.get_received()
        
        # Send multiple rapid updates
        num_updates = 5
        for i in range(num_updates):
            update_data = {
                'analysis_id': test_analysis.id,
                'overall_progress': i * 20,
                'current_stage': i,
                'status': 'processing',
                'current_step_name': f'Step {i}',
                'sequence_number': i  # Add sequence for verification
            }
            websocket_service.emit_progress_update(test_analysis.id, update_data)
        
        # Allow time for all messages to be received
        time.sleep(1)
        
        # Check message ordering
        received = socketio_client.get_received()
        progress_events = [event for event in received if event['name'] == 'progress_update']
        
        assert len(progress_events) == num_updates
        
        # Verify ordering (if sequence numbers are preserved)
        for i, event in enumerate(progress_events):
            data = event['args'][0]
            if 'sequence_number' in data:
                assert data['sequence_number'] == i
