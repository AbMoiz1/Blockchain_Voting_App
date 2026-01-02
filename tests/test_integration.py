"""
Integration tests for blockchain voting system.

Tests complete user workflows end-to-end, verifying that the core voting system
components work together properly. Tests all functionality through direct system
calls and validates the complete voting process from registration to results.
"""

import unittest
import json
import tempfile
import os
import time
from blockchain_voting.voting.voting_system import VotingSystem


class TestIntegrationWorkflows(unittest.TestCase):
    """Integration tests for complete voting workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.voting_system = VotingSystem()
    
    def tearDown(self):
        """Clean up after tests."""
        pass
    
    def test_complete_voting_workflow(self):
        """Test complete voting workflow from registration to results."""
        # Step 1: Verify system starts in clean state
        self.assertEqual(len(self.voting_system.voter_manager.get_registered_voters()), 0)
        self.assertEqual(len(self.voting_system.pending_votes), 0)
        self.assertEqual(len(self.voting_system.blockchain.chain), 1)  # Genesis block
        
        # Step 2: Register multiple voters
        voters = ['alice', 'bob', 'charlie', 'diana', 'eve']
        for voter_id in voters:
            result = self.voting_system.register_voter(voter_id)
            self.assertTrue(result['success'])
            self.assertEqual(result['message'], f"Voter {voter_id} registered successfully")
        
        # Step 3: Verify all voters are registered
        registered_voters = self.voting_system.voter_manager.get_registered_voters()
        self.assertEqual(len(registered_voters), 5)
        voted_voters = self.voting_system.voter_manager.get_voted_voters()
        self.assertEqual(len(voted_voters), 0)
        self.assertEqual(set(registered_voters), set(voters))
        
        # Step 4: Cast votes for different candidates
        votes = [
            ('alice', 'Candidate A'),
            ('bob', 'Candidate B'),
            ('charlie', 'Candidate A'),
            ('diana', 'Candidate C'),
            ('eve', 'Candidate A')
        ]
        
        for voter_id, candidate in votes:
            result = self.voting_system.cast_vote(voter_id, candidate)
            self.assertTrue(result['success'])
            self.assertEqual(result['voter_id'], voter_id)
            self.assertEqual(result['candidate'], candidate)
        
        # Step 5: Verify pending votes status
        self.assertEqual(len(self.voting_system.pending_votes), 5)
        voted_voters = self.voting_system.voter_manager.get_voted_voters()
        self.assertEqual(len(voted_voters), 5)
        
        # Step 6: Create block from pending votes
        result = self.voting_system.create_block_from_pending_votes()
        self.assertTrue(result['success'])
        self.assertEqual(result['votes_count'], 5)
        self.assertEqual(result['block_index'], 1)  # First block after genesis
        
        # Step 7: Verify system state after block creation
        self.assertEqual(len(self.voting_system.pending_votes), 0)
        total_votes = len(self.voting_system.blockchain.get_all_votes())
        self.assertEqual(total_votes, 5)
        self.assertEqual(len(self.voting_system.blockchain.chain), 2)  # Genesis + 1 vote block
        
        # Step 8: Get and verify results
        result = self.voting_system.get_results()
        self.assertTrue(result['success'])
        
        # Expected vote counts
        expected_counts = {'Candidate A': 3, 'Candidate B': 1, 'Candidate C': 1}
        self.assertEqual(result['vote_counts'], expected_counts)
        self.assertEqual(result['total_votes'], 5)
        self.assertEqual(result['total_blocks'], 2)
        self.assertTrue(result['blockchain_valid'])
        
        # Step 9: Validate system integrity
        integrity_result = self.voting_system.validate_system_integrity()
        self.assertTrue(integrity_result['blockchain_valid'])
        self.assertEqual(integrity_result['total_blocks'], 2)
        self.assertEqual(integrity_result['total_votes'], 5)
        
        # Step 10: Verify individual voter information
        for voter_id, expected_candidate in votes:
            vote = self.voting_system.get_vote_by_voter(voter_id)
            self.assertTrue(vote['success'])
            self.assertEqual(vote['voter_id'], voter_id)
            self.assertTrue(self.voting_system.voter_manager.has_voted(voter_id))
            self.assertEqual(vote['vote']['candidate'], expected_candidate)
        
        # Step 11: Verify candidate information
        for candidate in ['Candidate A', 'Candidate B', 'Candidate C']:
            candidate_votes = self.voting_system.get_candidate_votes(candidate)
            self.assertTrue(candidate_votes['success'])
            self.assertEqual(candidate_votes['candidate'], candidate)
            self.assertEqual(candidate_votes['vote_count'], expected_counts[candidate])
    
    def test_multiple_block_creation_workflow(self):
        """Test workflow with multiple block creations."""
        # Register voters
        voters = [f'voter_{i}' for i in range(10)]
        for voter_id in voters:
            result = self.voting_system.register_voter(voter_id)
            self.assertTrue(result['success'])
        
        # Cast first batch of votes
        first_batch = voters[:5]
        for voter_id in first_batch:
            result = self.voting_system.cast_vote(voter_id, 'Alice')
            self.assertTrue(result['success'])
        
        # Create first block
        result = self.voting_system.create_block_from_pending_votes()
        self.assertTrue(result['success'])
        self.assertEqual(result['votes_count'], 5)
        self.assertEqual(result['block_index'], 1)
        
        # Cast second batch of votes
        second_batch = voters[5:]
        for voter_id in second_batch:
            result = self.voting_system.cast_vote(voter_id, 'Bob')
            self.assertTrue(result['success'])
        
        # Create second block
        result = self.voting_system.create_block_from_pending_votes()
        self.assertTrue(result['success'])
        self.assertEqual(result['votes_count'], 5)
        self.assertEqual(result['block_index'], 2)
        
        # Verify final state
        self.assertEqual(len(self.voting_system.pending_votes), 0)
        self.assertEqual(len(self.voting_system.blockchain.chain), 3)  # Genesis + 2 vote blocks
        
        # Verify results
        result = self.voting_system.get_results()
        self.assertTrue(result['success'])
        self.assertEqual(result['vote_counts'], {'Alice': 5, 'Bob': 5})
        self.assertEqual(result['total_votes'], 10)
        self.assertEqual(result['total_blocks'], 3)
        self.assertTrue(result['blockchain_valid'])
    
    def test_error_handling_workflow(self):
        """Test error handling in realistic workflow scenarios."""
        # Test duplicate voter registration
        result = self.voting_system.register_voter('test_voter')
        self.assertTrue(result['success'])
        
        result = self.voting_system.register_voter('test_voter')
        self.assertFalse(result['success'])
        self.assertIn('already registered', result['message'])
        
        # Test voting by unregistered voter
        result = self.voting_system.cast_vote('unregistered_voter', 'Candidate A')
        self.assertFalse(result['success'])
        self.assertIn('not registered', result['message'])
        
        # Test double voting
        result = self.voting_system.cast_vote('test_voter', 'Candidate A')
        self.assertTrue(result['success'])
        
        result = self.voting_system.cast_vote('test_voter', 'Candidate B')
        self.assertFalse(result['success'])
        self.assertIn('already voted', result['message'])
        
        # Test block creation with no pending votes
        result = self.voting_system.create_block_from_pending_votes()
        self.assertTrue(result['success'])  # Should create block with the one vote
        
        result = self.voting_system.create_block_from_pending_votes()
        self.assertFalse(result['success'])  # Should fail with no pending votes
        self.assertIn('No pending votes', result['message'])
    
    def test_persistence_workflow(self):
        """Test data persistence workflow with save and load operations."""
        # Set up initial state
        voters = ['alice', 'bob', 'charlie']
        for voter_id in voters:
            result = self.voting_system.register_voter(voter_id)
            self.assertTrue(result['success'])
        
        # Cast some votes
        votes = [('alice', 'Candidate A'), ('bob', 'Candidate B')]
        for voter_id, candidate in votes:
            result = self.voting_system.cast_vote(voter_id, candidate)
            self.assertTrue(result['success'])
        
        # Create block
        result = self.voting_system.create_block_from_pending_votes()
        self.assertTrue(result['success'])
        
        # Save state to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_filename = f.name
        
        try:
            success = self.voting_system.save_state(temp_filename)
            self.assertTrue(success)
            
            # Create new voting system and load state
            new_voting_system = VotingSystem()
            success = new_voting_system.load_state(temp_filename)
            self.assertTrue(success)
            
            # Verify loaded state matches original
            self.assertEqual(
                set(new_voting_system.voter_manager.get_registered_voters()),
                set(voters)
            )
            self.assertEqual(
                len(new_voting_system.blockchain.get_all_votes()),
                2
            )
            self.assertEqual(
                len(new_voting_system.blockchain.chain),
                2  # Genesis + 1 vote block
            )
            
            # Verify blockchain integrity after loading
            self.assertTrue(new_voting_system.blockchain.validate_chain())
            
            # Verify results match
            original_results = self.voting_system.get_results()
            loaded_results = new_voting_system.get_results()
            
            self.assertEqual(original_results['vote_counts'], loaded_results['vote_counts'])
            self.assertEqual(original_results['total_votes'], loaded_results['total_votes'])
            self.assertEqual(original_results['total_blocks'], loaded_results['total_blocks'])
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_concurrent_operations_workflow(self):
        """Test workflow simulating concurrent operations."""
        # Register multiple voters
        voters = [f'voter_{i}' for i in range(20)]
        for voter_id in voters:
            result = self.voting_system.register_voter(voter_id)
            self.assertTrue(result['success'])
        
        # Simulate concurrent voting (in reality, this would be sequential due to GIL)
        candidates = ['Alice', 'Bob', 'Charlie', 'Diana']
        for i, voter_id in enumerate(voters):
            candidate = candidates[i % len(candidates)]
            result = self.voting_system.cast_vote(voter_id, candidate)
            self.assertTrue(result['success'])
        
        # Verify all votes are pending
        self.assertEqual(len(self.voting_system.pending_votes), 20)
        
        # Create block with all votes
        result = self.voting_system.create_block_from_pending_votes()
        self.assertTrue(result['success'])
        self.assertEqual(result['votes_count'], 20)
        
        # Verify results
        result = self.voting_system.get_results()
        self.assertTrue(result['success'])
        self.assertEqual(result['total_votes'], 20)
        
        # Each candidate should have 5 votes (20 voters / 4 candidates)
        for candidate in candidates:
            self.assertEqual(result['vote_counts'][candidate], 5)
        
        # Verify blockchain integrity
        self.assertTrue(result['blockchain_valid'])
    
    def test_system_restart_simulation(self):
        """Test complete system restart scenarios with persistence."""
        # Phase 1: Initial setup and voting
        voters = ['alice', 'bob', 'charlie', 'diana']
        for voter_id in voters:
            result = self.voting_system.register_voter(voter_id)
            self.assertTrue(result['success'])
        
        # Cast votes
        for voter_id in voters:
            result = self.voting_system.cast_vote(voter_id, 'Candidate A')
            self.assertTrue(result['success'])
        
        # Create block
        result = self.voting_system.create_block_from_pending_votes()
        self.assertTrue(result['success'])
        
        # Save state
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_filename = f.name
        
        try:
            success = self.voting_system.save_state(temp_filename)
            self.assertTrue(success)
            
            # Phase 2: Simulate system restart
            del self.voting_system
            self.voting_system = VotingSystem()
            
            # Load previous state
            success = self.voting_system.load_state(temp_filename)
            self.assertTrue(success)
            
            # Phase 3: Continue operations after restart
            # Register new voter
            result = self.voting_system.register_voter('eve')
            self.assertTrue(result['success'])
            
            # New voter votes
            result = self.voting_system.cast_vote('eve', 'Candidate B')
            self.assertTrue(result['success'])
            
            # Create another block
            result = self.voting_system.create_block_from_pending_votes()
            self.assertTrue(result['success'])
            
            # Verify final state
            result = self.voting_system.get_results()
            self.assertTrue(result['success'])
            self.assertEqual(result['vote_counts'], {'Candidate A': 4, 'Candidate B': 1})
            self.assertEqual(result['total_votes'], 5)
            self.assertEqual(result['total_blocks'], 3)  # Genesis + 2 vote blocks
            self.assertTrue(result['blockchain_valid'])
            
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_cross_session_data_integrity(self):
        """Test data integrity across multiple sessions with complex workflows."""
        temp_files = []
        
        try:
            # Session 1: Initial voting
            session1_voters = ['voter1', 'voter2', 'voter3']
            for voter_id in session1_voters:
                result = self.voting_system.register_voter(voter_id)
                self.assertTrue(result['success'])
            
            for voter_id in session1_voters:
                result = self.voting_system.cast_vote(voter_id, 'Alice')
                self.assertTrue(result['success'])
            
            result = self.voting_system.create_block_from_pending_votes()
            self.assertTrue(result['success'])
            
            # Save session 1
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                session1_file = f.name
                temp_files.append(session1_file)
            
            success = self.voting_system.save_state(session1_file)
            self.assertTrue(success)
            
            # Session 2: Load and continue
            self.voting_system = VotingSystem()
            success = self.voting_system.load_state(session1_file)
            self.assertTrue(success)
            
            session2_voters = ['voter4', 'voter5']
            for voter_id in session2_voters:
                result = self.voting_system.register_voter(voter_id)
                self.assertTrue(result['success'])
            
            for voter_id in session2_voters:
                result = self.voting_system.cast_vote(voter_id, 'Bob')
                self.assertTrue(result['success'])
            
            result = self.voting_system.create_block_from_pending_votes()
            self.assertTrue(result['success'])
            
            # Save session 2
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                session2_file = f.name
                temp_files.append(session2_file)
            
            success = self.voting_system.save_state(session2_file)
            self.assertTrue(success)
            
            # Session 3: Final verification
            self.voting_system = VotingSystem()
            success = self.voting_system.load_state(session2_file)
            self.assertTrue(success)
            
            # Verify complete state
            all_voters = session1_voters + session2_voters
            registered_voters = self.voting_system.voter_manager.get_registered_voters()
            self.assertEqual(set(registered_voters), set(all_voters))
            
            result = self.voting_system.get_results()
            self.assertTrue(result['success'])
            self.assertEqual(result['vote_counts'], {'Alice': 3, 'Bob': 2})
            self.assertEqual(result['total_votes'], 5)
            self.assertEqual(result['total_blocks'], 3)  # Genesis + 2 vote blocks
            self.assertTrue(result['blockchain_valid'])
            
            # Verify blockchain integrity across all sessions
            integrity_result = self.voting_system.validate_system_integrity()
            self.assertTrue(integrity_result['blockchain_valid'])
            
        finally:
            # Clean up all temporary files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    def test_multiple_restart_cycles(self):
        """Test multiple save/restart/load cycles to ensure data integrity."""
        temp_files = []
        
        try:
            # Cycle through multiple restart scenarios
            for cycle in range(3):
                # Register voters for this cycle
                cycle_voters = [f'cycle{cycle}_voter{i}' for i in range(3)]
                for voter_id in cycle_voters:
                    result = self.voting_system.register_voter(voter_id)
                    self.assertTrue(result['success'])
                
                # Cast votes
                for voter_id in cycle_voters:
                    result = self.voting_system.cast_vote(voter_id, f'Candidate_{cycle}')
                    self.assertTrue(result['success'])
                
                # Create block
                result = self.voting_system.create_block_from_pending_votes()
                self.assertTrue(result['success'])
                
                # Save state
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                    cycle_file = f.name
                    temp_files.append(cycle_file)
                
                success = self.voting_system.save_state(cycle_file)
                self.assertTrue(success)
                
                # Restart system
                self.voting_system = VotingSystem()
                success = self.voting_system.load_state(cycle_file)
                self.assertTrue(success)
                
                # Verify state after restart
                result = self.voting_system.get_results()
                self.assertTrue(result['success'])
                self.assertEqual(result['total_votes'], (cycle + 1) * 3)
                self.assertEqual(result['total_blocks'], cycle + 2)  # Genesis + vote blocks
                self.assertTrue(result['blockchain_valid'])
            
            # Final verification
            result = self.voting_system.get_results()
            expected_counts = {'Candidate_0': 3, 'Candidate_1': 3, 'Candidate_2': 3}
            self.assertEqual(result['vote_counts'], expected_counts)
            self.assertEqual(result['total_votes'], 9)
            self.assertEqual(result['total_blocks'], 4)  # Genesis + 3 vote blocks
            
        finally:
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
    
    def test_persistence_error_recovery(self):
        """Test system behavior when persistence operations fail or encounter errors."""
        # Test saving to invalid path
        result = self.voting_system.save_state('/invalid/path/file.json')
        self.assertFalse(result['success'] if isinstance(result, dict) else result)
        
        # Test loading from non-existent file
        result = self.voting_system.load_state('non_existent_file.json')
        self.assertFalse(result['success'] if isinstance(result, dict) else result)
        
        # System should still be functional after failed operations
        result = self.voting_system.register_voter('test_voter')
        self.assertTrue(result['success'])
        
        result = self.voting_system.cast_vote('test_voter', 'Test Candidate')
        self.assertTrue(result['success'])
        
        result = self.voting_system.create_block_from_pending_votes()
        self.assertTrue(result['success'])
        
        # Verify system integrity after failed persistence operations
        integrity_result = self.voting_system.validate_system_integrity()
        self.assertTrue(integrity_result['blockchain_valid'])


if __name__ == '__main__':
    unittest.main()