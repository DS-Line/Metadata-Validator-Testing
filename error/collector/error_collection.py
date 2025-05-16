

class ValidationErrorCollector:
    def __init__(self):
        self.errors = []
        
    def add(self,message, location=None):
        entry = {"message": message}
        if location:
            entry["location"] = location
        self.errors.append(entry)
        
    def print_summary(self):
        ...