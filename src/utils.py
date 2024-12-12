class Frame:
    
    def __init__(self, frame_name, frame_data):
        self.frame_name = frame_name
        self.frame_data = frame_data
        
    def __str__(self):
        # we dont want to get the full data
        return f'Frame name: {self.frame_name}, Length of frame data: {len(self.frame_data)}'
    
    def get_explicit_string(self) -> str:
        return f'Frame name: {self.frame_name}, Frame data: {self.frame_data}'