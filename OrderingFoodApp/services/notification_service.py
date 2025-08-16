import os
from flask_mail import Message
from flask import current_app
from OrderingFoodApp import mail
from flask import render_template


class NotificationService:
    @staticmethod
    def send_email(to, subject, body, html=None):
        try:
            msg = Message(
                subject=subject,
                recipients=[to],
                body=body,
                html=html
            )
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send email: {str(e)}")
            return False

    @staticmethod
    def send_order_confirmation(owner, order):
        try:
            html = render_template(
                'emails/new_order.html',
                owner=owner,
                order=order,
                current_year=datetime.now().year
            )

            return NotificationService.send_email(
                to=owner.email,
                subject=f"Đơn hàng mới #{order.id}",
                body=f"Bạn có đơn hàng mới #{order.id} từ {order.customer.name}",
                html=html
            )
        except Exception as e:
            current_app.logger.error(f"Failed to send order confirmation: {str(e)}")
            return False