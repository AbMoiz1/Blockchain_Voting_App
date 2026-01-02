"""
Unit tests for VotingSystem class.
"""

import unittest
import tempfile
import os
from blockchain_voting.voting.voting_system import VotingSystem


class TestVotingSystem(unittest.TestCase):
    """Test cases for VotingSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.voting_system = VotingSystem()
    
    def test_voting_system_initialization(self):
        """Test VotingSystem initializes correctly."""
        self.assertIsNotNone(self.voting_system.blockchain)
        self.assertIsNotNone(self.voting_system.voter_manager)
        self.assertEqual(len(self.voting_system.pending_votes), 0)
        self.assertEqual(self.voting_system.blockchain.get_block_count(), 1)  # Genesis block
    
    def test_register_voter_success(self):
        """Test successful voter registration."""
        result = self.voting_system.register_voter("voter1")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["voter_id"], "voter1")
        self.assertIn("registered successfully", result["message"])
        self.assertIn("voter1", self.voting_system.get_registered_voters())
    
    def test_register_voter_duplicate(self):
        """Test duplicate voter registration is rejected."""
        # Register voter first time
        self.voting_system.register_voter("voter1")
        
        # Try to register same voter again
        result = self.voting_system.register_voter("voter1")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "DUPLICATE_VOTER")
        self.assertIn("already registered", result["message"])
    
    def test_register_voter_invalid_id(self):
        """Test invalid voter ID is rejected."""
        result = self.voting_system.register_voter("")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "INVALID_VOTER_ID")
    
    def test_cast_vote_success(self):
        """Test successful vote casting."""
        # Register voter first
        self.voting_system.register_voter("voter1")
        
        # Cast vote
        result = self.voting_system.cast_vote("voter1", "candidate_a")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["voter_id"], "voter1")
        self.assertEqual(result["candidate"], "candidate_a")
        self.assertIn("Vote cast successfully", result["message"])
        self.assertEqual(self.voting_system.get_pending_votes_count(), 1)
        self.assertIn("voter1", self.voting_system.get_voted_voters())
    
    def test_cast_vote_unregistered_voter(self):
        """Test vote casting by unregistered voter is rejected."""
        result = self.voting_system.cast_vote("unregistered", "candidate_a")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "UNREGISTERED_VOTER")
        self.assertIn("not registered", result["message"])
    
    def test_cast_vote_already_voted(self):
        """Test multiple votes by same voter are rejected."""
        # Register voter and cast first vote
        self.voting_system.register_voter("voter1")
        self.voting_system.cast_vote("voter1", "candidate_a")
        
        # Try to cast second vote
        result = self.voting_system.cast_vote("voter1", "candidate_b")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "ALREADY_VOTED")
        self.assertIn("already voted", result["message"])
    
    def test_create_block_from_pending_votes_success(self):
        """Test successful block creation from pending votes."""
        # Register voters and cast votes
        self.voting_system.register_voter("voter1")
        self.voting_system.register_voter("voter2")
        self.voting_system.cast_vote("voter1", "candidate_a")
        self.voting_system.cast_vote("voter2", "candidate_b")
        
        # Create block
        result = self.voting_system.create_block_from_pending_votes()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["votes_count"], 2)
        self.assertEqual(result["block_index"], 1)  # Genesis is 0, this is 1
        self.assertIn("Block created successfully", result["message"])
        self.assertEqual(self.voting_system.get_pending_votes_count(), 0)  # Pending votes cleared
        self.assertEqual(self.voting_system.blockchain.get_block_count(), 2)  # Genesis + new block
    
    def test_create_block_no_pending_votes(self):
        """Test block creation fails when no pending votes."""
        result = self.voting_system.create_block_from_pending_votes()
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "NO_PENDING_VOTES")
        self.assertIn("No pending votes", result["message"])
    
    def test_get_results_empty(self):
        """Test getting results when no votes cast."""
        result = self.voting_system.get_results()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["vote_counts"], {})
        self.assertEqual(result["total_votes"], 0)
        self.assertEqual(result["registered_voters"], 0)
        self.assertEqual(result["voted_voters"], 0)
        self.assertTrue(result["blockchain_valid"])
    
    def test_get_results_with_votes(self):
        """Test getting results with votes cast and mined."""
        # Register voters and cast votes
        self.voting_system.register_voter("voter1")
        self.voting_system.register_voter("voter2")
        self.voting_system.register_voter("voter3")
        self.voting_system.cast_vote("voter1", "candidate_a")
        self.voting_system.cast_vote("voter2", "candidate_a")
        self.voting_system.cast_vote("voter3", "candidate_b")
        
        # Create block to mine votes
        self.voting_system.create_block_from_pending_votes()
        
        # Get results
        result = self.voting_system.get_results()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["vote_counts"]["candidate_a"], 2)
        self.assertEqual(result["vote_counts"]["candidate_b"], 1)
        self.assertEqual(result["total_votes"], 3)
        self.assertEqual(result["registered_voters"], 3)
        self.assertEqual(result["voted_voters"], 3)
        self.assertTrue(result["blockchain_valid"])
        self.assertTrue(result["integrity_valid"])
    
    def test_validate_system_integrity(self):
        """Test system integrity validation."""
        # Register voter and cast vote
        self.voting_system.register_voter("voter1")
        self.voting_system.cast_vote("voter1", "candidate_a")
        
        result = self.voting_system.validate_system_integrity()
        
        self.assertTrue(result["success"])
        self.assertTrue(result["blockchain_valid"])
        self.assertTrue(result["integrity_valid"])
        self.assertEqual(result["total_blocks"], 1)  # Only genesis block
        self.assertEqual(result["total_votes"], 0)   # No votes mined yet
        self.assertEqual(result["pending_votes"], 1)
        self.assertEqual(result["registered_voters"], 1)
        self.assertEqual(result["voted_voters"], 1)
    
    def test_get_candidate_votes(self):
        """Test getting votes for specific candidate."""
        # Register voters and cast votes
        self.voting_system.register_voter("voter1")
        self.voting_system.register_voter("voter2")
        self.voting_system.cast_vote("voter1", "candidate_a")
        self.voting_system.cast_vote("voter2", "candidate_a")
        
        # Create block to mine votes
        self.voting_system.create_block_from_pending_votes()
        
        result = self.voting_system.get_candidate_votes("candidate_a")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["candidate"], "candidate_a")
        self.assertEqual(result["vote_count"], 2)
        self.assertEqual(len(result["votes"]), 2)
    
    def test_get_all_candidates(self):
        """Test getting all candidates."""
        # Register voters and cast votes
        self.voting_system.register_voter("voter1")
        self.voting_system.register_voter("voter2")
        self.voting_system.cast_vote("voter1", "candidate_b")
        self.voting_system.cast_vote("voter2", "candidate_a")
        
        # Create block to mine votes
        self.voting_system.create_block_from_pending_votes()
        
        candidates = self.voting_system.get_all_candidates()
        
        self.assertEqual(sorted(candidates), ["candidate_a", "candidate_b"])
    
    def test_get_vote_by_voter(self):
        """Test getting vote by specific voter."""
        # Register voter and cast vote
        self.voting_system.register_voter("voter1")
        self.voting_system.cast_vote("voter1", "candidate_a")
        
        # Create block to mine vote
        self.voting_system.create_block_from_pending_votes()
        
        result = self.voting_system.get_vote_by_voter("voter1")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["voter_id"], "voter1")
        self.assertTrue(result["has_voted"])
        self.assertEqual(result["vote"]["candidate"], "candidate_a")
        self.assertEqual(result["status"], "voted")
    
    def test_get_vote_by_voter_not_voted(self):
        """Test getting vote for voter who hasn't voted."""
        # Register voter but don't cast vote
        self.voting_system.register_voter("voter1")
        
        result = self.voting_system.get_vote_by_voter("voter1")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["voter_id"], "voter1")
        self.assertFalse(result["has_voted"])
        self.assertEqual(result["status"], "registered_not_voted")
    
    def test_get_vote_by_voter_unregistered(self):
        """Test getting vote for unregistered voter."""
        result = self.voting_system.get_vote_by_voter("unregistered")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "VOTER_NOT_REGISTERED")
    
    def test_save_and_load_state(self):
        """Test saving and loading system state."""
        # Set up some state
        self.voting_system.register_voter("voter1")
        self.voting_system.cast_vote("voter1", "candidate_a")
        self.voting_system.create_block_from_pending_votes()
        
        # Save state
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_filename = f.name
        
        try:
            save_result = self.voting_system.save_state(temp_filename)
            self.assertTrue(save_result["success"])
            
            # Create new voting system and load state
            new_voting_system = VotingSystem()
            load_result = new_voting_system.load_state(temp_filename)
            
            self.assertTrue(load_result["success"])
            
            # Verify state was loaded correctly
            self.assertEqual(len(new_voting_system.get_registered_voters()), 1)
            self.assertEqual(len(new_voting_system.get_voted_voters()), 1)
            self.assertEqual(new_voting_system.blockchain.get_block_count(), 2)  # Genesis + 1 block
            
            results = new_voting_system.get_results()
            self.assertEqual(results["vote_counts"]["candidate_a"], 1)
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_serialization_round_trip(self):
        """Test to_dict and from_dict methods."""
        # Set up some state
        self.voting_system.register_voter("voter1")
        self.voting_system.register_voter("voter2")
        self.voting_system.cast_vote("voter1", "candidate_a")
        
        # Convert to dict and back
        system_dict = self.voting_system.to_dict()
        new_voting_system = VotingSystem.from_dict(system_dict)
        
        # Verify state was preserved
        self.assertEqual(len(new_voting_system.get_registered_voters()), 2)
        self.assertEqual(len(new_voting_system.get_voted_voters()), 1)
        self.assertEqual(len(new_voting_system.get_pending_votes()), 1)
        self.assertEqual(new_voting_system.blockchain.get_block_count(), 1)  # Genesis block


if __name__ == '__main__':
    unittest.main()