from starlette.responses import JSONResponse as Response

class OriginException(Exception):
    NoAnyMoreConfiure = False
    metadata = None

    def __init__(self, metadata=None, error=None, errorMessage=None, code=None, message="SomethingWrong"):
        if not self.NoAnyMoreConfiure:
            self.error = error
            self.message = errorMessage,
            self.code = code
        if metadata:
            self.metadata = metadata
        super().__init__(message)

    def json(self):
        return {
            "error": self.error,
            "errorMessage": self.message
        } if not self.metadata else {
            "error": self.error,
            "errorMessage": self.message,
            "metadata": self.metadata
        }

    def response(self):
        return Response(self.json(), status_code=self.code)