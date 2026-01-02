"""
Tkinter GUI Application for Blockchain Voting System
Desktop application interface as specified in the project document
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
from datetime import datetime
import os
import sys

# Add parent directory to path to import blockchain modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain_voting.voting.voting_system import VotingSystem


class BlockchainVotingGUI:
    """Main GUI application for blockchain voting system"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Blockchain Voting System")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize voting system
        self.voting_system = VotingSystem()
        
        # Try to load existing data
        self.load_system_state()
        
        # Create GUI components
        self.create_widgets()
        
        # Update display
        self.refresh_display()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main title
        title_label = tk.Label(
            self.root, 
            text="Blockchain Voting System", 
            font=("Arial", 20, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create tabs
        self.create_voter_registration_tab()
        self.create_voting_tab()
        self.create_mining_tab()
        self.create_results_tab()
        self.create_blockchain_tab()
        self.create_admin_tab()
    
    def create_voter_registration_tab(self):
        """Create voter registration tab"""
        reg_frame = ttk.Frame(self.notebook)
        self.notebook.add(reg_frame, text="Voter Registration")
        
        # Registration section
        reg_section = ttk.LabelFrame(reg_frame, text="Register New Voter", padding=20)
        reg_section.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(reg_section, text="Voter ID:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.voter_id_entry = tk.Entry(reg_section, font=("Arial", 12), width=30)
        self.voter_id_entry.grid(row=0, column=1, padx=10, pady=5)
        
        register_btn = tk.Button(
            reg_section, 
            text="Register Voter", 
            command=self.register_voter,
            bg='#3498db',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20
        )
        register_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # Registered voters display
        voters_section = ttk.LabelFrame(reg_frame, text="Registered Voters", padding=20)
        voters_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.voters_listbox = tk.Listbox(voters_section, font=("Arial", 11))
        voters_scrollbar = ttk.Scrollbar(voters_section, orient=tk.VERTICAL, command=self.voters_listbox.yview)
        self.voters_listbox.configure(yscrollcommand=voters_scrollbar.set)
        
        self.voters_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        voters_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_voting_tab(self):
        """Create voting tab"""
        vote_frame = ttk.Frame(self.notebook)
        self.notebook.add(vote_frame, text="Cast Vote")
        
        # Voting section
        vote_section = ttk.LabelFrame(vote_frame, text="Cast Your Vote", padding=20)
        vote_section.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(vote_section, text="Voter ID:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.vote_voter_id_entry = tk.Entry(vote_section, font=("Arial", 12), width=20)
        self.vote_voter_id_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(vote_section, text="Candidate:", font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.candidate_entry = tk.Entry(vote_section, font=("Arial", 12), width=20)
        self.candidate_entry.grid(row=1, column=1, padx=10, pady=5)
        
        vote_btn = tk.Button(
            vote_section, 
            text="Cast Vote", 
            command=self.cast_vote,
            bg='#27ae60',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20
        )
        vote_btn.grid(row=0, column=2, rowspan=2, padx=20, pady=5)
        
        # Pending votes display
        pending_section = ttk.LabelFrame(vote_frame, text="Pending Votes", padding=20)
        pending_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.pending_votes_text = scrolledtext.ScrolledText(
            pending_section, 
            height=10, 
            font=("Courier", 10),
            state=tk.DISABLED
        )
        self.pending_votes_text.pack(fill=tk.BOTH, expand=True)
    
    def create_mining_tab(self):
        """Create mining/block creation tab"""
        mining_frame = ttk.Frame(self.notebook)
        self.notebook.add(mining_frame, text="Mining")
        
        # Mining section
        mining_section = ttk.LabelFrame(mining_frame, text="Block Mining", padding=20)
        mining_section.pack(fill=tk.X, padx=20, pady=10)
        
        mine_btn = tk.Button(
            mining_section, 
            text="Mine Pending Votes into Block", 
            command=self.mine_block,
            bg='#e67e22',
            fg='white',
            font=("Arial", 14, "bold"),
            padx=30,
            pady=10
        )
        mine_btn.pack(pady=10)
        
        # Mining status
        self.mining_status_label = tk.Label(
            mining_section, 
            text="Ready to mine", 
            font=("Arial", 12),
            fg='#7f8c8d'
        )
        self.mining_status_label.pack(pady=5)
        
        # Blockchain info
        info_section = ttk.LabelFrame(mining_frame, text="Blockchain Information", padding=20)
        info_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.blockchain_info_text = scrolledtext.ScrolledText(
            info_section, 
            height=15, 
            font=("Courier", 10),
            state=tk.DISABLED
        )
        self.blockchain_info_text.pack(fill=tk.BOTH, expand=True)
    
    def create_results_tab(self):
        """Create results display tab"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Results")
        
        # Results section
        results_section = ttk.LabelFrame(results_frame, text="Election Results", padding=20)
        results_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        refresh_btn = tk.Button(
            results_section, 
            text="Refresh Results", 
            command=self.refresh_results,
            bg='#9b59b6',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20
        )
        refresh_btn.pack(pady=10)
        
        self.results_text = scrolledtext.ScrolledText(
            results_section, 
            height=20, 
            font=("Courier", 12),
            state=tk.DISABLED
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
    
    def create_blockchain_tab(self):
        """Create blockchain viewer tab"""
        blockchain_frame = ttk.Frame(self.notebook)
        self.notebook.add(blockchain_frame, text="Blockchain")
        
        # Controls
        controls_section = ttk.LabelFrame(blockchain_frame, text="Blockchain Controls", padding=20)
        controls_section.pack(fill=tk.X, padx=20, pady=10)
        
        validate_btn = tk.Button(
            controls_section, 
            text="Validate Blockchain", 
            command=self.validate_blockchain,
            bg='#34495e',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20
        )
        validate_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_blockchain_btn = tk.Button(
            controls_section, 
            text="Refresh View", 
            command=self.refresh_blockchain_view,
            bg='#16a085',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20
        )
        refresh_blockchain_btn.pack(side=tk.LEFT, padx=5)
        
        # Blockchain display
        blockchain_section = ttk.LabelFrame(blockchain_frame, text="Blockchain Data", padding=20)
        blockchain_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.blockchain_text = scrolledtext.ScrolledText(
            blockchain_section, 
            height=20, 
            font=("Courier", 9),
            state=tk.DISABLED
        )
        self.blockchain_text.pack(fill=tk.BOTH, expand=True)
    
    def create_admin_tab(self):
        """Create admin/system tab"""
        admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(admin_frame, text="System")
        
        # File operations
        file_section = ttk.LabelFrame(admin_frame, text="Data Management", padding=20)
        file_section.pack(fill=tk.X, padx=20, pady=10)
        
        save_btn = tk.Button(
            file_section, 
            text="Save System State", 
            command=self.save_system_state,
            bg='#2ecc71',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20
        )
        save_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        load_btn = tk.Button(
            file_section, 
            text="Load System State", 
            command=self.load_system_state,
            bg='#3498db',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20
        )
        load_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        reset_btn = tk.Button(
            file_section, 
            text="Reset System", 
            command=self.reset_system,
            bg='#e74c3c',
            fg='white',
            font=("Arial", 12, "bold"),
            padx=20
        )
        reset_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # System status
        status_section = ttk.LabelFrame(admin_frame, text="System Status", padding=20)
        status_section.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.status_text = scrolledtext.ScrolledText(
            status_section, 
            height=15, 
            font=("Courier", 10),
            state=tk.DISABLED
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
    
    def register_voter(self):
        """Register a new voter"""
        voter_id = self.voter_id_entry.get().strip()
        
        if not voter_id:
            messagebox.showerror("Error", "Please enter a voter ID")
            return
        
        result = self.voting_system.register_voter(voter_id)
        
        if result['success']:
            messagebox.showinfo("Success", f"Voter '{voter_id}' registered successfully!")
            self.voter_id_entry.delete(0, tk.END)
            self.refresh_display()
        else:
            messagebox.showerror("Error", result['message'])
    
    def cast_vote(self):
        """Cast a vote"""
        voter_id = self.vote_voter_id_entry.get().strip()
        candidate = self.candidate_entry.get().strip()
        
        if not voter_id or not candidate:
            messagebox.showerror("Error", "Please enter both voter ID and candidate")
            return
        
        result = self.voting_system.cast_vote(voter_id, candidate)
        
        if result['success']:
            messagebox.showinfo("Success", f"Vote cast successfully for '{candidate}'!")
            self.vote_voter_id_entry.delete(0, tk.END)
            self.candidate_entry.delete(0, tk.END)
            self.refresh_display()
        else:
            messagebox.showerror("Error", result['message'])
    
    def mine_block(self):
        """Mine pending votes into a new block"""
        if not self.voting_system.pending_votes:
            messagebox.showwarning("Warning", "No pending votes to mine")
            return
        
        result = self.voting_system.create_block_from_pending_votes()
        
        if result['success']:
            messagebox.showinfo("Success", f"Block mined successfully! Block #{result['block_index']} created.")
            self.refresh_display()
        else:
            messagebox.showerror("Error", result['message'])
    
    def refresh_results(self):
        """Refresh and display election results"""
        results = self.voting_system.get_results()
        
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        if results['success']:
            content = "ELECTION RESULTS\n"
            content += "=" * 50 + "\n\n"
            
            if results['vote_counts']:
                content += "Vote Counts by Candidate:\n"
                content += "-" * 30 + "\n"
                for candidate, count in results['vote_counts'].items():
                    content += f"  {candidate}: {count} votes\n"
                
                content += f"\nTotal Votes Cast: {results['total_votes']}\n"
                content += f"Total Blocks: {results['total_blocks']}\n"
                content += f"Blockchain Valid: {'Yes' if results['blockchain_valid'] else 'No'}\n"
            else:
                content += "No votes have been cast yet.\n"
            
            content += f"\nLast Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        else:
            content = f"Error retrieving results: {results['message']}"
        
        self.results_text.insert(tk.END, content)
        self.results_text.config(state=tk.DISABLED)
    
    def validate_blockchain(self):
        """Validate blockchain integrity"""
        result = self.voting_system.validate_system_integrity()
        
        if result['blockchain_valid']:
            messagebox.showinfo("Validation", "Blockchain is valid and secure!")
        else:
            messagebox.showerror("Validation", "Blockchain validation failed!")
        
        self.refresh_display()
    
    def refresh_blockchain_view(self):
        """Refresh blockchain display"""
        self.blockchain_text.config(state=tk.NORMAL)
        self.blockchain_text.delete(1.0, tk.END)
        
        content = "BLOCKCHAIN DATA\n"
        content += "=" * 60 + "\n\n"
        
        for i, block in enumerate(self.voting_system.blockchain.chain):
            content += f"Block #{block.index}\n"
            content += f"   Timestamp: {datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"   Previous Hash: {block.previous_hash[:16]}...\n"
            content += f"   Current Hash:  {block.hash[:16]}...\n"
            content += f"   Votes in Block: {len(block.votes)}\n"
            
            if block.votes:
                content += "   Votes:\n"
                for vote in block.votes:
                    content += f"      • {vote.voter_id} → {vote.candidate}\n"
            
            content += "\n" + "-" * 60 + "\n\n"
        
        self.blockchain_text.insert(tk.END, content)
        self.blockchain_text.config(state=tk.DISABLED)
    
    def save_system_state(self):
        """Save system state to file"""
        try:
            filename = "blockchain_voting_state.json"
            success = self.voting_system.save_state(filename)
            
            if success:
                messagebox.showinfo("Success", f"System state saved to {filename}")
            else:
                messagebox.showerror("Error", "Failed to save system state")
        except Exception as e:
            messagebox.showerror("Error", f"Save failed: {str(e)}")
    
    def load_system_state(self):
        """Load system state from file"""
        try:
            filename = "blockchain_voting_state.json"
            if os.path.exists(filename):
                success = self.voting_system.load_state(filename)
                if success:
                    self.refresh_display()
                    messagebox.showinfo("Success", f"System state loaded from {filename}")
                else:
                    messagebox.showerror("Error", "Failed to load system state")
        except Exception as e:
            # Silently fail on startup if no save file exists
            pass
    
    def reset_system(self):
        """Reset the entire system"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the entire system? This will delete all data."):
            self.voting_system = VotingSystem()
            self.refresh_display()
            messagebox.showinfo("Reset", "System has been reset successfully")
    
    def refresh_display(self):
        """Refresh all display elements"""
        # Update registered voters list
        self.voters_listbox.delete(0, tk.END)
        for voter_id in self.voting_system.voter_manager.get_registered_voters():
            status = "Voted" if self.voting_system.voter_manager.has_voted(voter_id) else "Not Voted"
            self.voters_listbox.insert(tk.END, f"{voter_id} - {status}")
        
        # Update pending votes
        self.pending_votes_text.config(state=tk.NORMAL)
        self.pending_votes_text.delete(1.0, tk.END)
        
        if self.voting_system.pending_votes:
            content = f"Pending Votes ({len(self.voting_system.pending_votes)}):\n"
            content += "-" * 40 + "\n"
            for vote in self.voting_system.pending_votes:
                timestamp = datetime.fromtimestamp(vote.timestamp).strftime('%H:%M:%S')
                content += f"[{timestamp}] {vote.voter_id} → {vote.candidate}\n"
        else:
            content = "No pending votes"
        
        self.pending_votes_text.insert(tk.END, content)
        self.pending_votes_text.config(state=tk.DISABLED)
        
        # Update mining status
        pending_count = len(self.voting_system.pending_votes)
        if pending_count > 0:
            self.mining_status_label.config(
                text=f"Ready to mine {pending_count} pending vote(s)",
                fg='#27ae60'
            )
        else:
            self.mining_status_label.config(
                text="No pending votes to mine",
                fg='#7f8c8d'
            )
        
        # Update blockchain info
        self.blockchain_info_text.config(state=tk.NORMAL)
        self.blockchain_info_text.delete(1.0, tk.END)
        
        info_content = f"Blockchain Status:\n"
        info_content += f"   Total Blocks: {len(self.voting_system.blockchain.chain)}\n"
        info_content += f"   Total Votes: {len(self.voting_system.blockchain.get_all_votes())}\n"
        info_content += f"   Pending Votes: {len(self.voting_system.pending_votes)}\n"
        info_content += f"   Blockchain Valid: {'Yes' if self.voting_system.blockchain.validate_chain() else 'No'}\n"
        
        self.blockchain_info_text.insert(tk.END, info_content)
        self.blockchain_info_text.config(state=tk.DISABLED)
        
        # Update system status
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        
        status_content = f"System Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        status_content += "=" * 50 + "\n"
        status_content += f"Registered Voters: {len(self.voting_system.voter_manager.get_registered_voters())}\n"
        status_content += f"Voters Who Voted: {len(self.voting_system.voter_manager.get_voted_voters())}\n"
        status_content += f"Pending Votes: {len(self.voting_system.pending_votes)}\n"
        status_content += f"Blockchain Blocks: {len(self.voting_system.blockchain.chain)}\n"
        status_content += f"Total Votes in Chain: {len(self.voting_system.blockchain.get_all_votes())}\n"
        status_content += f"System Integrity: {'Valid' if self.voting_system.validate_system_integrity()['blockchain_valid'] else 'Invalid'}\n"
        
        self.status_text.insert(tk.END, status_content)
        self.status_text.config(state=tk.DISABLED)


def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = BlockchainVotingGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()