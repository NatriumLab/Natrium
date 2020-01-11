from starlette.responses import JSONResponse as Response

def error_handle(exception):
    return Response({
        "error": exception.error,
        "errorMessage": exception.message
    }, status_code=exception.code)
