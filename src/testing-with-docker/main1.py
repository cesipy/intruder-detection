import time


def function(counter: int):
    print(f"bye world from main1: {counter}")
    
    
    
def main(): 
    while True:
        function(1)
        time.sleep(1)
        
        
main()