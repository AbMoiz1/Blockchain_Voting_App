"""
VotingSystem class for orchestrating the entire voting process.
"""

from typing import List, Dict, Any, Optional
import time
import json
import os
from blockchain_voting.blockchain.blockchain import Blockchain
from blockchain_voting.voting.voter_manager import VoterManager
from blockchain_voting.voting.vote import Vote


class VotingSystem:
    """
    Orchestrates the entire voting process by coordinating blockchain and voter management.
    
    Manages voter registration, vote casting, pending votes, block creation, and results.
    """
    
    def __init__(self):
        """Initialize VotingSystem with blockchain and voter manager."""
        self.blockchain = Blockchain()
        self.voter_manager = VoterManager()
        self.pending_votes: List[Vote] = []
    
    def register_voter(self, voter_id: str) -> Dict[str, Any]:
        """
        Register a new voter with unique ID validation.
        
        Args:
            voter_id: Unique identifier for the voter
            
        Returns:
            Dictionary with success status and message
        """
        try:
            if self.voter_manager.register_voter(voter_id):
                return {
                    "success": True,
                    "message": f"Voter {voter_id} registered successfully",
                    "voter_id": voter_id
                }
            else:
                return {
                    "success": False,
                    "error": "DUPLICATE_VOTER",
                    "message": f"Voter {voter_id} is already registered"
                }
        except ValueError as e:
            return {
                "success": False,
                "error": "INVALID_VOTER_ID",
                "message": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": "REGISTRATION_ERROR",
                "message": f"Failed to register voter: {str(e)}"
            }
    
    def cast_vote(self, voter_id: str, candidate: str) -> Dict[str, Any]:
        """
        Cast a vote with validation for registered voters and one-vote-per-voter policy.
        
        Args:
            voter_id: ID of the voter casting the vote
            candidate: The candidate being voted for
            
        Returns:
            Dictionary with success status and message
        """
        try:
            # Validate voter is registered
            if not self.voter_manager.is_registered(voter_id):
                return {
                    "success": False,
                    "error": "UNREGISTERED_VOTER",
                    "message": f"Voter {voter_id} is not registered"
                }
            
            # Check if voter has already voted
            if self.voter_manager.has_voted(voter_id):
                return {
                    "success": False,
                    "error": "ALREADY_VOTED",
                    "message": f"Voter {voter_id} has already voted"
                }
            
            # Create and add vote to pending votes
            vote = Vote.create_vote(voter_id, candidate)
            self.pending_votes.append(vote)
            
            # Mark voter as having voted
            self.voter_manager.mark_as_voted(voter_id)
            
            return {
                "success": True,
                "message": f"Vote cast successfully for {candidate}",
                "voter_id": voter_id,
                "candidate": candidate,
                "timestamp": vote.timestamp
            }
            
        except ValueError as e:
            return {
                "success": False,
                "error": "INVALID_VOTE_DATA",
                "message": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "error": "VOTE_CASTING_ERROR",
                "message": f"Failed to cast vote: {str(e)}"
            }
    
    def create_block_from_pending_votes(self) -> Dict[str, Any]:
        """
        Create a new block from pending votes and add it to the blockchain.
        
        Returns:
            Dictionary with success status and block information
        """
        try:
            if not self.pending_votes:
                return {
                    "success": False,
                    "error": "NO_PENDING_VOTES",
                    "message": "No pending votes to create a block"
                }
            
            # Create a copy of pending votes for the block
            votes_for_block = self.pending_votes.copy()
            
            # Add block to blockchain
            if self.blockchain.add_block(votes_for_block):
                # Clear pending votes after successful block creation
                vote_count = len(self.pending_votes)
                self.pending_votes.clear()
                
                latest_block = self.blockchain.get_latest_block()
                
                return {
                    "success": True,
                    "message": f"Block created successfully with {vote_count} votes",
                    "block_index": latest_block.index,
                    "block_hash": latest_block.hash,
                    "votes_count": vote_count,
                    "timestamp": latest_block.timestamp
                }
            else:
                return {
                    "success": False,
                    "error": "BLOCK_CREATION_FAILED",
                    "message": "Failed to add block to blockchain"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": "BLOCK_CREATION_ERROR",
                "message": f"Error creating block: {str(e)}"
            }
    
    def get_pending_votes_count(self) -> int:
        """
        Get the number of pending votes waiting to be mined into a block.
        
        Returns:
            Number of pending votes
        """
        return len(self.pending_votes)
    
    def get_pending_votes(self) -> List[Vote]:
        """
        Get a copy of all pending votes.
        
        Returns:
            List of pending votes
        """
        return self.pending_votes.copy()
    
    def get_registered_voters(self) -> List[str]:
        """
        Get list of all registered voter IDs.
        
        Returns:
            List of registered voter IDs
        """
        return self.voter_manager.get_registered_voters()
    
    def get_voted_voters(self) -> List[str]:
        """
        Get list of all voters who have voted.
        
        Returns:
            List of voter IDs who have voted
        """
        return self.voter_manager.get_voted_voters()
    
    def validate_system_integrity(self) -> Dict[str, Any]:
        """
        Validate the integrity of the entire voting system.
        
        Returns:
            Dictionary with validation results
        """
        try:
            blockchain_valid = self.blockchain.validate_chain()
            
            # Additional integrity checks
            all_votes = self.blockchain.get_all_votes()
            voted_voters = set(self.voter_manager.get_voted_voters())
            blockchain_voters = set(vote.voter_id for vote in all_votes)
            
            # Check if all voters in blockchain are marked as voted
            integrity_issues = []
            
            # Voters in blockchain but not marked as voted
            unmarked_voters = blockchain_voters - voted_voters
            if unmarked_voters:
                integrity_issues.append(f"Voters in blockchain but not marked as voted: {unmarked_voters}")
            
            # Voters marked as voted but not in blockchain (considering pending votes)
            pending_voters = set(vote.voter_id for vote in self.pending_votes)
            all_voting_voters = blockchain_voters | pending_voters
            extra_voted_voters = voted_voters - all_voting_voters
            if extra_voted_voters:
                integrity_issues.append(f"Voters marked as voted but no votes found: {extra_voted_voters}")
            
            return {
                "success": True,
                "blockchain_valid": blockchain_valid,
                "integrity_valid": len(integrity_issues) == 0,
                "issues": integrity_issues,
                "total_blocks": self.blockchain.get_block_count(),
                "total_votes": len(all_votes),
                "pending_votes": len(self.pending_votes),
                "registered_voters": len(self.get_registered_voters()),
                "voted_voters": len(self.get_voted_voters())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": f"Error validating system: {str(e)}"
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert VotingSystem state to dictionary for serialization.
        
        Returns:
            Dictionary representation of the voting system state
        """
        return {
            'blockchain': self.blockchain.to_dict(),
            'voter_manager': self.voter_manager.to_dict(),
            'pending_votes': [vote.to_dict() for vote in self.pending_votes]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VotingSystem':
        """
        Create VotingSystem instance from dictionary.
        
        Args:
            data: Dictionary containing voting system state
            
        Returns:
            VotingSystem instance
            
        Raises:
            KeyError: If required keys are missing
            ValueError: If data is invalid
        """
        required_keys = {'blockchain', 'voter_manager', 'pending_votes'}
        if not all(key in data for key in required_keys):
            missing = required_keys - set(data.keys())
            raise KeyError(f"Missing required keys: {missing}")
        
        voting_system = cls.__new__(cls)  # Create instance without calling __init__
        
        # Reconstruct components
        voting_system.blockchain = Blockchain.from_dict(data['blockchain'])
        voting_system.voter_manager = VoterManager.from_dict(data['voter_manager'])
        
        # Reconstruct pending votes
        voting_system.pending_votes = []
        for vote_data in data['pending_votes']:
            vote = Vote.from_dict(vote_data)
            voting_system.pending_votes.append(vote)
        
        return voting_system
    
    def save_state(self, filename: str) -> Dict[str, Any]:
        """
        Save the entire voting system state to a JSON file.
        
        Args:
            filename: Path to the file where state should be saved
            
        Returns:
            Dictionary with success status and message
        """
        try:
            system_dict = self.to_dict()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(system_dict, f, indent=2, separators=(',', ': '))
            
            return {
                "success": True,
                "message": f"System state saved to {filename}",
                "filename": filename
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "SAVE_ERROR",
                "message": f"Failed to save system state: {str(e)}"
            }
    
    def load_state(self, filename: str) -> Dict[str, Any]:
        """
        Load voting system state from a JSON file.
        
        Args:
            filename: Path to the file containing system state
            
        Returns:
            Dictionary with success status and message
        """
        try:
            if not os.path.exists(filename):
                return {
                    "success": False,
                    "error": "FILE_NOT_FOUND",
                    "message": f"File {filename} does not exist"
                }
            
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            loaded_system = self.from_dict(data)
            
            # Validate the loaded system
            validation_result = loaded_system.validate_system_integrity()
            if not validation_result.get('blockchain_valid', False):
                return {
                    "success": False,
                    "error": "INVALID_BLOCKCHAIN",
                    "message": "Loaded blockchain is invalid"
                }
            
            # Replace current state with loaded state
            self.blockchain = loaded_system.blockchain
            self.voter_manager = loaded_system.voter_manager
            self.pending_votes = loaded_system.pending_votes
            
            return {
                "success": True,
                "message": f"System state loaded from {filename}",
                "filename": filename,
                "validation": validation_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "LOAD_ERROR",
                "message": f"Failed to load system state: {str(e)}"
            }
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get vote counting results across the entire blockchain with validation status.
        
        Returns:
            Dictionary with vote counts, totals, and validation status
        """
        try:
            # Get all votes from blockchain
            all_votes = self.blockchain.get_all_votes()
            
            # Count votes by candidate
            vote_counts = {}
            for vote in all_votes:
                candidate = vote.candidate
                if candidate in vote_counts:
                    vote_counts[candidate] += 1
                else:
                    vote_counts[candidate] = 1
            
            # Calculate total votes
            total_votes = sum(vote_counts.values())
            
            # Get validation status
            validation_result = self.validate_system_integrity()
            
            # Get additional statistics
            registered_count = len(self.get_registered_voters())
            voted_count = len(self.get_voted_voters())
            pending_count = len(self.pending_votes)
            
            return {
                "success": True,
                "vote_counts": vote_counts,
                "total_votes": total_votes,
                "registered_voters": registered_count,
                "voted_voters": voted_count,
                "pending_votes": pending_count,
                "blockchain_valid": validation_result.get('blockchain_valid', False),
                "integrity_valid": validation_result.get('integrity_valid', False),
                "total_blocks": self.blockchain.get_block_count(),
                "validation_issues": validation_result.get('issues', [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "RESULTS_ERROR",
                "message": f"Error calculating results: {str(e)}"
            }
    
    def get_candidate_votes(self, candidate: str) -> Dict[str, Any]:
        """
        Get detailed vote information for a specific candidate.
        
        Args:
            candidate: The candidate to get votes for
            
        Returns:
            Dictionary with candidate vote details
        """
        try:
            all_votes = self.blockchain.get_all_votes()
            candidate_votes = [vote for vote in all_votes if vote.candidate == candidate]
            
            return {
                "success": True,
                "candidate": candidate,
                "vote_count": len(candidate_votes),
                "votes": [vote.to_dict() for vote in candidate_votes]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "CANDIDATE_VOTES_ERROR",
                "message": f"Error getting votes for candidate {candidate}: {str(e)}"
            }
    
    def get_all_candidates(self) -> List[str]:
        """
        Get list of all candidates that have received votes.
        
        Returns:
            List of candidate names (sorted)
        """
        try:
            all_votes = self.blockchain.get_all_votes()
            candidates = set(vote.candidate for vote in all_votes)
            return sorted(list(candidates))
        except Exception:
            return []
    
    def get_vote_by_voter(self, voter_id: str) -> Dict[str, Any]:
        """
        Get the vote cast by a specific voter.
        
        Args:
            voter_id: The voter ID to look up
            
        Returns:
            Dictionary with voter's vote information
        """
        try:
            all_votes = self.blockchain.get_all_votes()
            voter_votes = [vote for vote in all_votes if vote.voter_id == voter_id]
            
            if not voter_votes:
                # Check if voter is registered but hasn't voted
                if self.voter_manager.is_registered(voter_id):
                    if self.voter_manager.has_voted(voter_id):
                        # Check pending votes
                        pending_votes = [vote for vote in self.pending_votes if vote.voter_id == voter_id]
                        if pending_votes:
                            return {
                                "success": True,
                                "voter_id": voter_id,
                                "has_voted": True,
                                "vote": pending_votes[0].to_dict(),
                                "status": "pending"
                            }
                        else:
                            return {
                                "success": False,
                                "error": "VOTE_NOT_FOUND",
                                "message": f"Vote for voter {voter_id} not found despite being marked as voted"
                            }
                    else:
                        return {
                            "success": True,
                            "voter_id": voter_id,
                            "has_voted": False,
                            "status": "registered_not_voted"
                        }
                else:
                    return {
                        "success": False,
                        "error": "VOTER_NOT_REGISTERED",
                        "message": f"Voter {voter_id} is not registered"
                    }
            
            # Should only be one vote per voter
            if len(voter_votes) > 1:
                return {
                    "success": False,
                    "error": "MULTIPLE_VOTES_FOUND",
                    "message": f"Multiple votes found for voter {voter_id} - system integrity compromised"
                }
            
            return {
                "success": True,
                "voter_id": voter_id,
                "has_voted": True,
                "vote": voter_votes[0].to_dict(),
                "status": "voted"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": "VOTER_LOOKUP_ERROR",
                "message": f"Error looking up vote for voter {voter_id}: {str(e)}"
            }