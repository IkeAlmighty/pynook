import uuid

class SwitchContext:
    def __init__(self):
        self.expr_id = f"___switch_expr_{uuid.uuid4()}___"        
        self.end_jumps = []
