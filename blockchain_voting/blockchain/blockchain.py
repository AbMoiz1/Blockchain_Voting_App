"""
Blockchain class for managing the chain of blocks in the voting system.
"""

from typing import List, Dict, Any, Optional
import json
import os
from blockchain_voting.blockchain.block import Block
from blockchain_voting.voting.vote import Vote


class Blockchain:
    """
    Manages the blockchain for the voting system.
    
    Attributes:
        chain: List of blocks in the blockchain
    """
    
    def __init__(self):
        """Initialize blockchain with genesis block."""
        self.chain: List[Block] = []
        self.create_genesis_block()
    
    def create_genesis_block(self) -> Block:
        """
        Create the first block in the blockchain.
        
        Returns:
            The genesis block
        """
        genesis_block = Block.create_block(
            index=0,
            votes=[],  # Genesis block has no votes
            previous_hash="0"  # Genesis block has no previous hash
        )
        self.chain.append(genesis_block)
        return genesis_block
    
    def get_latest_block(self) -> Block:
        """
        Get the most recent block in the chain.
        
        Returns:
            The latest block
            
        Raises:
            IndexError: If blockchain is empty (should never happen after initialization)
        """
        if not self.chain:
            raise IndexError("Blockchain is empty")
        return self.chain[-1]
    
    def add_block(self, votes: List[Vote]) -> bool:
        """
        Add a new block to the blockchain with the given votes.
        
        Args:
            votes: List of votes to include in the new block
            
        Returns:
            True if block was added successfully, False otherwise
        """
        try:
            if not isinstance(votes, list):
                return False
            
            # Validate all votes are Vote instances
            for vote in votes:
                if not isinstance(vote, Vote):
                    return False
            
            latest_block = self.get_latest_block()
            new_index = latest_block.index + 1
            
            new_block = Block.create_block(
                index=new_index,
                votes=votes,
                previous_hash=latest_block.hash
            )
            
            self.chain.append(new_block)
            return True
            
        except Exception:
            return False
    
    def validate_chain(self) -> bool:
        """
        Validate the entire blockchain for integrity.
        
        Returns:
            True if blockchain is valid, False otherwise
        """
        try:
            if not self.chain:
                return False
            
            # Check genesis block
            genesis = self.chain[0]
            if genesis.index != 0 or genesis.previous_hash != "0":
                return False
            
            # Validate each block's hash
            if not genesis.validate_hash():
                return False
            
            # Check linkage between blocks
            for i in range(1, len(self.chain)):
                current_block = self.chain[i]
                previous_block = self.chain[i - 1]
                
                # Validate current block's hash
                if not current_block.validate_hash():
                    return False
                
                # Check if current block's previous_hash matches previous block's hash
                if current_block.previous_hash != previous_block.hash:
                    return False
                
                # Check if index is sequential
                if current_block.index != previous_block.index + 1:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def get_all_votes(self) -> List[Vote]:
        """
        Retrieve all votes from the entire blockchain.
        
        Returns:
            List of all votes across all blocks
        """
        all_votes = []
        for block in self.chain:
            all_votes.extend(block.votes)
        return all_votes
    
    def get_block_count(self) -> int:
        """
        Get the number of blocks in the blockchain.
        
        Returns:
            Number of blocks in the chain
        """
        return len(self.chain)
    
    def get_block_by_index(self, index: int) -> Optional[Block]:
        """
        Get a block by its index.
        
        Args:
            index: Index of the block to retrieve
            
        Returns:
            Block at the given index, or None if index is invalid
        """
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert blockchain to dictionary for serialization.
        
        Returns:
            Dictionary representation of the blockchain
        """
        return {
            'chain': [block.to_dict() for block in self.chain]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Blockchain':
        """
        Create Blockchain instance from dictionary.
        
        Args:
            data: Dictionary containing blockchain data
            
        Returns:
            Blockchain instance
            
        Raises:
            KeyError: If required keys are missing
            ValueError: If data is invalid
        """
        if 'chain' not in data:
            raise KeyError("Missing required key: chain")
        
        blockchain = cls.__new__(cls)  # Create instance without calling __init__
        blockchain.chain = []
        
        # Reconstruct blocks from dictionary data
        for block_data in data['chain']:
            block = Block.from_dict(block_data)
            blockchain.chain.append(block)
        
        return blockchain
    
    def save_to_file(self, filename: str) -> bool:
        """
        Save blockchain to a JSON file.
        
        Args:
            filename: Path to the file where blockchain should be saved
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            blockchain_dict = self.to_dict()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(blockchain_dict, f, indent=2, separators=(',', ': '))
            return True
        except Exception:
            return False
    
    def load_from_file(self, filename: str) -> bool:
        """
        Load blockchain from a JSON file.
        
        Args:
            filename: Path to the file containing blockchain data
            
        Returns:
            True if load was successful, False otherwise
        """
        try:
            if not os.path.exists(filename):
                return False
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            loaded_blockchain = self.from_dict(data)
            
            # Validate the loaded blockchain
            if not loaded_blockchain.validate_chain():
                return False
            
            # Replace current chain with loaded chain
            self.chain = loaded_blockchain.chain
            return True
            
        except Exception:
            return False