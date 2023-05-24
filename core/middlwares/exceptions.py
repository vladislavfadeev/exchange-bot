


class MinAmountError(Exception):
    pass


class MaxAmountError(Exception):
    pass


class MaxLenError(Exception):
    pass


class ResponseError(Exception):
    def __str__(self):
        return(
            'Responce status code does not '
            'match the expected code'
        )