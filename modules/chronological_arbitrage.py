import numpy as np
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import random
from scipy.signal import butter, filtfilt

@dataclass
class TemporalWeakPoint:
    timestamp: float
    pattern_strength: float
    keystroke_pattern: List[float]

class ChronologicalArbitrageEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self._initialize_consciousness_state()
        self.current_mode = None
        self.current_pattern_index = 0
        self.pattern_templates = {
            'easy': [],
            'moderate': [],
            'complex': []
        }
        self.leaderboard = {'easy': [], 'moderate': [], 'complex': []}

    def start_game(self, mode: str) -> str:
        """Start a new pattern matching game."""
        if mode not in ['easy', 'moderate', 'complex']:
            raise ValueError(f"Invalid mode: {mode}")
        
        # Generate new patterns for this session
        self.pattern_templates[mode] = self._generate_patterns(10, 
            complexity=1 if mode == 'easy' else 2 if mode == 'moderate' else 3)
        
        self.current_mode = mode
        self.current_pattern_index = 0
        
        # Initialize state with empty arrays
        self.consciousness_state = {
            'patterns_completed': 0,
            'accuracy_history': [],
            'timing_history': [],
            'neural_resonance': 0.3,
            'quantum_coherence': 0.3,
            'reality_stability': 0.3,
            'time_compression_ratio': 1.0,
            'experience_depth': 0.1,
            'reality_anchor_points': [],
            'timeline_branches': []
        }
        
        # Return the first pattern
        pattern = self._get_next_pattern()
        if not pattern:
            raise ValueError("Failed to generate pattern")
        return pattern

    def _generate_patterns(self, count: int, complexity: int) -> List[str]:
        """Generate temporal patterns with specified complexity."""
        patterns = []
        
        # Word banks for pattern generation
        quantum_words = ["quantum", "temporal", "neural", "cosmic", "photon", "wave", "flux", "sync", "pulse", "phase"]
        action_words = ["leap", "shift", "flow", "drift", "surge", "dive", "bend", "warp", "fold", "loop"]
        sequence_words = ["sequence", "pattern", "matrix", "field", "stream", "chain", "array", "grid", "mesh", "web"]
        identifier_words = ["alpha", "beta", "gamma", "delta", "omega", "prime", "core", "node", "apex", "zero"]
        
        for _ in range(count):
            pattern_words = []
            
            # Always add these two words for all modes
            pattern_words.append(random.choice(quantum_words))
            pattern_words.append(random.choice(action_words))
            pattern_words.append(random.choice(identifier_words))
            
            # Add additional words based on complexity
            if complexity >= 2:  # Moderate
                pattern_words.insert(2, random.choice(sequence_words))
            
            if complexity >= 3:  # Complex
                pattern_words.insert(3, random.choice(quantum_words))
            
            # Join words with dots
            pattern = ".".join(pattern_words)
            patterns.append(pattern)
        
        return patterns

    def _get_next_pattern(self) -> Optional[str]:
        """Get the next pattern in the sequence."""
        if not self.current_mode:
            return None
            
        patterns = self.pattern_templates[self.current_mode]
        if not patterns or self.current_pattern_index >= len(patterns):
            return None
            
        pattern = patterns[self.current_pattern_index]
        self.current_pattern_index += 1
        return pattern

    def check_pattern(self, input_pattern: str) -> tuple[bool, float]:
        """Check if input pattern matches current pattern and calculate score."""
        if not self.current_mode or self.current_pattern_index <= 0:
            return False, 0.0

        patterns = self.pattern_templates[self.current_mode]
        if self.current_pattern_index > len(patterns):
            return False, 0.0

        target_pattern = patterns[self.current_pattern_index - 1]
        correct = input_pattern.strip().lower() == target_pattern.strip().lower()  # Case-insensitive comparison

        if correct:
            # Calculate base score based on pattern complexity
            complexity_multiplier = {
                'easy': 1.0,
                'moderate': 1.5,
                'complex': 2.0
            }[self.current_mode]
            
            # Calculate score components
            base_score = 50.0 * complexity_multiplier
            speed_bonus = self.consciousness_state['time_compression_ratio'] * 10
            accuracy = 100.0  # Perfect match
            
            # Update state
            self.consciousness_state['accuracy_history'].append(accuracy)
            self.consciousness_state['timing_history'].append(speed_bonus)
            self.consciousness_state['patterns_completed'] += 1
            
            # Update consciousness state
            self._update_consciousness_state(1.0)  # Perfect accuracy
            
            # Calculate total score
            total_score = base_score + speed_bonus
            
            # Update leaderboard
            self._update_leaderboard(self.current_mode, total_score)
            
            return True, total_score

        return False, 0.0

    def _initialize_consciousness_state(self):
        """Initialize consciousness state with default values."""
        self.consciousness_state = {
            'patterns_completed': 0,
            'accuracy_history': [],
            'timing_history': [],
            'neural_resonance': 0.3,
            'quantum_coherence': 0.3,
            'reality_stability': 0.3,
            'time_compression_ratio': 1.0,
            'experience_depth': 0.1,
            'reality_anchor_points': [],
            'timeline_branches': []
        }

    def _update_consciousness_state(self, accuracy: float):
        """Update consciousness state based on performance."""
        # Update neural resonance (more gradual changes)
        self.consciousness_state['neural_resonance'] = min(1.0, 
            self.consciousness_state['neural_resonance'] * 0.8 + accuracy * 0.2)
        
        # Update quantum coherence based on pattern completion
        total_patterns = len(self.pattern_templates[self.current_mode])
        progress_ratio = self.consciousness_state['patterns_completed'] / total_patterns
        self.consciousness_state['quantum_coherence'] = min(1.0, 
            self.consciousness_state['quantum_coherence'] * 0.7 + progress_ratio * 0.3)
        
        # Update reality stability
        self.consciousness_state['reality_stability'] = min(1.0,
            (self.consciousness_state['neural_resonance'] + 
             self.consciousness_state['quantum_coherence']) / 2)
        
        # Update time compression ratio
        self.consciousness_state['time_compression_ratio'] = 1.0 + (
            self.consciousness_state['quantum_coherence'] * 2.0 * 
            (self.consciousness_state['patterns_completed'] / total_patterns)
        )

    def _update_leaderboard(self, mode: str, score: float):
        """Update leaderboard with new score."""
        self.leaderboard[mode] = sorted(
            self.leaderboard[mode] + [score],
            reverse=True
        )[:5]  # Keep top 5 scores

    def get_leaderboard(self) -> Dict[str, List[float]]:
        """Get current leaderboard."""
        return self.leaderboard

    def generate_pattern(self, sequence: str) -> dict:
        """Generate visualization data for a temporal pattern."""
        # Calculate base metrics
        neural_resonance = self.consciousness_state['neural_resonance']
        dilation_level = self.consciousness_state['time_compression_ratio']
        
        # Generate wave pattern based on sequence
        wave_pattern = []
        for char in sequence:
            # Convert character to numeric value and normalize
            value = (ord(char) - 32) / 95  # Printable ASCII range
            # Add some variance based on neural resonance
            variance = np.random.normal(0, 0.1 * neural_resonance)
            wave_pattern.extend([
                value + variance,
                value * 0.8 + variance,
                value * 0.6 + variance
            ])
        
        # Smooth the pattern
        if len(wave_pattern) > 3:
            wave_pattern = np.convolve(wave_pattern, [0.3, 0.4, 0.3], mode='valid')
        
        return {
            'wave_pattern': wave_pattern,
            'neural_resonance': neural_resonance,
            'dilation_level': dilation_level
        }