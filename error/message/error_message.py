class ValidationMessage:
    """
    location, message, 'severity', category, hint, suggested_fix, 'auto-fix'

    """
    
    def __init__(
        self,
        message:str,
        location: str = None,
        severity: str = "error",
        category: str = None,
        hint: str = None,
        suggested_fix: str = None
    ):
        self.message = message
        self.location = location
        self.severity = severity
        self.category = category
        self.hint = hint
        self.suggested_fix = suggested_fix
    
    ...