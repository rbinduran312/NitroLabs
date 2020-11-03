import os
import uuid
from linepay import LinePayApi
import logging
import time
import tempfile

from dotenv import load_dotenv
from linepay.exceptions import LinePayApiError


load_dotenv()


logging.basicConfig(filename=os.path.join(tempfile.gettempdir(), 'line.log'), filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger('linepay')
logger.addHandler(logging.StreamHandler())


def _get_api():
    return LinePayApi(
        channel_id=os.getenv('LINE_CHANNEL_ID'),
        channel_secret=os.getenv('LINE_SECRET_KEY'),
        is_sandbox=os.getenv('LINE_SANDBOX').lower() == 'true')


def reserve_payment(order_id, product_id, product_name, currency="THB", image_url=""):
    request_options = {
        "amount": 0,
        "currency": currency,
        "orderId": order_id,
        "packages": [
            {
                "id": f"package-{product_id}",
                "amount": 0,
                "name": f"Package {product_name}",
                "products": [
                    {
                        "id": str(product_id),
                        "name": product_name,
                        "imageUrl": image_url,
                        "quantity": 0,
                        "price": 0
                    }
                ]
            }
        ],
        "options": {
            "payment": {
                "payType": "PREAPPROVED",
                "capture": True,
            }
        },
        "redirectUrls": {
            "confirmUrl": "https://nitro.co.th/",
            "cancelUrl": "https://nitro.co.th/"
        }
    }
    try:
        response = _get_api().request(options=request_options)
        return True, response
    except LinePayApiError as e:
        return False, e.api_response


def get_payment_details(transaction_id, order_id):
    try:
        return _get_api().payment_details(transaction_id=transaction_id, order_id=order_id)
    except LinePayApiError as e:
        return e.api_response


def check_payment_status(transaction_id):
    try:
        response = _get_api().check_payment_status(transaction_id=transaction_id)
        if response['returnCode'] == '0110':
            return True, response['returnMessage']
        else:
            return False, response['returnMessage']
    except LinePayApiError as e:
        return False, e.api_response


def confirm(transaction_id):
    try:
        return True, _get_api().confirm(transaction_id=transaction_id, amount=0.0, currency="THB")
    except LinePayApiError as e:
        return False, e.api_response


def void_transaction(transaction_id):
    try:
        return True, _get_api().void(transaction_id=transaction_id)
    except LinePayApiError as e:
        return False, e.api_response


def pay_preapproved(reg_key, amount, product_name, order_id, capture=True):
    try:
        return True, _get_api().pay_preapproved(reg_key=reg_key, product_name=product_name, amount=float(amount),
                                                currency="THB", order_id=str(order_id), capture=capture)
    except LinePayApiError as e:
        return False, e.api_response


def capture_payment(transaction_id, amount, currency="THB"):
    try:
        return True, _get_api().capture(transaction_id=transaction_id, amount=amount, currency=currency)
    except LinePayApiError as e:
        return False, e.api_response


def check_reg_key(reg_key):
    try:
        return _get_api().check_regkey(reg_key=reg_key)
    except LinePayApiError as e:
        return e.api_response


def expire_reg_key(reg_key):
    try:
        return _get_api().expire_regkey(reg_key=reg_key)
    except LinePayApiError as e:
        return e.api_response


if __name__ == '__main__':

    _order_id = str(uuid.uuid4())
    _product_name = "Sample product"

    ret, requested = reserve_payment(order_id=_order_id, product_id=1, product_name=_product_name)
    logger.info('===== Reserve Payment')
    # logger.info(requested)
    _transaction_id = int(requested['info']['transactionId'])

    logger.info('===== Check Status')
    # Wait for customer to confirm
    while True:
        ret, status = check_payment_status(_transaction_id)
        if status['returnCode'] == '0110':
            # logger.info("Authentication is done!")
            break
        else:
            details = get_payment_details(transaction_id=_transaction_id, order_id=_order_id)
            # logger.info(details)
            time.sleep(10)

    # Confirm amount to see if possible
    logger.info(f'===== Confirm')
    ret, confirm_info = confirm(transaction_id=_transaction_id)
    # logger.info(confirm_info)

    _reg_key = confirm_info['info']['regKey']

    # Charge actual amount
    actual_amount = 50
    logger.info(f'===== But charge {actual_amount} THB')
    pay_info = pay_preapproved(reg_key=_reg_key, product_name=_product_name, amount=actual_amount, order_id=_order_id)
    # logger.info(pay_info)

    # Finish process
    logger.info('===== Expire RegKey')
    exp_result = expire_reg_key(_reg_key)

    # Just for testing...
    logger.info('===== Status after expiration')
    reg_key_status = check_reg_key(_reg_key)
