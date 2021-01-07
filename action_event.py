class Action:
    
    def __init__(self, higher: bool, limit:float):
        self.higher = higher
        self.limit = limit
        self.action_notified = False
    

    def notify_event(self):
        self.action_notified = True
    
    def notification_should_trigger(self, current_value:float):
        current_value = float(current_value)
        if self.action_notified:
            return False
        elif self.higher:
            if current_value > self.limit:
                return True
        else:
            if current_value < self.limit:
                return True
        return False

    def __str__(self):
        completed = "no"
        if self.action_notified:
            completed = "yes"
        if self.higher:
            return str(self.limit) + " : higher : " + completed
        else:
            return str(self.limit) + " : lower : " + completed
