import matplotlib.pyplot as plt
import numpy as np
from collections import deque

from config import *


class MetricsCollector:

    def __init__(self, n=30):
        # n is when to update the graphs
        self.n = n
        self.current_n = 0
        
        # store the metrics
        self.edge_latencies = deque(maxlen=1000)    # store last 100 edge processing times
        self.cloud_latencies = deque(maxlen=1000)   # store last 100 cloud processing times
        
        self.counter_edge_latencies  = 0
        self.counter_cloud_latencies = 0
        self.counter_yolo_ratios     = 0
        self.counter_intruder_ratios = 0    
        
            
    def _should_plot(self) -> bool:
        self.current_n += 1
        if self.current_n >= self.n: 
            self.current_n = 0
            return True
        return False
        
    def plot_edge_latencies(self, edge_latency):
        try:
            # genai came up with the boxplot function, aswell as others here
            # Store the new latency
            
            if np.isnan(edge_latency) or edge_latency <= 0:  # Skip invalid values
                return
            self.edge_latencies.append(edge_latency)
            
            # Ensure we have enough valid data points and it's time to plot
            if not self._should_plot() or len(self.edge_latencies) < 5:  
                return
                
            # Get valid data points for plotting
            data = [x for x in self.edge_latencies if not np.isnan(x) and x > 0]
            if len(data) < 5:  # Need minimum points for meaningful boxplot
                return
                    
            plt.figure(1)
            plt.clf()
            
            # Create boxplot using validated data
            plt.boxplot(data, tick_labels=['Edge'])
            plt.title("Edge Processing Latency Distribution")
            plt.ylabel("Latency (ms)")
            
            # Add a text box with statistics
            if len(data) > 0:
                stats_text = f'Mean: {np.mean(data):.1f}ms\n'
                stats_text += f'Median: {np.median(data):.1f}ms\n'
                stats_text += f'Std: {np.std(data):.1f}ms'
                
                # Position text box relative to the median of valid data
                median_pos = np.median(data)
                plt.text(1.3, median_pos, stats_text, 
                        bbox=dict(facecolor='white', alpha=0.8))
                    
            plt.grid(True, axis='y')
            
            self.counter_edge_latencies += 1
            filename = generate_file_name("edge_latencies", PLOT_PATH_PREFIX, self.counter_edge_latencies)
            plt.savefig(filename)
        except Exception as e:
            print(f"Error in plot_edge_latencies: {e}")
            return
        
            
    def plot_cloud_latencies(self, cloud_latency):
        try:
            if np.isnan(cloud_latency) or cloud_latency <= 0:  # Skip invalid values
                return
            
            self.cloud_latencies.append(cloud_latency)
            
            # Ensure we have enough valid data points and it's time to plot
            if not self._should_plot() or len(self.cloud_latencies) < 5: 
                return
            
            # Get valid data points for plotting
            data = [x for x in self.cloud_latencies if not np.isnan(x) and x > 0]
            if len(data) < 5:  # Need minimum points for meaningful boxplot
                return
                    
            plt.figure(2)
            plt.clf()
            
            # Create boxplot using validated data
            plt.boxplot(data, tick_labels=['Cloud'])
            plt.title("Cloud Processing Latency Distribution")
            plt.ylabel("Latency (ms)")
            
            # Add a text box with statistics
            if len(data) > 0:
                stats_text = f'Mean: {np.mean(data):.1f}ms\n'
                stats_text += f'Median: {np.median(data):.1f}ms\n'
                stats_text += f'Std: {np.std(data):.1f}ms'
                
                # Position text box relative to the median of valid data
                median_pos = np.median(data)
                plt.text(1.3, median_pos, stats_text, 
                        bbox=dict(facecolor='white', alpha=0.8))
                    
            plt.grid(True, axis='y')
            
            self.counter_cloud_latencies += 1
            filename = generate_file_name("cloud_latencies", PLOT_PATH_PREFIX, self.counter_cloud_latencies)
            plt.savefig(filename)
            
        except Exception as e:
            print(f"Error in plot_cloud_latencies: {e}")
            return
    
        
    def plot_yolo_ratio(self, total_requests, total_detections):
        try: 
            if not self._should_plot():
                return
            plt.figure(3)
            plt.clf()
            
            no_detections = total_requests - total_detections
            ratio = (total_detections / max(1, total_requests)) * 100  
            
            labels = ['No Detection', 'Detection']
            values = [no_detections, total_detections]
            colors = ['lightgray', 'lightgreen']
            
            plt.bar(labels, values, color=colors)
            plt.title(f"YOLO Detection Statistics\nDetection Rate: {ratio:.1f}%")
            plt.ylabel("Number of Frames")
            
            # Add value labels on top of bars
            for i, v in enumerate(values):
                plt.text(i, v, str(v), ha='center', va='bottom')
                
            plt.grid(True, axis='y')
            
            self.counter_yolo_ratios += 1
            filename = generate_file_name("yolo_ratios", PLOT_PATH_PREFIX, self.counter_yolo_ratios)
            plt.savefig(filename)
        
        except Exception as e:
            print(f"Error in plot_yolo_ratio: {e}")
            return
        
        
    def plot_intruder_ratio(self, total_requests, total_detections):
        try: 
            # Basic input validation
            if not isinstance(total_requests, (int, float)) or not isinstance(total_detections, (int, float)):
                print("Invalid input types for plot_intruder_ratio")
                return
                
            if total_requests < 0 or total_detections < 0:
                print("Negative values not allowed in plot_intruder_ratio")
                return
                
            if total_detections > total_requests:
                print("Number of detections cannot be greater than total requests")
                return
                
            # Only plot when it's time to update
            if not self._should_plot():
                return
                
            # Skip if we don't have any data to plot
            if total_requests == 0:
                return
                
            plt.figure(4)
            plt.clf()
            
            # Calculate metrics
            no_intruders = total_requests - total_detections
            
            # Ensure we have valid numbers for plotting
            if no_intruders <= 0 and total_detections <= 0:
                print("No valid data to plot")
                return
                
            # Create pie chart with validated data
            labels = [f'No Intruder\n{no_intruders} frames', 
                    f'Intruder Detected\n{total_detections} frames']
            sizes = [no_intruders, total_detections]
            colors = ['lightgray', 'salmon']
            
            # Only create pie chart if we have valid non-zero values
            if sum(sizes) > 0:
                plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                    shadow=True, startangle=90)
                plt.title(f"Cloud Intruder Detection\nTotal Processed: {total_requests}")
                plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                
                self.counter_intruder_ratios += 1
                filename = generate_file_name("intruder_ratios", PLOT_PATH_PREFIX, self.counter_intruder_ratios)
                plt.savefig(filename)
            
        except Exception as e:
            print(f"Error in plot_intruder_ratio: {e}")
            return


def generate_file_name( metric: str, path_prefix: str, counter : int): 
    #return f"{path_prefix}/{metric}_{counter}.png"
    return f"{path_prefix}/{metric}.png"


if __name__ == "__main__":
    # Example usage and testing
    collector = MetricsCollector(n=10)
    
    # Simulate some metrics
    for i in range(500):
        # Simulate edge processing
        edge_latency = np.random.normal(100, 20)  # mean 100ms, std 20ms
        collector.plot_edge_latencies(edge_latency)
        
        # Simulate cloud processing 
        cloud_latency = np.random.normal(200, 40)  # mean 200ms, std 40ms
        collector.plot_cloud_latencies(cloud_latency)
        
        # Simulate detection counts
        total_yolo = i + 1
        yolo_detections = np.random.randint(0, total_yolo)
        collector.plot_yolo_ratio(total_yolo, yolo_detections)
        
        total_cloud = i + 1
        intruder_detections = np.random.randint(0, total_cloud)
        collector.plot_intruder_ratio(total_cloud, intruder_detections)
        
