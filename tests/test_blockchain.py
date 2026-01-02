"""
Unit tests for Blockchain class.
"""

import unittest
import tempfile
import os
import time
from blockchain_voting.blockchain.blockchain import Blockchain
from blockchain_voting.blockchain.block import Block
from blockchain_voting.voting.vote import Vote


class TestBlockchain(unittest.TestCase):
    """Test cases for Blockchain class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.blockchain = Blockchain()
        self.sample_votes = [
            Vote("voter1", "Alice", time.time()),
            Vote("voter2", "Bob", time.time())
        ]
    
    def test_blockchain_initialization(self):
        """Test blockchain initialization with genesis block."""
        self.assertEqual(len(self.blockchain.chain), 1)
        genesis = self.blockchain.chain[0]
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.previous_hash, "0")
        self.assertEqual(len(genesis.votes), 0)
    
    def test_create_genesis_block(self):
        """Test genesis block creation."""
        genesis = self.blockchain.create_genesis_block()
        self.assertEqual(genesis.index, 0)
        self.assertEqual(genesis.previous_hash, "0")
        self.assertEqual(len(genesis.votes), 0)
        self.assertTrue(len(genesis.hash) == 64)  # SHA-256 produces 64-char hex
    
    def test_get_latest_block(self):
        """Test getting the latest block."""
        latest = self.blockchain.get_latest_block()
        self.assertEqual(latest.index, 0)  # Should be genesis block initially
        
        # Add a block and test again
        self.blockchain.add_block(self.sample_votes)
        latest = self.blockchain.get_latest_block()
        self.assertEqual(latest.index, 1)
    
    def test_add_block_success(self):
        """Test successfully adding a block."""
        initial_count = len(self.blockchain.chain)
        result = self.blockchain.add_block(self.sample_votes)
        
        self.assertTrue(result)
        self.assertEqual(len(self.blockchain.chain), initial_count + 1)
        
        new_block = self.blockchain.get_latest_block()
        self.assertEqual(new_block.index, 1)
        self.assertEqual(len(new_block.votes), 2)
        self.assertEqual(new_block.previous_hash, self.blockchain.chain[0].hash)
    
    def test_add_block_invalid_votes(self):
        """Test adding block with invalid votes."""
        result = self.blockchain.add_block("not a list")
        self.assertFalse(result)
        
        result = self.blockchain.add_block(["not a vote object"])
        self.assertFalse(result)
    
    def test_validate_chain_valid(self):
        """Test validation of a valid blockchain."""
        self.assertTrue(self.blockchain.validate_chain())
        
        # Add some blocks and validate
        self.blockchain.add_block(self.sample_votes)
        self.blockchain.add_block([Vote("voter3", "Charlie", time.time())])
        
        self.assertTrue(self.blockchain.validate_chain())
    
    def test_validate_chain_corrupted_hash(self):
        """Test validation fails with corrupted hash."""
        self.blockchain.add_block(self.sample_votes)
        
        # Corrupt a block's hash
        self.blockchain.chain[1].hash = "corrupted_hash"
        
        self.assertFalse(self.blockchain.validate_chain())
    
    def test_validate_chain_broken_linkage(self):
        """Test validation fails with broken linkage."""
        self.blockchain.add_block(self.sample_votes)
        
        # Break the linkage
        self.blockchain.chain[1].previous_hash = "wrong_hash"
        # Recalculate hash to make block internally consistent
        self.blockchain.chain[1].hash = self.blockchain.chain[1].calculate_hash()
        
        self.assertFalse(self.blockchain.validate_chain())
    
    def test_get_all_votes(self):
        """Test retrieving all votes from blockchain."""
        # Initially should be empty (genesis block has no votes)
        all_votes = self.blockchain.get_all_votes()
        self.assertEqual(len(all_votes), 0)
        
        # Add blocks with votes
        self.blockchain.add_block(self.sample_votes)
        more_votes = [Vote("voter3", "Charlie", time.time())]
        self.blockchain.add_block(more_votes)
        
        all_votes = self.blockchain.get_all_votes()
        self.assertEqual(len(all_votes), 3)  # 2 + 1 votes
    
    def test_get_block_count(self):
        """Test getting block count."""
        self.assertEqual(self.blockchain.get_block_count(), 1)  # Genesis block
        
        self.blockchain.add_block(self.sample_votes)
        self.assertEqual(self.blockchain.get_block_count(), 2)
    
    def test_get_block_by_index(self):
        """Test getting block by index."""
        genesis = self.blockchain.get_block_by_index(0)
        self.assertIsNotNone(genesis)
        self.assertEqual(genesis.index, 0)
        
        # Invalid index
        invalid_block = self.blockchain.get_block_by_index(10)
        self.assertIsNone(invalid_block)
        
        # Add block and test
        self.blockchain.add_block(self.sample_votes)
        block1 = self.blockchain.get_block_by_index(1)
        self.assertIsNotNone(block1)
        self.assertEqual(block1.index, 1)
    
    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization."""
        # Add some blocks
        self.blockchain.add_block(self.sample_votes)
        self.blockchain.add_block([Vote("voter3", "Charlie", time.time())])
        
        # Convert to dict
        blockchain_dict = self.blockchain.to_dict()
        self.assertIn('chain', blockchain_dict)
        self.assertEqual(len(blockchain_dict['chain']), 3)  # Genesis + 2 blocks
        
        # Reconstruct from dict
        reconstructed = Blockchain.from_dict(blockchain_dict)
        self.assertEqual(len(reconstructed.chain), len(self.blockchain.chain))
        self.assertTrue(reconstructed.validate_chain())
        
        # Compare vote counts
        original_votes = self.blockchain.get_all_votes()
        reconstructed_votes = reconstructed.get_all_votes()
        self.assertEqual(len(original_votes), len(reconstructed_votes))
    
    def test_save_and_load_file(self):
        """Test saving and loading blockchain from file."""
        # Add some blocks
        self.blockchain.add_block(self.sample_votes)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_filename = f.name
        
        try:
            # Save blockchain
            result = self.blockchain.save_to_file(temp_filename)
            self.assertTrue(result)
            self.assertTrue(os.path.exists(temp_filename))
            
            # Create new blockchain and load
            new_blockchain = Blockchain()
            # Clear the genesis block to test loading
            new_blockchain.chain = []
            
            result = new_blockchain.load_from_file(temp_filename)
            self.assertTrue(result)
            self.assertEqual(len(new_blockchain.chain), 2)  # Genesis + 1 block
            self.assertTrue(new_blockchain.validate_chain())
            
            # Compare votes
            original_votes = self.blockchain.get_all_votes()
            loaded_votes = new_blockchain.get_all_votes()
            self.assertEqual(len(original_votes), len(loaded_votes))
            
        finally:
            # Clean up
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file."""
        result = self.blockchain.load_from_file("nonexistent_file.json")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()