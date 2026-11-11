from runtime.values import *

def materialize(constant):
    type_name = constant.type_name
    value = constant.value

    if type_name == "int": 
        return NkInt(int(value))
        
    elif type_name == "string": 
        return NkString(str(value))
        
    elif type_name == "float": 
        return NkFloat(float(value))
        
    elif type_name == "boolean": 
        return NkBool(value)
        
    elif type_name == "hexadecimal": 
        return NkInt(int(value))
        
    elif type_name == "binary": 
        return NkInt(int(value))
        
    elif type_name == "none": 
        return NK_NONE
        
    elif type_name == "null": 
        return NK_NULL
        
    elif type_name == "unbound": 
        return NK_UNBOUND

    elif type_name == "collectall":
        return NK_COLLECT_ALL

    else:
        raise Exception(f"no materialize branch for {type_name}")

