
class CompilerException(Exception):

    def __init__(self, message, location):
        super().__init__(message)
        self.message = message
        self.location = location


    def get_error_message(self):
        with open(self.location.filepath) as f:
            source = f.readlines()

            err_msg = "\033[31m"
            err_msg += source[self.location.row] 
            err_msg += " " * self.location.col 
            err_msg += "^\n" + self.message
            err_msg += f"\nline {self.location.row}, column {self.location.col}"
            err_msg += "\033[0m"

            return err_msg


