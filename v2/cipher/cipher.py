from fastapi import APIRouter
from starlette.responses import PlainTextResponse
from src import function
from src import schema

router = APIRouter(prefix="/cipher", tags=["cipher"])

RESPONSE_CLASS = PlainTextResponse  # Introduce constant


async def process_request(body_data: str, mode: str) -> PlainTextResponse:
    """
    Processes a request for encryption or decryption using the Cipher class.

    This function takes input data and a specified mode (encryption or
    decryption) and processes it. It validates the mode to determine the
    operation to perform and then uses the Cipher object to execute the
    respective operation. An Exception is raised if an invalid mode
    is specified. A response containing the processed text is returned.

    :param body_data: The text input that needs to be encrypted or decrypted.
    :type body_data: str
    :param mode: The mode of operation, should be either "encryption"
        or "decryption".
    :type mode: str
    :return: A plain text response containing the result of the encryption
        or decryption operation.
    :rtype: PlainTextResponse
    :raises ValueError: If the mode is invalid (not "encryption" or
        "decryption").
    """
    cipher = function.Cipher(body_data)
    if mode == "encryption":
        result = cipher.encryption()
    elif mode == "decryption":
        result = cipher.decryption()
    else:
        raise ValueError("Invalid mode")
    return RESPONSE_CLASS(result)


@router.post("/encryption")
async def encrypt_data(body: schema.Encryption):
    """
    Encrypts the given data by processing the request with encryption mode. This
    API endpoint receives the required data through the request body in the
    defined schema and performs encryption using the specified business logic
    defined in the `process_request` function.

    :param body: Request body containing the data to be encrypted.
    :type body: schema.Encryption
    :return: The encrypted version of the input data.
    :rtype: Any
    """
    return await process_request(body.data, mode="encryption")


@router.post("/decryption")
async def decrypt_data(body: schema.Decryption):
    """
    Decrypts the provided data using the decryption process. This endpoint
    accepts an input schema, processes the submitted data, and returns
    the decrypted result. It leverages the `process_request` function to
    execute the decryption logic.

    :param body: The body of the request payload, which should conform to
        the `schema.Decryption` schema. It holds the data to be decrypted.
    :type body: schema.Decryption
    :return: The decrypted data that was processed in "decryption" mode.
    :rtype: Depends on the return type of `process_request` function.
    """
    return await process_request(body.data, mode="decryption")
