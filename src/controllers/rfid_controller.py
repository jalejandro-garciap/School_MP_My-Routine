import threading
from database.database_operations import get_passenger_by_card_id, has_exercised_today

class RfidController:

    def __init__(self):
        
        self.passenger = None
        self.scanned_card = False
        self.card_id = None
        self.message = None

        self.read_thread = threading.Thread(target=self.read_card)
        self.read_thread.daemon = True

    def validate_card(self, card_id):
        return get_passenger_by_card_id(card_id)

    def read_card(self):
        while not self.scanned_card:
            try:
                data = input("").strip()  
                self.card_id = data  
                passenger = self.validate_card(data)
                
                if passenger:

                    #print(f"Card read: {data}")
                    if has_exercised_today(passenger.id):
                        self.message = "This user has reached their exercise limit"
                    else:
                        self.passenger = passenger
                        self.scanned_card = True
                        self.message = None

                else:
                    #print(f"Card read: {data} - Not found")
                    self.message = "This card is not registered"

            except KeyboardInterrupt:
                #print("RFID reading interrupted by user.")
                break
    
    def start_reading(self):
        if not self.read_thread.is_alive():
            self.read_thread.start()

    def stop_reading(self):
        self.scanned_card = True 