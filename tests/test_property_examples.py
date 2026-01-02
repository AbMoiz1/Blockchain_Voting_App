"""
Example property-based tests using hypothesis.
This demonstrates the testing framework setup for future property tests.
"""

import unittest
from hypothesis import given, strategies as st
from blockchain_voting.voting.vote import Vote
from blockchain_voting.blockchain.block import Block
from blockchain_voting.blockchain.blockchain import Blockchain
from blockchain_voting.voting.voting_system import VotingSystem


class TestPropertyExamples(unittest.TestCase):
    """Example property-based tests to verify framework setup."""
    
    @given(
        voter_id=st.text(min_size=1, max_size=50),
        candidate=st.text(min_size=1, max_size=50),
        timestamp=st.floats(min_value=1.0, max_value=2147483647.0)
    )
    def test_vote_serialization_round_trip(self, voter_id, candidate, timestamp):
        """
        Property 10: Data Persistence Round Trip (Vote component)
        Feature: blockchain-voting, Property 10: Data Persistence Round Trip (Vote component)
        Validates: Requirements 7.1, 7.2
        """
        # Create vote
        vote = Vote(voter_id, candidate, timestamp)
        
        # Serialize to dict and back
        vote_dict = vote.to_dict()
        reconstructed_vote = Vote.from_dict(vote_dict)
        
        # Should be identical
        self.assertEqual(vote.voter_id, reconstructed_vote.voter_id)
        self.assertEqual(vote.candidate, reconstructed_vote.candidate)
        self.assertEqual(vote.timestamp, reconstructed_vote.timestamp)
    
    @given(
        index=st.integers(min_value=0, max_value=1000),
        timestamp=st.floats(min_value=1.0, max_value=2147483647.0),
        previous_hash=st.text(min_size=64, max_size=64, alphabet='0123456789abcdef'),
        votes=st.lists(
            st.builds(
                Vote,
                voter_id=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                candidate=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                timestamp=st.floats(min_value=1.0, max_value=2147483647.0)
            ),
            min_size=0,
            max_size=10
        )
    )
    def test_block_hash_consistency_property_5(self, index, timestamp, previous_hash, votes):
        """
        Property 5: Block Hash Consistency
        Feature: blockchain-voting, Property 5: Block Hash Consistency
        Validates: Requirements 4.1, 4.3
        
        For any block data, calculating the hash multiple times should always produce 
        the same result, and the hash should include the previous block's hash.
        """
        # Create block with generated data
        block = Block(index, timestamp, votes, previous_hash)
        
        # Test 1: Hash calculation should be deterministic
        hash1 = block.calculate_hash()
        hash2 = block.calculate_hash()
        hash3 = block.calculate_hash()
        
        self.assertEqual(hash1, hash2)
        self.assertEqual(hash2, hash3)
        self.assertEqual(hash1, block.hash)
        
        # Test 2: Hash should include previous block's hash
        # Create identical block with different previous hash
        different_previous_hash = "f" * 64 if previous_hash != "f" * 64 else "a" * 64
        block_different_prev = Block(index, timestamp, votes, different_previous_hash)
        
        # Hashes should be different when previous hash is different
        self.assertNotEqual(block.hash, block_different_prev.hash)
        
        # Test 3: Hash should be affected by all block data
        # Change index
        if index > 0:
            block_different_index = Block(index - 1, timestamp, votes, previous_hash)
            self.assertNotEqual(block.hash, block_different_index.hash)
        
        # Change timestamp (if we can create a different valid timestamp)
        different_timestamp = timestamp + 1.0
        block_different_timestamp = Block(index, different_timestamp, votes, previous_hash)
        self.assertNotEqual(block.hash, block_different_timestamp.hash)
    
    @given(
        num_blocks=st.integers(min_value=1, max_value=5),
        votes_per_block=st.lists(
            st.lists(
                st.builds(
                    Vote,
                    voter_id=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                    candidate=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                    timestamp=st.floats(min_value=1.0, max_value=2147483647.0)
                ),
                min_size=0,
                max_size=5
            ),
            min_size=1,
            max_size=5
        )
    )
    def test_blockchain_integrity_validation_property_6(self, num_blocks, votes_per_block):
        """
        Property 6: Blockchain Integrity Validation
        Feature: blockchain-voting, Property 6: Blockchain Integrity Validation
        Validates: Requirements 3.4, 4.2, 4.4
        
        For any blockchain, validation should pass if and only if all hash linkages 
        are correct and each block's hash matches its calculated value.
        """
        # Create a fresh blockchain
        blockchain = Blockchain()
        
        # Add blocks with the generated votes
        for i in range(min(num_blocks, len(votes_per_block))):
            votes = votes_per_block[i]
            success = blockchain.add_block(votes)
            self.assertTrue(success, f"Failed to add block {i}")
        
        # Test 1: Valid blockchain should pass validation
        self.assertTrue(blockchain.validate_chain(), "Valid blockchain should pass validation")
        
        # Test 2: Corrupting a block's hash should fail validation
        if len(blockchain.chain) > 1:  # Only test if we have more than genesis block
            original_blockchain = Blockchain.from_dict(blockchain.to_dict())  # Make a copy
            
            # Corrupt the hash of a non-genesis block
            block_to_corrupt = blockchain.chain[1]
            original_hash = block_to_corrupt.hash
            block_to_corrupt.hash = "corrupted_hash_" + original_hash[:50]
            
            self.assertFalse(blockchain.validate_chain(), "Blockchain with corrupted hash should fail validation")
            
            # Restore the blockchain for next test
            blockchain = original_blockchain
        
        # Test 3: Breaking hash linkage should fail validation
        if len(blockchain.chain) > 1:  # Only test if we have more than genesis block
            original_blockchain = Blockchain.from_dict(blockchain.to_dict())  # Make a copy
            
            # Break the linkage by changing previous_hash
            block_to_break = blockchain.chain[1]
            original_prev_hash = block_to_break.previous_hash
            block_to_break.previous_hash = "broken_linkage_" + original_prev_hash[:50]
            # Recalculate hash to make block internally consistent but break chain linkage
            block_to_break.hash = block_to_break.calculate_hash()
            
            self.assertFalse(blockchain.validate_chain(), "Blockchain with broken linkage should fail validation")
            
            # Restore the blockchain for next test
            blockchain = original_blockchain
        
        # Test 4: Changing block index should fail validation
        if len(blockchain.chain) > 1:  # Only test if we have more than genesis block
            original_blockchain = Blockchain.from_dict(blockchain.to_dict())  # Make a copy
            
            # Change the index of a block
            block_to_change = blockchain.chain[1]
            original_index = block_to_change.index
            block_to_change.index = original_index + 10  # Invalid index sequence
            # Recalculate hash to make block internally consistent
            block_to_change.hash = block_to_change.calculate_hash()
            
            self.assertFalse(blockchain.validate_chain(), "Blockchain with invalid index sequence should fail validation")
            
            # Restore the blockchain
            blockchain = original_blockchain
        
        # Test 5: Final validation - restored blockchain should be valid
        self.assertTrue(blockchain.validate_chain(), "Restored blockchain should be valid")
    
    @given(
        votes_to_add=st.lists(
            st.builds(
                Vote,
                voter_id=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                candidate=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                timestamp=st.floats(min_value=1.0, max_value=2147483647.0)
            ),
            min_size=0,
            max_size=10
        )
    )
    def test_block_creation_linkage_property_7(self, votes_to_add):
        """
        Property 7: Block Creation Linkage
        Feature: blockchain-voting, Property 7: Block Creation Linkage
        Validates: Requirements 3.2, 3.3
        
        For any blockchain with votes to add, creating a new block should properly 
        link it to the previous block and include all provided votes.
        """
        # Create a fresh blockchain
        blockchain = Blockchain()
        
        # Get the initial state
        initial_block_count = blockchain.get_block_count()
        latest_block_before = blockchain.get_latest_block()
        
        # Add a block with the generated votes
        success = blockchain.add_block(votes_to_add)
        
        # Test 1: Block addition should succeed for valid votes
        self.assertTrue(success, "Adding valid votes should succeed")
        
        # Test 2: Block count should increase by 1
        new_block_count = blockchain.get_block_count()
        self.assertEqual(new_block_count, initial_block_count + 1, 
                        "Block count should increase by 1 after adding a block")
        
        # Test 3: New block should be properly linked to previous block
        new_latest_block = blockchain.get_latest_block()
        self.assertEqual(new_latest_block.previous_hash, latest_block_before.hash,
                        "New block's previous_hash should match the previous block's hash")
        
        # Test 4: New block should have correct index
        expected_index = latest_block_before.index + 1
        self.assertEqual(new_latest_block.index, expected_index,
                        f"New block should have index {expected_index}")
        
        # Test 5: New block should contain all provided votes
        self.assertEqual(len(new_latest_block.votes), len(votes_to_add),
                        "New block should contain all provided votes")
        
        # Verify each vote is included correctly
        for i, original_vote in enumerate(votes_to_add):
            block_vote = new_latest_block.votes[i]
            self.assertEqual(block_vote.voter_id, original_vote.voter_id,
                           f"Vote {i} voter_id should match")
            self.assertEqual(block_vote.candidate, original_vote.candidate,
                           f"Vote {i} candidate should match")
            self.assertEqual(block_vote.timestamp, original_vote.timestamp,
                           f"Vote {i} timestamp should match")
        
        # Test 6: Blockchain should remain valid after adding the block
        self.assertTrue(blockchain.validate_chain(),
                       "Blockchain should remain valid after adding a properly linked block")
        
        # Test 7: Hash linkage should be maintained
        if blockchain.get_block_count() > 1:
            for i in range(1, blockchain.get_block_count()):
                current_block = blockchain.get_block_by_index(i)
                previous_block = blockchain.get_block_by_index(i - 1)
                self.assertEqual(current_block.previous_hash, previous_block.hash,
                               f"Block {i} should be properly linked to block {i-1}")
        
        # Test 8: Adding multiple blocks should maintain proper linkage
        if len(votes_to_add) > 0:  # Only test if we have votes to work with
            # Create a subset of votes for second block
            second_block_votes = votes_to_add[:max(1, len(votes_to_add)//2)]
            
            # Get state before adding second block
            before_second_count = blockchain.get_block_count()
            before_second_latest = blockchain.get_latest_block()
            
            # Add second block
            success_second = blockchain.add_block(second_block_votes)
            self.assertTrue(success_second, "Adding second block should succeed")
            
            # Verify second block linkage
            after_second_latest = blockchain.get_latest_block()
            self.assertEqual(after_second_latest.previous_hash, before_second_latest.hash,
                           "Second block should be properly linked to first added block")
            self.assertEqual(blockchain.get_block_count(), before_second_count + 1,
                           "Block count should increase by 1 after adding second block")
            
            # Final validation
            self.assertTrue(blockchain.validate_chain(),
                           "Blockchain should remain valid after adding multiple blocks")
    
    @given(
        voter_id=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
        candidate=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
    )
    def test_vote_authorization_property_3(self, voter_id, candidate):
        """
        Property 3: Vote Authorization
        Feature: blockchain-voting, Property 3: Vote Authorization
        Validates: Requirements 2.1, 2.2, 2.3
        
        For any voter ID and vote, the vote should be accepted if and only if 
        the voter is registered and has not voted before.
        """
        # Create a fresh voting system
        voting_system = VotingSystem()
        
        # Test 1: Unregistered voter should not be able to vote
        unregistered_result = voting_system.cast_vote(voter_id, candidate)
        self.assertFalse(unregistered_result["success"], 
                        "Unregistered voter should not be able to vote")
        self.assertEqual(unregistered_result["error"], "UNREGISTERED_VOTER",
                        "Should return UNREGISTERED_VOTER error")
        self.assertEqual(len(voting_system.get_pending_votes()), 0,
                        "No votes should be pending after failed vote attempt")
        
        # Test 2: Registered voter should be able to vote
        register_result = voting_system.register_voter(voter_id)
        self.assertTrue(register_result["success"], 
                       "Voter registration should succeed")
        
        first_vote_result = voting_system.cast_vote(voter_id, candidate)
        self.assertTrue(first_vote_result["success"], 
                       "Registered voter should be able to vote")
        self.assertEqual(first_vote_result["voter_id"], voter_id,
                        "Vote result should contain correct voter ID")
        self.assertEqual(first_vote_result["candidate"], candidate,
                        "Vote result should contain correct candidate")
        self.assertEqual(len(voting_system.get_pending_votes()), 1,
                        "One vote should be pending after successful vote")
        
        # Verify voter is marked as having voted
        self.assertTrue(voting_system.voter_manager.has_voted(voter_id),
                       "Voter should be marked as having voted")
        self.assertIn(voter_id, voting_system.get_voted_voters(),
                     "Voter should appear in voted voters list")
        
        # Test 3: Voter who has already voted should not be able to vote again
        # Try to vote for the same candidate
        second_vote_same_result = voting_system.cast_vote(voter_id, candidate)
        self.assertFalse(second_vote_same_result["success"], 
                        "Voter who has already voted should not be able to vote again")
        self.assertEqual(second_vote_same_result["error"], "ALREADY_VOTED",
                        "Should return ALREADY_VOTED error")
        self.assertEqual(len(voting_system.get_pending_votes()), 1,
                        "Pending votes count should remain unchanged after failed second vote")
        
        # Try to vote for a different candidate (should also fail)
        different_candidate = candidate + "_different" if candidate != candidate + "_different" else "other_candidate"
        second_vote_different_result = voting_system.cast_vote(voter_id, different_candidate)
        self.assertFalse(second_vote_different_result["success"], 
                        "Voter who has already voted should not be able to vote for different candidate")
        self.assertEqual(second_vote_different_result["error"], "ALREADY_VOTED",
                        "Should return ALREADY_VOTED error for different candidate too")
        self.assertEqual(len(voting_system.get_pending_votes()), 1,
                        "Pending votes count should remain unchanged after failed vote for different candidate")
        
        # Test 4: Verify the original vote is still intact
        pending_votes = voting_system.get_pending_votes()
        self.assertEqual(len(pending_votes), 1, "Should still have exactly one pending vote")
        original_vote = pending_votes[0]
        self.assertEqual(original_vote.voter_id, voter_id, "Original vote voter_id should be preserved")
        self.assertEqual(original_vote.candidate, candidate, "Original vote candidate should be preserved")
        
        # Test 5: Test with multiple different voters to ensure independence
        # Create a second voter with a different ID
        second_voter_id = voter_id + "_second" if voter_id != voter_id + "_second" else "second_voter"
        second_candidate = candidate + "_second" if candidate != candidate + "_second" else "second_candidate"
        
        # Second voter should be able to register and vote independently
        second_register_result = voting_system.register_voter(second_voter_id)
        self.assertTrue(second_register_result["success"], 
                       "Second voter registration should succeed")
        
        second_voter_vote_result = voting_system.cast_vote(second_voter_id, second_candidate)
        self.assertTrue(second_voter_vote_result["success"], 
                       "Second registered voter should be able to vote")
        self.assertEqual(len(voting_system.get_pending_votes()), 2,
                        "Should have two pending votes after second voter votes")
        
        # First voter still should not be able to vote again
        first_voter_retry_result = voting_system.cast_vote(voter_id, second_candidate)
        self.assertFalse(first_voter_retry_result["success"], 
                        "First voter should still not be able to vote again")
        self.assertEqual(first_voter_retry_result["error"], "ALREADY_VOTED",
                        "Should still return ALREADY_VOTED error")
        
        # Test 6: Verify system state consistency
        registered_voters = voting_system.get_registered_voters()
        voted_voters = voting_system.get_voted_voters()
        
        self.assertEqual(len(registered_voters), 2, "Should have two registered voters")
        self.assertEqual(len(voted_voters), 2, "Should have two voted voters")
        self.assertIn(voter_id, registered_voters, "First voter should be in registered list")
        self.assertIn(second_voter_id, registered_voters, "Second voter should be in registered list")
        self.assertIn(voter_id, voted_voters, "First voter should be in voted list")
        self.assertIn(second_voter_id, voted_voters, "Second voter should be in voted list")
        
        # Test 7: Test authorization after block creation
        # Create a block from pending votes
        block_result = voting_system.create_block_from_pending_votes()
        self.assertTrue(block_result["success"], "Block creation should succeed")
        self.assertEqual(len(voting_system.get_pending_votes()), 0, "Pending votes should be cleared")
        
        # Voters should still not be able to vote again even after block creation
        post_block_vote_result = voting_system.cast_vote(voter_id, candidate)
        self.assertFalse(post_block_vote_result["success"], 
                        "Voter should still not be able to vote after block creation")
        self.assertEqual(post_block_vote_result["error"], "ALREADY_VOTED",
                        "Should still return ALREADY_VOTED error after block creation")
        
        # But a new voter should still be able to register and vote
        third_voter_id = voter_id + "_third" if voter_id != voter_id + "_third" else "third_voter"
        third_candidate = candidate + "_third" if candidate != candidate + "_third" else "third_candidate"
        
        third_register_result = voting_system.register_voter(third_voter_id)
        self.assertTrue(third_register_result["success"], 
                       "Third voter registration should succeed after block creation")
        
        third_vote_result = voting_system.cast_vote(third_voter_id, third_candidate)
        self.assertTrue(third_vote_result["success"], 
                       "Third voter should be able to vote after block creation")
        self.assertEqual(len(voting_system.get_pending_votes()), 1,
                        "Should have one pending vote from third voter")
    
    @given(
        votes_to_cast=st.lists(
            st.tuples(
                st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
            ),
            min_size=1,
            max_size=10,
            unique_by=lambda x: x[0]  # Ensure unique voter IDs
        )
    )
    def test_vote_persistence_property_4(self, votes_to_cast):
        """
        Property 4: Vote Persistence
        Feature: blockchain-voting, Property 4: Vote Persistence
        Validates: Requirements 2.4
        
        For any accepted vote, it should remain in pending votes until a block is created, 
        and then appear in the blockchain.
        """
        # Create a fresh voting system
        voting_system = VotingSystem()
        
        # Register all voters and cast their votes
        cast_votes = []
        for voter_id, candidate in votes_to_cast:
            # Register voter
            register_result = voting_system.register_voter(voter_id)
            self.assertTrue(register_result["success"], 
                           f"Registration should succeed for voter {voter_id}")
            
            # Cast vote
            vote_result = voting_system.cast_vote(voter_id, candidate)
            self.assertTrue(vote_result["success"], 
                           f"Vote casting should succeed for voter {voter_id}")
            
            cast_votes.append((voter_id, candidate, vote_result["timestamp"]))
        
        # Test 1: All votes should be in pending votes before block creation
        pending_votes = voting_system.get_pending_votes()
        self.assertEqual(len(pending_votes), len(votes_to_cast),
                        "All cast votes should be in pending votes")
        
        # Verify each vote is in pending votes with correct data
        pending_vote_data = [(v.voter_id, v.candidate) for v in pending_votes]
        expected_vote_data = [(voter_id, candidate) for voter_id, candidate in votes_to_cast]
        
        for expected_voter_id, expected_candidate in expected_vote_data:
            self.assertIn((expected_voter_id, expected_candidate), pending_vote_data,
                         f"Vote from {expected_voter_id} for {expected_candidate} should be in pending votes")
        
        # Test 2: Votes should NOT be in blockchain before block creation
        blockchain_votes_before = voting_system.blockchain.get_all_votes()
        blockchain_voter_ids_before = set(vote.voter_id for vote in blockchain_votes_before)
        
        for voter_id, candidate in votes_to_cast:
            self.assertNotIn(voter_id, blockchain_voter_ids_before,
                           f"Vote from {voter_id} should NOT be in blockchain before block creation")
        
        # Test 3: Create block from pending votes
        initial_block_count = voting_system.blockchain.get_block_count()
        block_result = voting_system.create_block_from_pending_votes()
        self.assertTrue(block_result["success"], "Block creation should succeed")
        self.assertEqual(block_result["votes_count"], len(votes_to_cast),
                        "Block should contain all pending votes")
        
        # Test 4: Pending votes should be cleared after block creation
        pending_votes_after = voting_system.get_pending_votes()
        self.assertEqual(len(pending_votes_after), 0,
                        "Pending votes should be cleared after block creation")
        
        # Test 5: All votes should now appear in the blockchain
        blockchain_votes_after = voting_system.blockchain.get_all_votes()
        self.assertEqual(len(blockchain_votes_after), len(votes_to_cast),
                        "All votes should now be in blockchain")
        
        # Verify each vote appears in blockchain with correct data
        blockchain_vote_data = [(v.voter_id, v.candidate) for v in blockchain_votes_after]
        
        for expected_voter_id, expected_candidate in expected_vote_data:
            self.assertIn((expected_voter_id, expected_candidate), blockchain_vote_data,
                         f"Vote from {expected_voter_id} for {expected_candidate} should be in blockchain")
        
        # Test 6: Block count should have increased by 1
        final_block_count = voting_system.blockchain.get_block_count()
        self.assertEqual(final_block_count, initial_block_count + 1,
                        "Block count should increase by 1 after creating block")
        
        # Test 7: The new block should contain exactly the votes that were pending
        latest_block = voting_system.blockchain.get_latest_block()
        block_votes = latest_block.votes
        self.assertEqual(len(block_votes), len(votes_to_cast),
                        "Latest block should contain all the votes that were pending")
        
        block_vote_data = [(v.voter_id, v.candidate) for v in block_votes]
        for expected_voter_id, expected_candidate in expected_vote_data:
            self.assertIn((expected_voter_id, expected_candidate), block_vote_data,
                         f"Latest block should contain vote from {expected_voter_id} for {expected_candidate}")
        
        # Test 8: Test persistence across multiple block creations
        # Cast additional votes to test the pattern continues to work
        if len(votes_to_cast) > 1:  # Only test if we have multiple votes to work with
            # Take the first voter and create a new voter ID for second round
            first_voter_base = votes_to_cast[0][0]
            first_candidate_base = votes_to_cast[0][1]
            
            second_round_voter = first_voter_base + "_round2"
            second_round_candidate = first_candidate_base + "_round2"
            
            # Register and vote for second round
            register_result_2 = voting_system.register_voter(second_round_voter)
            self.assertTrue(register_result_2["success"], 
                           "Second round voter registration should succeed")
            
            vote_result_2 = voting_system.cast_vote(second_round_voter, second_round_candidate)
            self.assertTrue(vote_result_2["success"], 
                           "Second round vote casting should succeed")
            
            # Verify vote is in pending votes
            pending_votes_round2 = voting_system.get_pending_votes()
            self.assertEqual(len(pending_votes_round2), 1,
                           "Should have one pending vote in second round")
            self.assertEqual(pending_votes_round2[0].voter_id, second_round_voter,
                           "Pending vote should be from second round voter")
            
            # Create second block
            block_result_2 = voting_system.create_block_from_pending_votes()
            self.assertTrue(block_result_2["success"], "Second block creation should succeed")
            
            # Verify persistence pattern continues
            pending_votes_after_2 = voting_system.get_pending_votes()
            self.assertEqual(len(pending_votes_after_2), 0,
                           "Pending votes should be cleared after second block creation")
            
            all_blockchain_votes = voting_system.blockchain.get_all_votes()
            self.assertEqual(len(all_blockchain_votes), len(votes_to_cast) + 1,
                           "Blockchain should contain all votes from both rounds")
            
            # Verify the second round vote is in blockchain
            second_round_votes = [v for v in all_blockchain_votes if v.voter_id == second_round_voter]
            self.assertEqual(len(second_round_votes), 1,
                           "Second round vote should be in blockchain")
            self.assertEqual(second_round_votes[0].candidate, second_round_candidate,
                           "Second round vote should have correct candidate")
        
        # Test 9: Verify blockchain integrity is maintained
        integrity_result = voting_system.validate_system_integrity()
        self.assertTrue(integrity_result["success"], "System integrity validation should succeed")
        self.assertTrue(integrity_result["blockchain_valid"], "Blockchain should be valid")
        self.assertTrue(integrity_result["integrity_valid"], "System integrity should be valid")
        
        # Test 10: Verify vote counting works correctly after persistence
        results = voting_system.get_results()
        self.assertTrue(results["success"], "Getting results should succeed")
        
        # Count expected votes by candidate (including second round if it happened)
        expected_counts = {}
        for voter_id, candidate in votes_to_cast:
            expected_counts[candidate] = expected_counts.get(candidate, 0) + 1
        
        # Add second round vote to expected counts if it was created
        if len(votes_to_cast) > 1:
            first_voter_base = votes_to_cast[0][0]
            first_candidate_base = votes_to_cast[0][1]
            second_round_candidate = first_candidate_base + "_round2"
            expected_counts[second_round_candidate] = expected_counts.get(second_round_candidate, 0) + 1
        
        # Verify vote counts match expectations
        actual_counts = results["vote_counts"]
        for candidate, expected_count in expected_counts.items():
            self.assertEqual(actual_counts.get(candidate, 0), expected_count,
                           f"Vote count for {candidate} should be {expected_count}")
        
        total_expected = sum(expected_counts.values())
        self.assertEqual(results["total_votes"], total_expected,
                        f"Total vote count should be {total_expected}")
    
    @given(
        votes_to_cast=st.lists(
            st.tuples(
                st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
            ),
            min_size=1,
            max_size=15,
            unique_by=lambda x: x[0]  # Ensure unique voter IDs
        ),
        num_blocks=st.integers(min_value=1, max_value=3)
    )
    def test_vote_counting_accuracy_property_8(self, votes_to_cast, num_blocks):
        """
        Property 8: Vote Counting Accuracy
        Feature: blockchain-voting, Property 8: Vote Counting Accuracy
        Validates: Requirements 5.1, 5.2, 5.3
        
        For any blockchain, the vote counts for each candidate should equal the number 
        of votes cast for that candidate across all blocks, and the total should equal 
        the sum of all individual counts.
        """
        # Create a fresh voting system
        voting_system = VotingSystem()
        
        # Track expected vote counts manually
        expected_candidate_counts = {}
        all_cast_votes = []
        
        # Split votes across multiple blocks
        votes_per_block = len(votes_to_cast) // num_blocks
        remaining_votes = len(votes_to_cast) % num_blocks
        
        vote_index = 0
        for block_num in range(num_blocks):
            # Determine how many votes for this block
            votes_for_this_block = votes_per_block
            if block_num < remaining_votes:
                votes_for_this_block += 1
            
            # Skip if no votes for this block
            if votes_for_this_block == 0:
                continue
                
            # Get votes for this block
            block_votes = votes_to_cast[vote_index:vote_index + votes_for_this_block]
            vote_index += votes_for_this_block
            
            # Register voters and cast votes for this block
            for voter_id, candidate in block_votes:
                # Register voter
                register_result = voting_system.register_voter(voter_id)
                self.assertTrue(register_result["success"], 
                               f"Registration should succeed for voter {voter_id}")
                
                # Cast vote
                vote_result = voting_system.cast_vote(voter_id, candidate)
                self.assertTrue(vote_result["success"], 
                               f"Vote casting should succeed for voter {voter_id}")
                
                # Track expected counts
                expected_candidate_counts[candidate] = expected_candidate_counts.get(candidate, 0) + 1
                all_cast_votes.append((voter_id, candidate))
            
            # Create block from pending votes (if any votes were cast)
            if len(block_votes) > 0:
                block_result = voting_system.create_block_from_pending_votes()
                self.assertTrue(block_result["success"], 
                               f"Block creation should succeed for block {block_num}")
                self.assertEqual(block_result["votes_count"], len(block_votes),
                               f"Block {block_num} should contain {len(block_votes)} votes")
        
        # Test 1: Get results and verify vote counting accuracy
        results = voting_system.get_results()
        self.assertTrue(results["success"], "Getting results should succeed")
        
        actual_vote_counts = results["vote_counts"]
        
        # Test 2: Each candidate's count should match expected count
        for candidate, expected_count in expected_candidate_counts.items():
            actual_count = actual_vote_counts.get(candidate, 0)
            self.assertEqual(actual_count, expected_count,
                           f"Vote count for candidate '{candidate}' should be {expected_count}, got {actual_count}")
        
        # Test 3: No extra candidates should appear in results
        for candidate in actual_vote_counts:
            self.assertIn(candidate, expected_candidate_counts,
                         f"Candidate '{candidate}' appears in results but was not voted for")
        
        # Test 4: Total votes should equal sum of individual candidate counts
        expected_total = sum(expected_candidate_counts.values())
        actual_total_from_sum = sum(actual_vote_counts.values())
        actual_total_reported = results["total_votes"]
        
        self.assertEqual(actual_total_reported, expected_total,
                        f"Reported total votes should be {expected_total}, got {actual_total_reported}")
        self.assertEqual(actual_total_from_sum, expected_total,
                        f"Sum of individual counts should be {expected_total}, got {actual_total_from_sum}")
        self.assertEqual(actual_total_reported, actual_total_from_sum,
                        "Reported total should equal sum of individual counts")
        
        # Test 5: Verify counts by manually traversing blockchain
        all_blockchain_votes = voting_system.blockchain.get_all_votes()
        manual_candidate_counts = {}
        
        for vote in all_blockchain_votes:
            candidate = vote.candidate
            manual_candidate_counts[candidate] = manual_candidate_counts.get(candidate, 0) + 1
        
        # Manual counts should match both expected and reported counts
        self.assertEqual(len(all_blockchain_votes), expected_total,
                        f"Blockchain should contain {expected_total} votes, found {len(all_blockchain_votes)}")
        
        for candidate, expected_count in expected_candidate_counts.items():
            manual_count = manual_candidate_counts.get(candidate, 0)
            self.assertEqual(manual_count, expected_count,
                           f"Manual count for candidate '{candidate}' should be {expected_count}, got {manual_count}")
        
        # Test 6: Verify individual candidate vote retrieval
        for candidate in expected_candidate_counts:
            candidate_result = voting_system.get_candidate_votes(candidate)
            self.assertTrue(candidate_result["success"], 
                           f"Getting votes for candidate '{candidate}' should succeed")
            self.assertEqual(candidate_result["vote_count"], expected_candidate_counts[candidate],
                           f"Individual candidate query should return correct count for '{candidate}'")
            self.assertEqual(len(candidate_result["votes"]), expected_candidate_counts[candidate],
                           f"Individual candidate query should return correct number of vote details for '{candidate}'")
        
        # Test 7: Verify vote counts remain accurate after additional operations
        # Add one more voter and vote to test incremental accuracy
        if len(votes_to_cast) > 0:
            # Create a new voter ID that doesn't conflict
            base_voter = votes_to_cast[0][0]
            base_candidate = votes_to_cast[0][1]
            new_voter_id = base_voter + "_extra"
            new_candidate = base_candidate + "_extra"
            
            # Register and vote
            register_result = voting_system.register_voter(new_voter_id)
            self.assertTrue(register_result["success"], "Extra voter registration should succeed")
            
            vote_result = voting_system.cast_vote(new_voter_id, new_candidate)
            self.assertTrue(vote_result["success"], "Extra vote casting should succeed")
            
            # Create block for the extra vote
            block_result = voting_system.create_block_from_pending_votes()
            self.assertTrue(block_result["success"], "Extra block creation should succeed")
            
            # Update expected counts
            expected_candidate_counts[new_candidate] = expected_candidate_counts.get(new_candidate, 0) + 1
            expected_total += 1
            
            # Verify updated counts
            updated_results = voting_system.get_results()
            self.assertTrue(updated_results["success"], "Getting updated results should succeed")
            
            updated_vote_counts = updated_results["vote_counts"]
            updated_total = updated_results["total_votes"]
            
            self.assertEqual(updated_total, expected_total,
                           f"Updated total should be {expected_total}")
            self.assertEqual(updated_vote_counts.get(new_candidate, 0), 1,
                           f"New candidate should have 1 vote")
            
            # Verify all original counts are still correct
            for candidate, expected_count in expected_candidate_counts.items():
                if candidate != new_candidate:  # Skip the new candidate we just added
                    actual_count = updated_vote_counts.get(candidate, 0)
                    self.assertEqual(actual_count, expected_count,
                                   f"Original candidate '{candidate}' count should remain {expected_count}")
        
        # Test 8: Verify system integrity is maintained throughout
        integrity_result = voting_system.validate_system_integrity()
        self.assertTrue(integrity_result["success"], "System integrity validation should succeed")
        self.assertTrue(integrity_result["blockchain_valid"], "Blockchain should remain valid")
        self.assertTrue(integrity_result["integrity_valid"], "System integrity should remain valid")
        
        # Test 9: Verify consistency across different query methods
        all_candidates = voting_system.get_all_candidates()
        expected_candidates = set(expected_candidate_counts.keys())
        actual_candidates = set(all_candidates)
        
        self.assertEqual(actual_candidates, expected_candidates,
                        f"get_all_candidates() should return {expected_candidates}, got {actual_candidates}")
        
        # Test 10: Edge case - verify empty candidate handling
        # Try to get votes for a candidate that doesn't exist
        nonexistent_candidate = "nonexistent_candidate_12345"
        nonexistent_result = voting_system.get_candidate_votes(nonexistent_candidate)
        self.assertTrue(nonexistent_result["success"], 
                       "Getting votes for nonexistent candidate should succeed")
        self.assertEqual(nonexistent_result["vote_count"], 0,
                       "Nonexistent candidate should have 0 votes")
        self.assertEqual(len(nonexistent_result["votes"]), 0,
                       "Nonexistent candidate should have empty votes list")
    
    @given(
        votes_to_cast=st.lists(
            st.tuples(
                st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
            ),
            min_size=0,
            max_size=10,
            unique_by=lambda x: x[0]  # Ensure unique voter IDs
        )
    )
    def test_results_include_validation_status_property_9(self, votes_to_cast):
        """
        Property 9: Results Include Validation Status
        Feature: blockchain-voting, Property 9: Results Include Validation Status
        Validates: Requirements 5.4
        
        For any results query, the response should include both vote counts and 
        the current blockchain validation status.
        """
        # Create a fresh voting system
        voting_system = VotingSystem()
        
        # Register voters and cast votes (if any)
        for voter_id, candidate in votes_to_cast:
            # Register voter
            register_result = voting_system.register_voter(voter_id)
            self.assertTrue(register_result["success"], 
                           f"Registration should succeed for voter {voter_id}")
            
            # Cast vote
            vote_result = voting_system.cast_vote(voter_id, candidate)
            self.assertTrue(vote_result["success"], 
                           f"Vote casting should succeed for voter {voter_id}")
        
        # Create blocks from pending votes if any votes were cast
        if len(votes_to_cast) > 0:
            block_result = voting_system.create_block_from_pending_votes()
            self.assertTrue(block_result["success"], "Block creation should succeed")
        
        # Test 1: Get results and verify required validation status fields are present
        results = voting_system.get_results()
        self.assertTrue(results["success"], "Getting results should succeed")
        
        # Test 2: Results should include blockchain validation status
        self.assertIn("blockchain_valid", results,
                     "Results should include blockchain_valid field")
        self.assertIsInstance(results["blockchain_valid"], bool,
                             "blockchain_valid should be a boolean value")
        
        # Test 3: Results should include system integrity validation status
        self.assertIn("integrity_valid", results,
                     "Results should include integrity_valid field")
        self.assertIsInstance(results["integrity_valid"], bool,
                             "integrity_valid should be a boolean value")
        
        # Test 4: Results should include validation issues (if any)
        self.assertIn("validation_issues", results,
                     "Results should include validation_issues field")
        self.assertIsInstance(results["validation_issues"], list,
                             "validation_issues should be a list")
        
        # Test 5: For a valid system, validation status should be True
        # (assuming no corruption has occurred)
        self.assertTrue(results["blockchain_valid"],
                       "Blockchain should be valid for uncorrupted system")
        self.assertTrue(results["integrity_valid"],
                       "System integrity should be valid for uncorrupted system")
        self.assertEqual(len(results["validation_issues"]), 0,
                        "Valid system should have no validation issues")
        
        # Test 6: Results should also include vote counting information
        self.assertIn("vote_counts", results,
                     "Results should include vote_counts field")
        self.assertIn("total_votes", results,
                     "Results should include total_votes field")
        self.assertIsInstance(results["vote_counts"], dict,
                             "vote_counts should be a dictionary")
        self.assertIsInstance(results["total_votes"], int,
                             "total_votes should be an integer")
        
        # Test 7: Verify vote counts match expected values
        expected_counts = {}
        for voter_id, candidate in votes_to_cast:
            expected_counts[candidate] = expected_counts.get(candidate, 0) + 1
        
        actual_counts = results["vote_counts"]
        expected_total = sum(expected_counts.values())
        
        self.assertEqual(results["total_votes"], expected_total,
                        f"Total votes should be {expected_total}")
        
        for candidate, expected_count in expected_counts.items():
            self.assertEqual(actual_counts.get(candidate, 0), expected_count,
                           f"Vote count for {candidate} should be {expected_count}")
        
        # Test 8: Additional status fields should be present
        self.assertIn("registered_voters", results,
                     "Results should include registered_voters count")
        self.assertIn("voted_voters", results,
                     "Results should include voted_voters count")
        self.assertIn("pending_votes", results,
                     "Results should include pending_votes count")
        self.assertIn("total_blocks", results,
                     "Results should include total_blocks count")
        
        # Verify these are correct types and values
        self.assertIsInstance(results["registered_voters"], int,
                             "registered_voters should be an integer")
        self.assertIsInstance(results["voted_voters"], int,
                             "voted_voters should be an integer")
        self.assertIsInstance(results["pending_votes"], int,
                             "pending_votes should be an integer")
        self.assertIsInstance(results["total_blocks"], int,
                             "total_blocks should be an integer")
        
        self.assertEqual(results["registered_voters"], len(votes_to_cast),
                        "registered_voters count should match number of registered voters")
        self.assertEqual(results["voted_voters"], len(votes_to_cast),
                        "voted_voters count should match number of voters who voted")
        self.assertEqual(results["pending_votes"], 0,
                        "pending_votes should be 0 after block creation")
        
        # Test 9: Test validation status consistency with direct validation call
        direct_validation = voting_system.validate_system_integrity()
        self.assertTrue(direct_validation["success"], "Direct validation should succeed")
        
        self.assertEqual(results["blockchain_valid"], direct_validation["blockchain_valid"],
                        "blockchain_valid should match direct validation result")
        self.assertEqual(results["integrity_valid"], direct_validation["integrity_valid"],
                        "integrity_valid should match direct validation result")
        self.assertEqual(results["validation_issues"], direct_validation["issues"],
                        "validation_issues should match direct validation issues")
        
        # Test 10: Test with corrupted blockchain to verify validation status changes
        if len(votes_to_cast) > 0:  # Only test corruption if we have blocks to corrupt
            # Make a backup of the original system
            original_system_dict = voting_system.to_dict()
            
            # Corrupt the blockchain by modifying a block hash
            if voting_system.blockchain.get_block_count() > 1:  # Don't corrupt genesis block
                corrupted_block = voting_system.blockchain.chain[1]
                original_hash = corrupted_block.hash
                corrupted_block.hash = "corrupted_" + original_hash[:50]
                
                # Get results from corrupted system
                corrupted_results = voting_system.get_results()
                self.assertTrue(corrupted_results["success"], 
                               "Getting results should succeed even with corrupted blockchain")
                
                # Validation status should reflect corruption
                self.assertFalse(corrupted_results["blockchain_valid"],
                                "blockchain_valid should be False for corrupted blockchain")
                
                # Vote counts should still be present (even if blockchain is corrupted)
                self.assertIn("vote_counts", corrupted_results,
                             "vote_counts should still be present in corrupted results")
                self.assertIn("total_votes", corrupted_results,
                             "total_votes should still be present in corrupted results")
                
                # Restore the original system
                voting_system = VotingSystem.from_dict(original_system_dict)
                
                # Verify restoration worked
                restored_results = voting_system.get_results()
                self.assertTrue(restored_results["blockchain_valid"],
                               "blockchain_valid should be True after restoration")
                self.assertTrue(restored_results["integrity_valid"],
                               "integrity_valid should be True after restoration")
        
        # Test 11: Test empty system validation status
        empty_system = VotingSystem()
        empty_results = empty_system.get_results()
        
        self.assertTrue(empty_results["success"], "Getting results from empty system should succeed")
        self.assertTrue(empty_results["blockchain_valid"], "Empty system blockchain should be valid")
        self.assertTrue(empty_results["integrity_valid"], "Empty system integrity should be valid")
        self.assertEqual(empty_results["total_votes"], 0, "Empty system should have 0 votes")
        self.assertEqual(empty_results["vote_counts"], {}, "Empty system should have empty vote counts")
        self.assertEqual(len(empty_results["validation_issues"]), 0,
                        "Empty system should have no validation issues")
    
    @given(
        votes_to_cast=st.lists(
            st.tuples(
                st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
                st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
            ),
            min_size=0,
            max_size=10,
            unique_by=lambda x: x[0]  # Ensure unique voter IDs
        ),
        num_blocks=st.integers(min_value=0, max_value=3),
        filename=st.text(min_size=5, max_size=30, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_').map(lambda x: f"test_{x}.json")
    )
    def test_data_persistence_round_trip_property_10(self, votes_to_cast, num_blocks, filename):
        """
        Property 10: Data Persistence Round Trip
        Feature: blockchain-voting, Property 10: Data Persistence Round Trip
        Validates: Requirements 7.1, 7.2, 7.3, 7.4
        
        For any system state, saving then loading should restore the exact same voter 
        registrations, blockchain data, and validation status.
        """
        import tempfile
        import os
        
        # Create a fresh voting system
        original_system = VotingSystem()
        
        # Build up system state with voters and votes
        all_voters = []
        expected_vote_counts = {}
        
        # Register voters and cast votes
        for voter_id, candidate in votes_to_cast:
            # Register voter
            register_result = original_system.register_voter(voter_id)
            self.assertTrue(register_result["success"], 
                           f"Registration should succeed for voter {voter_id}")
            all_voters.append(voter_id)
            
            # Cast vote
            vote_result = original_system.cast_vote(voter_id, candidate)
            self.assertTrue(vote_result["success"], 
                           f"Vote casting should succeed for voter {voter_id}")
            
            # Track expected vote counts
            expected_vote_counts[candidate] = expected_vote_counts.get(candidate, 0) + 1
        
        # Create blocks from votes (split across multiple blocks if specified)
        if len(votes_to_cast) > 0 and num_blocks > 0:
            # Split votes across blocks by creating blocks at intervals
            votes_per_block = max(1, len(votes_to_cast) // num_blocks)
            blocks_created = 0
            
            while original_system.get_pending_votes_count() > 0 and blocks_created < num_blocks:
                # Create block from current pending votes
                block_result = original_system.create_block_from_pending_votes()
                self.assertTrue(block_result["success"], 
                               f"Block creation {blocks_created + 1} should succeed")
                blocks_created += 1
                
                # If we want multiple blocks but have more votes, add some more votes
                if blocks_created < num_blocks and len(votes_to_cast) > blocks_created:
                    # We already cast all votes, so just create blocks from pending votes
                    pass
        
        # Capture original system state for comparison
        original_registered_voters = set(original_system.get_registered_voters())
        original_voted_voters = set(original_system.get_voted_voters())
        original_pending_votes = original_system.get_pending_votes()
        original_blockchain_votes = original_system.blockchain.get_all_votes()
        original_block_count = original_system.blockchain.get_block_count()
        original_results = original_system.get_results()
        original_validation = original_system.validate_system_integrity()
        
        # Test 1: Save system state to temporary file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_filename = os.path.join(temp_dir, filename)
            
            save_result = original_system.save_state(temp_filename)
            self.assertTrue(save_result["success"], 
                           f"Saving system state should succeed: {save_result.get('message', '')}")
            self.assertEqual(save_result["filename"], temp_filename,
                           "Save result should contain correct filename")
            
            # Test 2: Verify file was created and contains data
            self.assertTrue(os.path.exists(temp_filename),
                           "Save file should exist after saving")
            
            file_size = os.path.getsize(temp_filename)
            self.assertGreater(file_size, 0, "Save file should not be empty")
            
            # Test 3: Create new system and load state
            loaded_system = VotingSystem()
            
            # Verify new system starts empty
            self.assertEqual(len(loaded_system.get_registered_voters()), 0,
                           "New system should start with no registered voters")
            self.assertEqual(loaded_system.blockchain.get_block_count(), 1,
                           "New system should start with only genesis block")
            
            load_result = loaded_system.load_state(temp_filename)
            self.assertTrue(load_result["success"], 
                           f"Loading system state should succeed: {load_result.get('message', '')}")
            self.assertEqual(load_result["filename"], temp_filename,
                           "Load result should contain correct filename")
            
            # Test 4: Verify voter registrations are preserved
            loaded_registered_voters = set(loaded_system.get_registered_voters())
            loaded_voted_voters = set(loaded_system.get_voted_voters())
            
            self.assertEqual(loaded_registered_voters, original_registered_voters,
                           "Loaded system should have same registered voters as original")
            self.assertEqual(loaded_voted_voters, original_voted_voters,
                           "Loaded system should have same voted voters as original")
            self.assertEqual(len(loaded_registered_voters), len(all_voters),
                           f"Should have {len(all_voters)} registered voters after loading")
            
            # Test 5: Verify blockchain data is preserved
            loaded_blockchain_votes = loaded_system.blockchain.get_all_votes()
            loaded_block_count = loaded_system.blockchain.get_block_count()
            
            self.assertEqual(loaded_block_count, original_block_count,
                           "Loaded system should have same number of blocks as original")
            self.assertEqual(len(loaded_blockchain_votes), len(original_blockchain_votes),
                           "Loaded system should have same number of blockchain votes as original")
            
            # Verify individual votes match
            original_vote_data = [(v.voter_id, v.candidate, v.timestamp) for v in original_blockchain_votes]
            loaded_vote_data = [(v.voter_id, v.candidate, v.timestamp) for v in loaded_blockchain_votes]
            
            self.assertEqual(set(loaded_vote_data), set(original_vote_data),
                           "Loaded blockchain votes should match original votes exactly")
            
            # Test 6: Verify pending votes are preserved
            loaded_pending_votes = loaded_system.get_pending_votes()
            self.assertEqual(len(loaded_pending_votes), len(original_pending_votes),
                           "Loaded system should have same number of pending votes as original")
            
            if len(original_pending_votes) > 0:
                original_pending_data = [(v.voter_id, v.candidate, v.timestamp) for v in original_pending_votes]
                loaded_pending_data = [(v.voter_id, v.candidate, v.timestamp) for v in loaded_pending_votes]
                
                self.assertEqual(set(loaded_pending_data), set(original_pending_data),
                               "Loaded pending votes should match original pending votes exactly")
            
            # Test 7: Verify vote counting results are preserved
            loaded_results = loaded_system.get_results()
            self.assertTrue(loaded_results["success"], "Getting results from loaded system should succeed")
            
            self.assertEqual(loaded_results["vote_counts"], original_results["vote_counts"],
                           "Loaded system vote counts should match original")
            self.assertEqual(loaded_results["total_votes"], original_results["total_votes"],
                           "Loaded system total votes should match original")
            self.assertEqual(loaded_results["registered_voters"], original_results["registered_voters"],
                           "Loaded system registered voters count should match original")
            self.assertEqual(loaded_results["voted_voters"], original_results["voted_voters"],
                           "Loaded system voted voters count should match original")
            self.assertEqual(loaded_results["pending_votes"], original_results["pending_votes"],
                           "Loaded system pending votes count should match original")
            self.assertEqual(loaded_results["total_blocks"], original_results["total_blocks"],
                           "Loaded system total blocks should match original")
            
            # Test 8: Verify validation status is preserved
            loaded_validation = loaded_system.validate_system_integrity()
            self.assertTrue(loaded_validation["success"], "Loaded system validation should succeed")
            
            self.assertEqual(loaded_validation["blockchain_valid"], original_validation["blockchain_valid"],
                           "Loaded system blockchain validation should match original")
            self.assertEqual(loaded_validation["integrity_valid"], original_validation["integrity_valid"],
                           "Loaded system integrity validation should match original")
            self.assertEqual(loaded_validation["issues"], original_validation["issues"],
                           "Loaded system validation issues should match original")
            
            # Test 9: Verify loaded system can continue operating normally
            if len(votes_to_cast) > 0:
                # Try to register a new voter in loaded system
                new_voter_id = f"new_voter_{len(all_voters)}"
                new_candidate = f"new_candidate_{len(expected_vote_counts)}"
                
                new_register_result = loaded_system.register_voter(new_voter_id)
                self.assertTrue(new_register_result["success"], 
                               "Should be able to register new voter in loaded system")
                
                new_vote_result = loaded_system.cast_vote(new_voter_id, new_candidate)
                self.assertTrue(new_vote_result["success"], 
                               "Should be able to cast vote in loaded system")
                
                # Verify the new vote is properly handled
                self.assertEqual(loaded_system.get_pending_votes_count(), 
                               len(original_pending_votes) + 1,
                               "Loaded system should handle new votes correctly")
                
                # Create block from new pending votes
                if loaded_system.get_pending_votes_count() > 0:
                    new_block_result = loaded_system.create_block_from_pending_votes()
                    self.assertTrue(new_block_result["success"], 
                                   "Should be able to create blocks in loaded system")
            
            # Test 10: Test round-trip preservation with serialization
            # Save the loaded system and verify it produces identical data
            temp_filename_2 = os.path.join(temp_dir, f"roundtrip_{filename}")
            
            save_result_2 = loaded_system.save_state(temp_filename_2)
            self.assertTrue(save_result_2["success"], "Second save should succeed")
            
            # Load into a third system
            third_system = VotingSystem()
            load_result_2 = third_system.load_state(temp_filename_2)
            self.assertTrue(load_result_2["success"], "Second load should succeed")
            
            # Verify third system matches loaded system (which should match original)
            third_results = third_system.get_results()
            
            # Compare key metrics (allowing for the new vote if it was added)
            if len(votes_to_cast) == 0:
                # If no original votes, systems should be identical
                self.assertEqual(third_results["vote_counts"], loaded_results["vote_counts"],
                               "Third system should match loaded system exactly")
                self.assertEqual(third_results["total_votes"], loaded_results["total_votes"],
                               "Third system total votes should match loaded system")
            else:
                # If we added a new vote, account for it
                expected_total_after_new_vote = original_results["total_votes"]
                if loaded_system.get_pending_votes_count() == 0:  # Block was created
                    expected_total_after_new_vote += 1
                
                # The core original data should still be preserved
                for candidate, count in original_results["vote_counts"].items():
                    self.assertEqual(third_results["vote_counts"].get(candidate, 0), count,
                                   f"Third system should preserve original vote count for {candidate}")
            
            # Test 11: Verify blockchain integrity is maintained through persistence
            third_validation = third_system.validate_system_integrity()
            self.assertTrue(third_validation["success"], "Third system validation should succeed")
            self.assertTrue(third_validation["blockchain_valid"], "Third system blockchain should be valid")
            self.assertTrue(third_validation["integrity_valid"], "Third system integrity should be valid")
            
            # Test 12: Test error handling for invalid files
            invalid_filename = os.path.join(temp_dir, "nonexistent.json")
            error_system = VotingSystem()
            
            load_error_result = error_system.load_state(invalid_filename)
            self.assertFalse(load_error_result["success"], "Loading nonexistent file should fail")
            self.assertEqual(load_error_result["error"], "FILE_NOT_FOUND",
                           "Should return FILE_NOT_FOUND error for nonexistent file")
            
            # Test 13: Test with corrupted JSON file
            corrupted_filename = os.path.join(temp_dir, "corrupted.json")
            with open(corrupted_filename, 'w') as f:
                f.write("invalid json content {")
            
            corrupted_load_result = error_system.load_state(corrupted_filename)
            self.assertFalse(corrupted_load_result["success"], "Loading corrupted file should fail")
            self.assertEqual(corrupted_load_result["error"], "LOAD_ERROR",
                           "Should return LOAD_ERROR for corrupted file")


if __name__ == '__main__':
    unittest.main()