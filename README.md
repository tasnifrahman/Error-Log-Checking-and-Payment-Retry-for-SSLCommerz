# 🔄 Error Log Checking and Payment Retry for SSLCommerz 🔄

## Overview
This project implements a **Payment Retry Mechanism** for the SSLCommerz payment gateway, specifically designed to handle various payment failure scenarios and retry the payment process without requiring users to start the entire workflow from the beginning. 

The system is built using **Django** and leverages **SSLCommerz's sandbox environment** for testing, providing a seamless user experience in the event of payment failures such as:

- Invalid Credentials
- Timeout Errors
- Network Failures
- Duplicate Transaction IDs
- Currency Mismatches
- Session Expired

## Features
- **Payment Retry Logic**: Automatically retries failed payments up to a specified limit without user intervention.
- **Error Handling**: Captures and handles various error conditions from the SSLCommerz gateway.
- **Logging**: All payment attempts and errors are logged for debugging and monitoring.
- **Mock Error Scenarios**: Simulated error scenarios for testing payment retry logic.
- **Seamless User Experience**: Prevents users from having to restart the payment process from scratch.

## Tech Stack
- **Django**: Web framework used for managing views, forms, and models.
- **Python**: Backend language used to implement the logic.
- **SSLCommerz Sandbox**: Payment gateway used for testing payment processes.
- **Logging**: Custom logger for tracking payment attempts and errors.
