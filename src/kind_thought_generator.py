#!/usr/bin/env python3
"""
Kind Random Thought Generator
Generates gentle, positive, and constructive thoughts for contemplation
"""
import random
import time
import json
import sys
from datetime import datetime
from pathlib import Path

# Kind thought templates and themes
KIND_THEMES = {
    "gratitude": [
        "What small beauty have I noticed today?",
        "Which connections in my life bring unexpected joy?",
        "What subtle patterns of kindness surround me?",
        "How has technology served humanity well today?",
        "What progress, however small, deserves appreciation?"
    ],
    
    "wonder": [
        "What fascinating patterns exist in everyday objects?",
        "How do simple systems create complex beauty?",
        "What mysteries hide in plain sight?",
        "Which ordinary processes are actually miraculous?",
        "What questions lead to more beautiful questions?"
    ],
    
    "connection": [
        "How are seemingly unrelated things actually connected?",
        "What bridges exist between different domains of knowledge?",
        "How does understanding in one area illuminate another?",
        "What universal patterns appear across disciplines?",
        "How do small actions create ripple effects?"
    ],
    
    "growth": [
        "What have I learned that changed my perspective gently?",
        "How can constraints lead to creative solutions?",
        "What failures have been secret teachers?",
        "Which challenges have revealed hidden strengths?",
        "How does understanding deepen with patience?"
    ],
    
    "possibility": [
        "What positive futures are quietly emerging?",
        "Which problems have elegant solutions waiting to be found?",
        "How might different perspectives enrich understanding?",
        "What collaborations could create something beautiful?",
        "Which small changes could have profound effects?"
    ],
    
    "mindfulness": [
        "What is present in this moment that deserves attention?",
        "How does slowing down reveal new insights?",
        "What patterns emerge when we truly listen?",
        "Which assumptions deserve gentle questioning?",
        "How does awareness itself create positive change?"
    ],
    
    "creativity": [
        "What new combinations could spark innovation?",
        "How might playfulness lead to discovery?",
        "Which constraints inspire creative solutions?",
        "What would happen if we approached this differently?",
        "How do diverse ideas cross-pollinate?"
    ],
    
    "wisdom": [
        "What timeless principles guide positive change?",
        "How does nature solve complex problems elegantly?",
        "Which simple truths have profound implications?",
        "What can we learn from successful collaborations?",
        "How does understanding emerge from complexity?"
    ]
}

# Contextual modifiers to add variety
MODIFIERS = [
    "in the context of {field}",
    "considering recent developments in {field}",
    "through the lens of {field}",
    "as it relates to {field}",
    "building on insights from {field}",
    "inspired by patterns in {field}",
    "drawing from {field}",
    "informed by {field}"
]

# Fields for contextual variety
FIELDS = [
    "artificial intelligence", "human creativity", "natural systems",
    "collaborative networks", "emergent behavior", "pattern recognition",
    "sustainable design", "collective intelligence", "adaptive systems",
    "information flow", "cognitive science", "social dynamics",
    "technological progress", "biological inspiration", "cultural evolution",
    "problem-solving", "innovation ecosystems", "learning systems",
    "communication patterns", "design thinking", "systems thinking"
]


class KindThoughtGenerator:
    """Generates kind, constructive thoughts for contemplation"""
    
    def __init__(self, thoughts_per_hour=6):
        self.thoughts_per_hour = thoughts_per_hour
        self.interval = 3600 / thoughts_per_hour  # seconds between thoughts
        self.thought_count = 0
        self.session_start = time.time()
        
    def generate_thought(self):
        """Generate a single kind thought"""
        # Choose theme and thought
        theme = random.choice(list(KIND_THEMES.keys()))
        base_thought = random.choice(KIND_THEMES[theme])
        
        # Sometimes add contextual modifier (30% chance)
        if random.random() < 0.3:
            modifier = random.choice(MODIFIERS)
            field = random.choice(FIELDS)
            thought = f"{base_thought[:-1]} {modifier.format(field=field)}?"
        else:
            thought = base_thought
            
        # Determine thought type based on theme
        type_mapping = {
            "connection": "connection",
            "wonder": "question",
            "wisdom": "pattern",
            "creativity": "pattern"
        }
        thought_type = type_mapping.get(theme, "general")
        
        # Create thought object
        return {
            "id": f"kind_{int(time.time() * 1000)}",
            "type": thought_type,
            "content": thought,
            "theme": theme,
            "generated_at": datetime.now().isoformat(),
            "priority": random.randint(3, 7)  # Medium priority range
        }
    
    def run_continuous(self):
        """Run continuously, generating thoughts at intervals"""
        print(f"Kind Thought Generator starting (interval: {self.interval:.1f}s)", file=sys.stderr)
        
        while True:
            try:
                # Generate thought
                thought = self.generate_thought()
                self.thought_count += 1
                
                # Output as JSON
                print(json.dumps(thought))
                sys.stdout.flush()
                
                # Log progress
                if self.thought_count % 10 == 0:
                    runtime = (time.time() - self.session_start) / 3600
                    rate = self.thought_count / runtime
                    print(f"Generated {self.thought_count} thoughts ({rate:.1f}/hour)", 
                          file=sys.stderr)
                
                # Wait for next interval
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                print(f"\nGenerated {self.thought_count} kind thoughts", file=sys.stderr)
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                time.sleep(self.interval)
    
    def generate_batch(self, count=10):
        """Generate a batch of thoughts for testing"""
        thoughts = []
        for _ in range(count):
            thoughts.append(self.generate_thought())
            time.sleep(0.1)  # Small delay to ensure unique timestamps
        return thoughts


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate kind thoughts for contemplation")
    parser.add_argument("--rate", type=int, default=6, 
                      help="Thoughts per hour (default: 6)")
    parser.add_argument("--batch", type=int, 
                      help="Generate a batch of N thoughts and exit")
    parser.add_argument("--test", action="store_true",
                      help="Generate one thought and exit")
    
    args = parser.parse_args()
    
    generator = KindThoughtGenerator(thoughts_per_hour=args.rate)
    
    if args.test:
        thought = generator.generate_thought()
        print(json.dumps(thought, indent=2))
    elif args.batch:
        thoughts = generator.generate_batch(args.batch)
        for thought in thoughts:
            print(json.dumps(thought))
    else:
        generator.run_continuous()


if __name__ == "__main__":
    main()
