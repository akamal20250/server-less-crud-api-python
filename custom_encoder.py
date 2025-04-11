import json
from decimal import Decimal

# ====================================================================
# Class: CustomEncoder
# ====================================================================
# Extends the default JSONEncoder to convert Decimal types from DynamoDB to float,
# ensuring that JSON serialization works properly.
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)  
