from pydantic import BaseModel as PydanticBaseModel, field_validator

# class BaseModel(PydanticBaseModel):
#     @field_validator('*')
#     def input_validation(cls, value):
#         if value == '':
#             raise ValueError("Input cannot be an empty string")
#         return value


class BaseModel(PydanticBaseModel):
    @field_validator("*")
    def input_validation(cls, value):
        if value == "":
            return None
        elif isinstance(value, str):
            input_str = value.strip()
            if input_str == "":
                return None
            return input_str
        return value
