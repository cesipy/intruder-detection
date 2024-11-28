import time


def function(counter: int):
    print(f"hello world from main2: {counter}")
    
    
    
def main(): 
    counter = 1
    while True:
        counter += 1
        function(counter)
        time.sleep(1)
        
        
main()