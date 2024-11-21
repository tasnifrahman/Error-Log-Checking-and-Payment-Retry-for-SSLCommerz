import logging
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
from sslcommerz_lib import SSLCOMMERZ
import uuid
import time
import random

# Get a custom logger for payment
logger = logging.getLogger('payment')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s %(asctime)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Mock error scenarios for testing purposes
def mock_invalid_credentials(post_body):
    return {'status': 'FAILED', 'failedreason': 'Invalid credentials'}

def mock_timeout_error(post_body):
    time.sleep(5)  # Simulate timeout
    return {'status': 'FAILED', 'failedreason': 'Timeout occurred'}

def mock_network_failure(post_body):
    raise ConnectionError("Simulated network failure")

def mock_unknown_error(post_body):
    return {'status': 'FAILED', 'failedreason': 'Unknown error from gateway'}

def mock_currency_mismatch(post_body):
    return {'status': 'FAILED', 'failedreason': 'Currency mismatch'}

def mock_invalid_amount(post_body):
    return {'status': 'FAILED', 'failedreason': 'Invalid amount'}

def mock_duplicate_transaction_id(post_body):
    return {'status': 'FAILED', 'failedreason': 'Duplicate transaction ID'}

def mock_inactive_store(post_body):
    return {'status': 'FAILED', 'failedreason': 'Inactive store'}

def mock_session_expired(post_body):
    return {'status': 'FAILED', 'failedreason': 'Session expired'}

def mock_invalid_store(post_body):
    return {'status': 'FAILED', 'failedreason': 'Invalid store ID'}

def mock_invalid_card_number(post_body):
    return {'status': 'FAILED', 'failedreason': 'Invalid card number'}

def initiate_payment(request):
    if request.method == 'POST':
        try:
            amount = request.POST.get('amount')
            transaction_id = str(uuid.uuid4())[:12]  # Generate unique transaction ID

            # SSLCOMMERZ configuration
            settings = {
                'store_id': 'abc673dc055bbd41',
                'store_pass': 'abc673dc055bbd41@ssl',
                'issandbox': True,
            }
            sslcz = SSLCOMMERZ(settings)

            # Post body for SSLCOMMERZ
            post_body = {
                'total_amount': amount,
                'currency': "BDT",
                'tran_id': transaction_id,
                'success_url': request.build_absolute_uri(reverse('payment_success')),
                'fail_url': request.build_absolute_uri(reverse('payment_fail')),
                'cancel_url': request.build_absolute_uri(reverse('payment_cancel')),
                'emi_option': 0,
                'cus_name': "Test User",
                'cus_email': "testuser@example.com",
                'cus_phone': "01700000000",
                'cus_add1': "Customer Address",
                'cus_city': "Dhaka",
                'cus_country': "Bangladesh",
                'shipping_method': "NO",
                'product_name': "Test Product",
                'product_category': "Test Category",
                'product_profile': "general",
            }

            # Retry logic for creating a session
            retry_count = 0
            max_retries = 7

            while retry_count < max_retries:
                try:
                    # Simulate error scenarios for testing
                    error_scenario = random.choice([
                        mock_invalid_credentials,
                        mock_timeout_error,
                        mock_network_failure,
                        mock_unknown_error,
                        mock_currency_mismatch,
                        mock_invalid_amount,
                        mock_duplicate_transaction_id,
                        mock_inactive_store,
                        mock_session_expired,
                        mock_invalid_store,
                        mock_invalid_card_number,
                        None  # Success case
                    ])

                    if error_scenario:
                        response = error_scenario(post_body)  # Simulate error
                    else:
                        response = sslcz.createSession(post_body)  # Real call
                        logger.info(f"SSLCommerz Response: {response}")

                    if response['status'] == 'SUCCESS':
                        logger.info(
                            f"Payment initiation successful on attempt {retry_count + 1}."
                        )
                        Payment.objects.create(
                            amount=amount,
                            transaction_id=transaction_id,
                            status='Pending',
                            session_key=response['sessionkey'],
                        )
                        return redirect(response['GatewayPageURL'])

                    else:
                        error_reason = response.get('failedreason', 'Unknown error')
                        logger.error(f"SSLCommerz & mock Error: {response['status']}, Reason: {error_reason}, Response: {response}")
                        raise RuntimeError(
                            f"Payment gateway returned failure: {error_reason}"
                        )

                except Exception as e:
                    retry_count += 1
                    logger.error(
                        f"Payment initiation failed on attempt {retry_count}: {str(e)}"
                    )
                    time.sleep(2)  # Wait before retrying

            # If retries are exhausted
            logger.error(f"Payment initiation failed after {max_retries} attempts.")
            return render(
                request,
                'testapp/payment_error.html',
                {'error_message': 'Payment initiation failed. Please try again later.', 'response': response},
            )

        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            logger.error(error_message)
            return render(
                request,
                'testapp/payment_error.html',
                {'error_message': error_message},
            )

    return render(request, 'testapp/payment_form.html')


@csrf_exempt
def payment_success(request):
    # Handle success IPN response
    tran_id = request.POST.get('tran_id')

    if not tran_id:
        return render(request, 'testapp/payment_error.html', {'error': 'Transaction ID missing'})

    try:
        payment = Payment.objects.get(transaction_id=tran_id)
        payment.status = 'Completed'
        payment.save()
        logger.info(f"Payment for transaction {tran_id} successfully completed.")
    except Payment.DoesNotExist:
        return render(request, 'testapp/payment_error.html', {'error': 'Invalid transaction ID'})
    
    except Exception as e:
        # Catch any other errors and print the message for debugging
        logger.error(f"Error processing payment success: {e}")
        return render(request, 'testapp/payment_error.html', {'error': 'An error occurred while processing the payment'})

    return render(request, 'testapp/payment_success.html', {'payment': payment})


@csrf_exempt
def payment_fail(request):
    tran_id = request.POST.get('tran_id')

    try:
        payment = Payment.objects.get(transaction_id=tran_id)
        payment.status = 'Failed'
        payment.save()
    except Payment.DoesNotExist:
        return render(request, 'testapp/payment_error.html', {'error': 'Invalid transaction ID'})

    return render(request, 'testapp/payment_fail.html', {'payment': payment})


@csrf_exempt
def payment_cancel(request):
    return render(request, 'testapp/payment_cancel.html')
