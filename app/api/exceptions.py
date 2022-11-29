class CustomException(Exception):
    def __init__(self, message: str, status: int = -1, status_code: int = 400):
        self.message = message
        self.status = status
        self.status_code = status_code
