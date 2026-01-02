"""
Unit tests for Vote class.
"""

import unittest
import time
from blockchain_voting.voting.vote import Vote


class TestVote(unittest.TestCase):
    """Test cases for Vote class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_voter_id = "voter123"
        self.valid_candidate = "Alice"
        self.valid_timestamp = time.time()
    
    def test_vote_creation(self):
        """Test creating a valid vote."""
        vote = Vote(self.valid_voter_id, self.valid_candidate, self.valid_timestamp)
        
        self.assertEqual(vote.voter_id, self.valid_voter_id)
        self.assertEqual(vote.candidate, self.valid_candidate)
        self.assertEqual(vote.timestamp, self.valid_timestamp)
    
    def test_vote_validation_empty_voter_id(self):
        """Test vote creation with empty voter_id raises ValueError."""
        with self.assertRaises(ValueError):
            Vote("", self.valid_candidate, self.valid_timestamp)
    
    def test_vote_validation_empty_candidate(self):
        """Test vote creation with empty candidate raises ValueError."""
        with self.assertRaises(ValueError):
            Vote(self.valid_voter_id, "", self.valid_timestamp)
    
    def test_vote_validation_invalid_timestamp(self):
        """Test vote creation with invalid timestamp raises ValueError."""
        with self.assertRaises(ValueError):
            Vote(self.valid_voter_id, self.valid_candidate, -1)
    
    def test_to_dict(self):
        """Test vote serialization to dictionary."""
        vote = Vote(self.valid_voter_id, self.valid_candidate, self.valid_timestamp)
        vote_dict = vote.to_dict()
        
        expected = {
            'voter_id': self.valid_voter_id,
            'candidate': self.valid_candidate,
            'timestamp': self.valid_timestamp
        }
        self.assertEqual(vote_dict, expected)
    
    def test_from_dict(self):
        """Test vote deserialization from dictionary."""
        vote_data = {
            'voter_id': self.valid_voter_id,
            'candidate': self.valid_candidate,
            'timestamp': self.valid_timestamp
        }
        vote = Vote.from_dict(vote_data)
        
        self.assertEqual(vote.voter_id, self.valid_voter_id)
        self.assertEqual(vote.candidate, self.valid_candidate)
        self.assertEqual(vote.timestamp, self.valid_timestamp)
    
    def test_from_dict_missing_keys(self):
        """Test vote deserialization with missing keys raises KeyError."""
        incomplete_data = {'voter_id': self.valid_voter_id}
        
        with self.assertRaises(KeyError):
            Vote.from_dict(incomplete_data)
    
    def test_create_vote(self):
        """Test creating vote with current timestamp."""
        before_time = time.time()
        vote = Vote.create_vote(self.valid_voter_id, self.valid_candidate)
        after_time = time.time()
        
        self.assertEqual(vote.voter_id, self.valid_voter_id)
        self.assertEqual(vote.candidate, self.valid_candidate)
        self.assertGreaterEqual(vote.timestamp, before_time)
        self.assertLessEqual(vote.timestamp, after_time)


if __name__ == '__main__':
    unittest.main()