import matplotlib.pyplot as plt
from collections import deque
import numpy as np


class RTTMetricsCollector:

    def __init__(self, n=30, maxlen=1000):

        # n is when to update the graphs
        self.n = n
        self.current_n = 0
        
        self.rtt_values = deque(maxlen=maxlen)    # store RTT times
        
    def _should_plot(self) -> bool:
        self.current_n += 1
        if self.current_n >= self.n: 
            self.current_n = 0
            return True
        return False
        
    def update_rtt(self, rtt_value):

        # genai came up with this boxplot implementation
        self.rtt_values.append(rtt_value)
        
        if not self._should_plot():
            return
            
        plt.figure(1)
        plt.clf()
        
        # Create boxplot
        plt.boxplot(list(self.rtt_values), labels=['RTT'])
        plt.title("Round Trip Time Distribution")
        plt.ylabel("RTT (ms)")
        
        # Add a text box with statistics
        if len(self.rtt_values) > 0:
            stats_text = f'Mean: {np.mean(self.rtt_values):.1f}ms\n'
            stats_text += f'Median: {np.median(self.rtt_values):.1f}ms\n'
            stats_text += f'Std: {np.std(self.rtt_values):.1f}ms'
            plt.text(1.3, np.median(self.rtt_values), stats_text, 
                    bbox=dict(facecolor='white', alpha=0.8))
            
        plt.grid(True, axis='y')
        
      
        plt.savefig('res/plots/rtt_distribution.png')

        