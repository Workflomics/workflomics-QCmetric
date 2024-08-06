"""
Defining own exceptions for schema validation errors. 

"""

class SchemaValidationError(Exception):
    def __init__(self, message="The schema of the contents of the file is incorrect."):
        self.message = message
        super().__init__(self.message)
